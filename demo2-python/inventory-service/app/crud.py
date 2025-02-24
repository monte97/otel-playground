from motor.motor_asyncio import AsyncIOMotorCollection
from .models import Product
from bson import ObjectId
from fastapi import HTTPException

# Helper function to convert MongoDB _id to string
def product_helper(product) -> dict:
    return {
        "id": str(product["_id"]),
        "name": product["name"],
        "description": product["description"],
        "quantity": product["quantity"]
    }

# CRUD operations for the products collection

async def get_product(db: AsyncIOMotorCollection, product_id: str) -> dict:
    product = await db.find_one({"_id": ObjectId(product_id)})
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product_helper(product)

async def get_products(db: AsyncIOMotorCollection, skip: int = 0, limit: int = 100) -> list:
    products = await db.find().skip(skip).limit(limit).to_list(length=limit)
    return [product_helper(product) for product in products]

async def create_product(db: AsyncIOMotorCollection, product: Product) -> dict:
    product_dict = product.dict()
    result = await db.insert_one(product_dict)
    new_product = await db.find_one({"_id": result.inserted_id})
    return product_helper(new_product)

async def update_product(db: AsyncIOMotorCollection, product_id: str, product: Product) -> dict:
    product_dict = product.dict(exclude_unset=True)
    result = await db.update_one(
        {"_id": ObjectId(product_id)}, {"$set": product_dict}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Product not found")
    updated_product = await db.find_one({"_id": ObjectId(product_id)})
    return product_helper(updated_product)

async def delete_product(db: AsyncIOMotorCollection, product_id: str) -> dict:
    result = await db.delete_one({"_id": ObjectId(product_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"message": "Product deleted successfully"}

async def get_product_quantity(db: AsyncIOMotorCollection, product_id: str) -> dict:
    product = await db.find_one({"_id": ObjectId(product_id)}, {"quantity": 1})
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"quantity": product["quantity"]}
