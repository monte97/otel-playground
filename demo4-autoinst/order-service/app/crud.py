import logging
import os
import requests
from sqlalchemy.orm import Session
from .models import Order

# Initialize logger
logger = logging.getLogger(__name__)

# Get Inventory Service URL from environment
INVENTORY_SERVICE_URL = os.getenv("INVENTORY_SERVICE_URL", "http://inventory-service:8000")

def create_order(db: Session, item_name: str, quantity: int):
    logger.info(f"Checking inventory for item: {item_name}, quantity: {quantity}")
    
    # Check inventory availability
    try:
        response = requests.get(
            f"{INVENTORY_SERVICE_URL}/products/{item_name}/availability", 
            params={"quantity": quantity}
        )
        response.raise_for_status()
        inventory_data = response.json()
        if not inventory_data.get("available", False):
            logger.warning(f"Item {item_name} is not available in requested quantity: {quantity}")
            return {"error": "Item not available"}
    except requests.RequestException as e:
        logger.error(f"Failed to check inventory: {e}")
        return {"error": "Inventory check failed"}
    
    logger.info(f"Creating order: item_name={item_name}, quantity: {quantity}")
    order = Order(item_name=item_name, quantity=quantity)
    db.add(order)
    db.commit()
    db.refresh(order)
    logger.info(f"Order created: {order.id}")
    
    # Reduce inventory quantity
    try:
        reduce_response = requests.post(
            f"{INVENTORY_SERVICE_URL}/products/{item_name}/reduce-quantity", 
            json={"quantity": quantity}
        )
        reduce_response.raise_for_status()
        logger.info(f"Inventory updated successfully for item: {item_name}, quantity reduced by {quantity}")
    except requests.RequestException as e:
        logger.error(f"Failed to reduce inventory: {e}")
    
    return order

def get_orders(db: Session):
    logger.info("Fetching all orders")
    orders = db.query(Order).all()
    logger.info(f"Fetched {len(orders)} orders")
    return orders
