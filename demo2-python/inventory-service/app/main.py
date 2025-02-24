from fastapi import FastAPI, Depends, HTTPException
from . import crud, models, database
import os

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import Resource

# Define service name
service_name = "inventory-service"

# Initialize OpenTelemetry with a named service
trace.set_tracer_provider(
    TracerProvider(resource=Resource.create({"service.name": service_name}))
)
tracer = trace.get_tracer(__name__)

# Set up OTLP exporter
otlp_exporter = OTLPSpanExporter(
    endpoint=os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317")
)
span_processor = BatchSpanProcessor(otlp_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

app = FastAPI()

FastAPIInstrumentor.instrument_app(app)

# Create a product
@app.post("/products/", response_model=models.ProductInResponse)
async def create_product(product: models.Product, db: database.get_db = Depends()):
    return await crud.create_product(db=db, product=product)

# Read a product by ID
@app.get("/products/{product_id}", response_model=models.ProductInResponse)
async def read_product(product_id: str, db: database.get_db = Depends()):
    return await crud.get_product(db=db, product_id=product_id)

# List all products
@app.get("/products/", response_model=list[models.ProductInResponse])
async def read_products(skip: int = 0, limit: int = 100, db: database.get_db = Depends()):
    return await crud.get_products(db=db, skip=skip, limit=limit)

# Update a product by ID
@app.put("/products/{product_id}", response_model=models.ProductInResponse)
async def update_product(product_id: str, product: models.Product, db: database.get_db = Depends()):
    return await crud.update_product(db=db, product_id=product_id, product=product)

# Delete a product by ID
@app.delete("/products/{product_id}", response_model=dict)
async def delete_product(product_id: str, db: database.get_db = Depends()):
    return await crud.delete_product(db=db, product_id=product_id)

# Get the quantity of a product by ID
@app.get("/products/{product_id}/quantity")
async def get_product_quantity(product_id: str, db: database.get_db = Depends()):
    return await crud.get_product_quantity(db=db, product_id=product_id)
