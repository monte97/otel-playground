from fastapi import FastAPI, HTTPException
from . import crud, models
from .tracing import init_tracing  # Import OpenTelemetry setup
import time

app = FastAPI()

# Initialize OpenTelemetry tracing
init_tracing(app)

# Create a product
@app.post("/products/", response_model=models.ProductInResponse)
def create_product(product: models.Product):
    return crud.create_product(product)

# Read a product by ID
@app.get("/products/{product_id}", response_model=models.ProductInResponse)
def read_product(product_id: str):
    return crud.get_product(product_id)

# List all products
@app.get("/products/", response_model=list[models.ProductInResponse])
def read_products(skip: int = 0, limit: int = 100):
    return crud.get_products(skip, limit)

# Update a product by ID
@app.put("/products/{product_id}", response_model=models.ProductInResponse)
def update_product(product_id: str, product: models.Product):
    return crud.update_product(product_id, product)

# Delete a product by ID
@app.delete("/products/{product_id}", response_model=dict)
def delete_product(product_id: str):
    return crud.delete_product(product_id)

# Get the quantity of a product by ID
@app.get("/products/{product_id}/quantity")
def get_product_quantity(product_id: str):
    return crud.get_product_quantity(product_id)
