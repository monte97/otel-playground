from fastapi import FastAPI, HTTPException, Query
from . import crud, models
import time
import logging
import os

app = FastAPI()

# Create a product
@app.post("/products/", response_model=models.ProductInResponse)
def create_product(product: models.Product):
    return crud.create_product(product)

# Read a product by ID
@app.get("/products/{product_id}", response_model=models.ProductInResponse)
def read_product(product_id: str):
    return crud.get_product(product_id)

# Check product availability
@app.get("/products/{product_name}/availability", response_model=models.AvailableResponse)
def check_availability(
    product_name: str,
    quantity: int = Query(..., description="Quantity to check availability for")
):
    return crud.check_availability(product_name, quantity)

# Reduce product quantity
@app.post("/products/{product_name}/reduce-quantity", response_model=models.ProductInResponse)
def reduce_quantity(
    product_name: str,
    reduce_quantity_request: models.ReduceQuantityRequest
):
    return crud.reduce_quantity(product_name, reduce_quantity_request.quantity)

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
