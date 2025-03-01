from pydantic import BaseModel
from typing import Optional

# Product model for the database
class Product(BaseModel):
    name: str
    description: str
    quantity: int

    class Config:
        # MongoDB doesn't use an ORM, but we use Pydantic to validate data
        orm_mode = True

# Product response model (with ID field)
class ProductInResponse(Product):
    id: str

class AvailableResponse(BaseModel):
    available: bool