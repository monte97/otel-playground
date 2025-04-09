import os
import json
import uuid
import asyncio
import logging
import aio_pika
from . import crud

logger = logging.getLogger(__name__)

# Configuration from environment
RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost/")
SUPPLY_QUEUE_NAME = os.getenv("RABBITMQ_SUPPLY_REQUEST", "supply_request_queue")
REPLY_QUEUE_NAME = os.getenv("RABBITMQ_SUPPLY_RESPONSE", "serviceA.reply")


class RabbitMQClient:
    def __init__(self):
        self.connection: aio_pika.RobustConnection | None = None
        self.channel: aio_pika.Channel | None = None
        self.reply_queue: aio_pika.Queue | None = None
        self.pending_requests: dict[str, asyncio.Future] = {}

    async def connect(self):
        """Establish connection, create channel and set up reply consumer."""
        self.connection = await aio_pika.connect_robust(RABBITMQ_URL)
        self.channel = await self.connection.channel()
        await self.channel.set_qos(prefetch_count=1)
        # Declare reply queue (non-durable is usually fine for reply queues)
        self.reply_queue = await self.channel.declare_queue(REPLY_QUEUE_NAME, durable=False)
        await self.reply_queue.consume(self.on_response)
        logger.info(f"Connected to RabbitMQ; consuming responses on queue: {REPLY_QUEUE_NAME}")

    async def close(self):
        if self.connection:
            await self.connection.close()
            logger.info("RabbitMQ connection closed")
    
    async def on_response(self, message: aio_pika.IncomingMessage):
        """
        Consume and log incoming messages on the reply queue.
        """
        async with message.process():
            try:
                payload = json.loads(message.body.decode())
                logger.info(f"Received message on reply queue: {payload}")
                await crud.increase_quantity(payload["item_id"], payload["new_quantity"])
            except Exception as e:
                logger.error(f"Failed to decode message: {e}")

    # async def on_response(self, message: aio_pika.IncomingMessage):
    #     async with message.process():
    #         correlation_id = message.correlation_id
    #         logger.info(f"Processing message with correlation_id '{correlation_id}'")
    #         try:
    #             payload = json.loads(message.body.decode())
    #         except Exception as e:
    #             logger.error(f"Failed to decode response message: {e}")
    #             return

    #         logger.info(f"Received reply for correlation_id '{correlation_id}': {payload}")
    #         future = self.pending_requests.pop(correlation_id, None)
    #         if future:
    #             future.set_result(payload)
    #         else:
    #             logger.warning(f"No pending request for correlation_id '{correlation_id}'")

    async def send_request(self, item_id: str, current_quantity: int, requested_quantity: int) -> None:
        """
        Send a supply request message with a correlation_id for traceability.
        No reply will be awaited or handled.
        """
        if not self.channel:
            raise Exception("RabbitMQ channel is not initialized.")

        correlation_id = str(uuid.uuid4())
        request_payload = {
            "item_id": item_id,
            "current_quantity": current_quantity,
            "requested_quantity": requested_quantity,
            "reply_to": REPLY_QUEUE_NAME,
            "correlation_id": correlation_id
        }
        message_body = json.dumps(request_payload).encode()

        logger.info(f"Sending supply request for item_id '{item_id}' with correlation_id '{correlation_id}'")

        await self.channel.default_exchange.publish(
            aio_pika.Message(
                body=message_body,
                correlation_id=correlation_id,
                content_type="application/json"
            ),
            routing_key=SUPPLY_QUEUE_NAME
    )




# Global RabbitMQ client instance, to be initialized at service startup.
client = RabbitMQClient()
