import logging
import time
from .models import Product
from bson import ObjectId
from fastapi import HTTPException
from .database import products_collection  # Import the PyMongo collection
from opentelemetry import trace
from opentelemetry.trace import Tracer

# Setup logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Initialize tracer
tracer = trace.get_tracer(__name__)

# Helper function to convert MongoDB _id to string
def product_helper(product) -> dict:
    return {
        "id": str(product["_id"]),
        "name": product["name"],
        "description": product["description"],
        "quantity": product["quantity"]
    }

# Get a single product by ID
def get_product(product_id: str) -> dict:
    with tracer.start_as_current_span("get_product") as span:
        query = {"_id": ObjectId(product_id)}
        span.set_attribute("db.query", str(query))
        start_time = time.time()
        logger.info(f"Querying product with ID: {product_id}")
        
        # Start tracing the database query
        product = products_collection.find_one(query)
        elapsed_time = time.time() - start_time
        
        # Add query execution time to the span attribute
        span.set_attribute("db.query_duration", elapsed_time)
        logger.info(f"Query executed in {elapsed_time:.4f} seconds with query: {query}")
        
        if product is None:
            raise HTTPException(status_code=404, detail="Product not found")
        
        return product_helper(product)

def check_availability(product_name: str, quantity: int) -> dict:
    with tracer.start_as_current_span("check_availability") as span:
        span.set_attribute("db.query.product_name", product_name)
        span.set_attribute("db.query.quantity", quantity)

        logger.info(f"Check avaiability product with name: {product_name}")
    return {"available": True}

def reduce_quantity(product_name: str, quantity: int) -> dict:
    return {}

# Get a list of all products
def get_products(skip: int = 0, limit: int = 100) -> list:
    with tracer.start_as_current_span("get_products") as span:
        query = {}
        span.set_attribute("db.query", str(query))
        start_time = time.time()
        logger.info(f"Querying all products with skip={skip} and limit={limit}")
        
        # Start tracing the database query
        products = products_collection.find(query).skip(skip).limit(limit)
        elapsed_time = time.time() - start_time
        
        # Add query execution time to the span attribute
        span.set_attribute("db.query_duration", elapsed_time)
        logger.info(f"Query executed in {elapsed_time:.4f} seconds with query: {query}")
        
        return [product_helper(product) for product in products]

# Create a new product
def create_product(product: Product) -> dict:
    with tracer.start_as_current_span("create_product") as span:
        product_dict = product.dict()
        span.set_attribute("db.query", "insert")
        start_time = time.time()
        
        # Start tracing the insert query
        result = products_collection.insert_one(product_dict)
        elapsed_time = time.time() - start_time
        span.set_attribute("db.query_duration", elapsed_time)
        
        logger.info(f"Inserted new product with ID: {result.inserted_id} in {elapsed_time:.4f} seconds")
        
        # Retrieve the newly inserted product
        new_product = products_collection.find_one({"_id": result.inserted_id})
        return product_helper(new_product)

# Update an existing product
def update_product(product_id: str, product: Product) -> dict:
    with tracer.start_as_current_span("update_product") as span:
        product_dict = product.dict(exclude_unset=True)
        query = {"_id": ObjectId(product_id)}
        span.set_attribute("db.query", str(query))
        start_time = time.time()
        logger.info(f"Updating product with ID: {product_id}")
        
        # Start tracing the update query
        result = products_collection.update_one(query, {"$set": product_dict})
        elapsed_time = time.time() - start_time
        span.set_attribute("db.query_duration", elapsed_time)
        
        logger.info(f"Update query executed in {elapsed_time:.4f} seconds with query: {query}")
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Product not found")
        
        updated_product = products_collection.find_one(query)
        return product_helper(updated_product)

# Delete a product
def delete_product(product_id: str) -> dict:
    with tracer.start_as_current_span("delete_product") as span:
        query = {"_id": ObjectId(product_id)}
        span.set_attribute("db.query", str(query))
        start_time = time.time()
        logger.info(f"Deleting product with ID: {product_id}")
        
        # Start tracing the delete query
        result = products_collection.delete_one(query)
        elapsed_time = time.time() - start_time
        span.set_attribute("db.query_duration", elapsed_time)
        
        logger.info(f"Delete query executed in {elapsed_time:.4f} seconds with query: {query}")
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Product not found")
        
        return {"message": "Product deleted successfully"}

# Get the quantity of a product by ID
def get_product_quantity(product_id: str) -> dict:
    with tracer.start_as_current_span("get_product_quantity") as span:
        query = {"_id": ObjectId(product_id)}
        projection = {"quantity": 1}
        span.set_attribute("db.query", str(query))
        start_time = time.time()
        logger.info(f"Querying quantity of product with ID: {product_id}")
        
        # Start tracing the query
        product = products_collection.find_one(query, projection)
        elapsed_time = time.time() - start_time
        span.set_attribute("db.query_duration", elapsed_time)
        
        logger.info(f"Query executed in {elapsed_time:.4f} seconds with query: {query}")
        
        if product is None:
            raise HTTPException(status_code=404, detail="Product not found")
        
        return {"quantity": product["quantity"]}
