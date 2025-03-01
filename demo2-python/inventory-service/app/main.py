from fastapi import FastAPI, HTTPException, Query
from . import crud, models
from .tracing import init_tracing  # Import OpenTelemetry setup
import time
import logging
import os

# OpenTelemetry Tracing Imports
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.pymongo import PymongoInstrumentor
from opentelemetry.sdk.resources import Resource

# OpenTelemetry Logging Imports
from opentelemetry._logs import set_logger_provider
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor

logger = logging.getLogger(__name__)

# ===========================
# Initialize OpenTelemetry Tracing
# ===========================

def init_otel_tracing(app):
    service_name = "inventory-service"

    # Set the tracer provider with a service name
    trace.set_tracer_provider(
        TracerProvider(resource=Resource.create({"service.name": service_name}))
    )
    tracer_provider = trace.get_tracer_provider()

    # Set up OTLP exporter
    otlp_exporter = OTLPSpanExporter(
        endpoint=os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317")
    )

    # Set up BatchSpanProcessor
    span_processor = BatchSpanProcessor(otlp_exporter)
    tracer_provider.add_span_processor(span_processor)

    # Instrument FastAPI
    FastAPIInstrumentor.instrument_app(app)


# ===========================
# Initialize OpenTelemetry Logging
# ===========================

def init_otel_logging():
    """Set up OpenTelemetry Logging to export logs via OTLP."""

    # Define service name in logs
    logger_provider = LoggerProvider(
        resource=Resource.create({
            "service.name": "inventory-service",
        })
    )

    # Set global LoggerProvider
    set_logger_provider(logger_provider)

    # Configure OTLP Log Exporter
    exporter = OTLPLogExporter(insecure=True)

    # Add Batch Log Processor
    logger_provider.add_log_record_processor(BatchLogRecordProcessor(exporter))

    # Create Logging Handler and Attach to Root Logger
    handler = LoggingHandler(level=logging.NOTSET, logger_provider=logger_provider)
    logging.getLogger().addHandler(handler)

    print("Logging initialized with OTLP Exporter")


# ===========================
# Initialize FastAPI Application
# ===========================

app = FastAPI()

# Initialize OpenTelemetry Tracing and Logging
init_otel_tracing(app)
init_otel_logging()

# Create a product
@app.post("/products/", response_model=models.ProductInResponse)
def create_product(product: models.Product):
    return crud.create_product(product)

# Read a product by ID
@app.get("/products/{product_id}", response_model=models.ProductInResponse)
def read_product(product_id: str):
    return crud.get_product(product_id)

@app.get("/products/{product_name}/availability", response_model=models.AvailableResponse)
def check_availability(product_name: str, quantity: int = Query(..., description="Quantity to check availability for")):
    return crud.check_availability(product_name, quantity)

@app.post("/products/{product_name}/reduce-quantity", response_model=models.ProductInResponse)
def reduce_quantity(product_name: str, reduce_quantity_request: models.ReduceQuantityRequest):
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
