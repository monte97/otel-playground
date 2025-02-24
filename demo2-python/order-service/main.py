from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import Base
from crud import create_order, get_orders
import telemetry

app = FastAPI()

# Initialize DB
Base.metadata.create_all(bind=engine)

# Setup tracing
telemetry.setup_tracing(app)

# Dependency for DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/orders/")
def place_order(item_name: str, quantity: int, db: Session = Depends(get_db)):
    return create_order(db, item_name, quantity)

@app.get("/orders/")
def list_orders(db: Session = Depends(get_db)):
    return get_orders(db)
