import logging
from sqlalchemy.orm import Session
from .models import Order
from opentelemetry import trace
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor

# Initialize logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize OpenTelemetry Tracer
tracer = trace.get_tracer(__name__)

def create_order(db: Session, item_name: str, quantity: int):
    with tracer.start_as_current_span("create_order"):
        logger.info(f"Creating order: item_name={item_name}, quantity={quantity}")
        order = Order(item_name=item_name, quantity=quantity)
        db.add(order)
        db.commit()
        db.refresh(order)
        logger.info(f"Order created: {order.id}")
        return order

def get_orders(db: Session):
    with tracer.start_as_current_span("get_orders"):
        logger.info("Fetching all orders")
        orders = db.query(Order).all()
        logger.info(f"Fetched {len(orders)} orders")
        return orders
