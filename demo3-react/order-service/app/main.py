from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from .database import SessionLocal, engine
from .models import Base
from .crud import create_order, get_orders
import logging
import os
import time

# OpenTelemetry Tracing Imports
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
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

service_name = "order-service"

def init_otel_tracing(app):

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
            "service.name": service_name,
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

# Initialize DB
Base.metadata.create_all(bind=engine)

# Setup tracing
#telemetry.setup_tracing(app)

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
