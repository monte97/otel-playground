import logging
import time
from .models import Product
from bson import ObjectId
from fastapi import HTTPException
from .database import products_collection  # Import the PyMongo collection
from .messaging import client

logger = logging.getLogger(__name__)

# ==========================
# Helper functions
# ==========================

# Helper function to convert MongoDB _id to string
def product_helper(product) -> dict:
    return {
        "id": str(product["_id"]),
        "name": product["name"],
        "description": product["description"],
        "quantity": product["quantity"]
    }

def avaiability_helper(product, isAvaiable) -> dict:
    return {
        "available": isAvaiable
    }


# ==========================
# API HANDLERS
# ==========================

# Get a single product by ID
async def get_product(product_id: str) -> dict:
    query = {"_id": ObjectId(product_id)}
    logger.warn(f"Querying product with ID: {product_id}")
    start_time = time.time()
    
    product = products_collection.find_one(query)
    elapsed_time = time.time() - start_time
    logger.warn(f"Query executed in {elapsed_time:.4f} seconds with query: {query}")
    
    if product is None:
        logger.error(f"Product {product_id} not found")
        raise HTTPException(status_code=404, detail="Product not found")
    
    logger.warn(f"Increment search for {product['name']}")
    return product_helper(product)

async def check_availability(product_name: str, quantity: int) -> dict:
    logger.warn(f"Checking availability for product with name: {product_name}")
    
    query = {"name": product_name}
    product = products_collection.find_one(query)
    if product is not None:
        if product["quantity"] >= quantity:
            return avaiability_helper(product, True)
        else:
            await client.send_request(product["name"], product["quantity"], quantity)
            return avaiability_helper(product, False)
    else:
        raise HTTPException(status_code=404, detail="Product not found")

async def reduce_quantity(product_name: str, quantity: int) -> dict:
    logger.warn(f"Reducing quantity for product with name: {product_name}")
    
    # Ensure quantity to reduce is a positive integer
    if quantity <= 0:
        raise HTTPException(status_code=400, detail="Quantity must be a positive integer")

    # Find the product by name
    product = products_collection.find_one({"name": product_name})
    logger.warn(f"Product found: {product}")

    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    # Ensure the product has enough quantity to reduce
    if product["quantity"] < quantity:
        raise HTTPException(status_code=400, detail="Not enough stock to reduce")

    # Reduce the quantity by the given amount
    updated_product = products_collection.find_one_and_update(
        {"name": product_name},  # Find the product by name
        {"$inc": {"quantity": -quantity}},  # Reduce the quantity by the specified amount
        return_document=True  # Return the updated document
    )
    logger.warn(f"Product updated: {updated_product}")

    return product_helper(updated_product)


async def increase_quantity(product_name: str, quantity: int) -> dict:
    logger.warn(f"Increase quantity for product with name: {product_name}")
    
    # Ensure quantity to reduce is a positive integer
    if quantity <= 0:
        raise HTTPException(status_code=400, detail="Quantity must be a positive integer")

    # Find the product by name
    product = products_collection.find_one({"name": product_name})
    logger.warn(f"Product found: {product}")

    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    # Reduce the quantity by the given amount
    updated_product = products_collection.find_one_and_update(
        {"name": product_name},  # Find the product by name
        {"$inc": {"quantity": quantity}},  # Reduce the quantity by the specified amount
        return_document=True  # Return the updated document
    )
    logger.warn(f"Product updated: {updated_product}")

    return product_helper(updated_product)

# Get a list of all products
async def get_products(skip: int = 0, limit: int = 100) -> list:
    query = {}
    logger.debug("Hola debug")
    logger.info(f"Querying all products with skip={skip} and limit={limit}")
    start_time = time.time()
    
    products = products_collection.find(query).skip(skip).limit(limit)
    elapsed_time = time.time() - start_time
    logger.warn(f"Query executed in {elapsed_time:.4f} seconds with query: {query}")
    logger.error("try out errors too")
    
    return [product_helper(product) for product in products]

# Create a new product
async def create_product(product: Product) -> dict:
    product_dict = product.dict()
    logger.warn("Inserting new product")
    start_time = time.time()
    
    result = products_collection.insert_one(product_dict)
    elapsed_time = time.time() - start_time
    logger.warn(f"Inserted new product with ID: {result.inserted_id} in {elapsed_time:.4f} seconds")
    
    new_product = products_collection.find_one({"_id": result.inserted_id})
    return product_helper(new_product)

# Update an existing product
async def update_product(product_id: str, product: Product) -> dict:
    product_dict = product.dict(exclude_unset=True)
    query = {"_id": ObjectId(product_id)}
    logger.warn(f"Updating product with ID: {product_id}")
    start_time = time.time()
    
    result = products_collection.update_one(query, {"$set": product_dict})
    elapsed_time = time.time() - start_time
    logger.warn(f"Update query executed in {elapsed_time:.4f} seconds with query: {query}")
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Product not found")
    
    updated_product = products_collection.find_one(query)
    return product_helper(updated_product)

# Delete a product
async def delete_product(product_id: str) -> dict:
    query = {"_id": ObjectId(product_id)}
    logger.warn(f"Deleting product with ID: {product_id}")
    start_time = time.time()
    
    result = products_collection.delete_one(query)
    elapsed_time = time.time() - start_time
    logger.warn(f"Delete query executed in {elapsed_time:.4f} seconds with query: {query}")
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return {"message": "Product deleted successfully"}

# Get the quantity of a product by ID
async def get_product_quantity(product_id: str) -> dict:
    query = {"_id": ObjectId(product_id)}
    projection = {"quantity": 1}
    logger.warn(f"Querying quantity of product with ID: {product_id}")
    start_time = time.time()
    
    product = products_collection.find_one(query, projection)
    elapsed_time = time.time() - start_time
    logger.warn(f"Query executed in {elapsed_time:.4f} seconds with query: {query}")
    
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return {"quantity": product["quantity"]}
