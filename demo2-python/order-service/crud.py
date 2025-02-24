from sqlalchemy.orm import Session
from models import Order

def create_order(db: Session, item_name: str, quantity: int):
    order = Order(item_name=item_name, quantity=quantity)
    db.add(order)
    db.commit()
    db.refresh(order)
    return order

def get_orders(db: Session):
    return db.query(Order).all()
