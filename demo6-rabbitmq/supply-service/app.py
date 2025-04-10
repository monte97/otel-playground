import os
import json
import asyncio
import logging
from fastapi import FastAPI
import aio_pika
from opentelemetry.propagate import extract
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

# Set up basic logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s"
)
logger = logging.getLogger(__name__)

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost/")
# Queue name for receiving supply requests from RabbitMQ
SUPPLY_QUEUE_NAME = os.getenv("RABBITMQ_SUPPLY_REQUEST", "supply_request_queue")

app = FastAPI()

# Initialize in-memory metrics
metrics = {
    "total_requests": 0,
    "successful_requests": 0,
    "failed_requests": 0
}


@app.on_event("startup")
async def startup():
    # Connect to RabbitMQ and create a channel
    app.state.rabbit_connection = await aio_pika.connect_robust(RABBITMQ_URL)
    app.state.channel = await app.state.rabbit_connection.channel()
    await app.state.channel.set_qos(prefetch_count=1)

    # Declare the supply request queue (durable)
    supply_queue = await app.state.channel.declare_queue(SUPPLY_QUEUE_NAME, durable=True)
    # Consume messages from the supply request queue
    await supply_queue.consume(on_supply_request)

    logger.info(f"Connected and consuming from supply request queue: {SUPPLY_QUEUE_NAME}")


@app.on_event("shutdown")
async def shutdown():
    await app.state.rabbit_connection.close()
    logger.info("RabbitMQ connection closed")


async def on_supply_request(message: aio_pika.IncomingMessage):
    async with message.process():
        # Extract tracing context from headers and start a new consumer span
        ctx = extract(message.headers or {})
        with tracer.start_as_current_span("on_supply_request", context=ctx, kind=trace.SpanKind.CONSUMER) as span:
            span.set_attribute("messaging.system", "rabbitmq")
            span.set_attribute("messaging.destination", SUPPLY_QUEUE_NAME)

            metrics["total_requests"] += 1

            try:
                payload = json.loads(message.body.decode())
            except Exception as e:
                metrics["failed_requests"] += 1
                span.record_exception(e)
                span.set_attribute("error", True)
                logger.error(f"Failed to decode message: {e}")
                return

            metrics["successful_requests"] += 1
            logger.info(f"Received supply request message: {payload}")

            # Expected message format:
            # {
            #     "item_id": "string",             # Identifier of the item
            #     "current_quantity": number,      # The current quantity of the item
            #     "requested_quantity": number,    # The quantity requested/supplied
            #     "reply_to": "reply_queue_name",    # Queue to send the reply
            #     "correlation_id": "unique_id"      # ID to correlate request/response
            # }

            item_id = payload.get("item_id")
            current_quantity = payload.get("current_quantity")
            requested_quantity = payload.get("requested_quantity")
            reply_to = payload.get("reply_to")
            correlation_id = payload.get("correlation_id")

            span.set_attribute("messaging.rabbitmq.correlation_id", correlation_id)
            span.set_attribute("item.id", item_id)

            # Business logic: calculate new quantity by adding the requested amount
            new_quantity = current_quantity + requested_quantity  # sample logic

            logger.info(
                f"Processing supply request for item {item_id}: "
                f"Current: {current_quantity}, "
                f"Requested: {requested_quantity}, "
                f"New Quantity: {new_quantity}, "
                f"Correlation: {correlation_id}"
            )

            # Build the reply message payload
            response_payload = {
                "item_id": item_id,
                "new_quantity": new_quantity,
                "correlation_id": correlation_id
            }

            response_body = json.dumps(response_payload).encode()

            # Publish the reply message to the specified reply_to queue
            await app.state.channel.default_exchange.publish(
                aio_pika.Message(
                    body=response_body,
                    correlation_id=correlation_id,
                    content_type="application/json"
                ),
                routing_key=reply_to
            )
            logger.info(f"Sent reply to '{reply_to}' with correlation_id '{correlation_id}'")


@app.get("/")
async def root():
    return {"message": f"Consuming from supply request queue '{SUPPLY_QUEUE_NAME}'"}


@app.get("/metrics")
async def get_metrics():
    """
    Returns current metrics about the supply requests.
    """
    return metrics
