import logging
import time
from .models import Product
from bson import ObjectId
from fastapi import HTTPException
from .database import products_collection  # Import the PyMongo collection
from opentelemetry import trace
from opentelemetry.trace import Tracer
from opentelemetry.metrics import (
    get_meter_provider,
)

# ==========================
# Initialize logging
# ==========================

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# ==========================
# Initialize tracer
# ==========================

tracer = trace.get_tracer(__name__)


# ==========================
# Initialize Metrics
# ==========================

meter = get_meter_provider().get_meter("custom-metrics", "1.0.0")

# Get OpenTelemetry meter
request_counter = meter.create_counter(
    "crud_request_counter",
    description="Total number of request"
    )

# Define a counter for tracking searches
search_counter = meter.create_counter(
    "crud_search_counter", 
    description="Total number of searches processed",
)

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

def avaiability_helper(product, requested_quantity) -> dict:
    return {
        "available": product["quantity"] >= requested_quantity
    }


# ==========================
# API HANDLERS
# ==========================

# Get a single product by ID
def get_product(product_id: str) -> dict:
    with tracer.start_as_current_span("get_product") as span:
        request_counter.add(1)  # Increment counter on request
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
            #search_counter.add(1)
            logger.error(f"Product {product_id} not found")
            raise HTTPException(status_code=404, detail="Product not found")
        
        search_counter.add(1, {"product_name": product["name"]})
        logger.info(f"increment search of {product["name"]}")
        return product_helper(product)

def check_availability(product_name: str, quantity: int) -> dict:
    with tracer.start_as_current_span("check_availability") as span:
        request_counter.add(1)  # Increment counter on request
        span.set_attribute("db.query.product_name", product_name)
        span.set_attribute("db.query.quantity", quantity)
        logger.info(f"Check avaiability product with name: {product_name}")
        
        query = {"name": product_name}
        product = products_collection.find_one(query)
        if product is not None:
            search_counter.add(1, {"product_name": product["name"]})
            return avaiability_helper(product, quantity)
        else:
            raise HTTPException(status_code=404, detail="Product not found")

def reduce_quantity(product_name: str, quantity: int) -> dict:
    with tracer.start_as_current_span("reduce_quantity") as span:
        request_counter.add(1)  # Increment counter on request
        span.set_attribute("db.query.product_name", product_name)
        span.set_attribute("db.query.quantity", quantity)
        # Ensure quantity to reduce is a positive integer
        if quantity <= 0:
            raise HTTPException(status_code=400, detail="Quantity must be a positive integer")

        # Find the product by name
        product = products_collection.find_one({"name": product_name})
        logger.info(f"product found {product}")

        if product is None:
            raise HTTPException(status_code=404, detail="Product not found")

        #search_counter.add(1)

        # Ensure the product has enough quantity to reduce
        if product["quantity"] < quantity:
            raise HTTPException(status_code=400, detail="Not enough stock to reduce")

        # Reduce the quantity by the given amount
        updated_product = products_collection.find_one_and_update(
            {"name": product_name},  # Find the product by name
            {"$inc": {"quantity": -quantity}},  # Reduce the quantity by the specified amount
            return_document=True  # Return the updated document
        )
        logger.info(f"product update {updated_product}")

        return product_helper(updated_product)


# Get a list of all products
def get_products(skip: int = 0, limit: int = 100) -> list:
    with tracer.start_as_current_span("get_products") as span:
        request_counter.add(1)  # Increment counter on request
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
        request_counter.add(1)  # Increment counter on request
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
        request_counter.add(1)  # Increment counter on request
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
        request_counter.add(1)  # Increment counter on request
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
        request_counter.add(1)  # Increment counter on request
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
        #search_counter.add(1)

        
        return {"quantity": product["quantity"]}
