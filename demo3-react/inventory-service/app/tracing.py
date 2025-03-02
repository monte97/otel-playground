import os
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.pymongo import PymongoInstrumentor  # Add PyMongo instrumentation
from opentelemetry.sdk.resources import Resource
from fastapi import FastAPI

def init_tracing(app: FastAPI):
    """Initialize OpenTelemetry tracing for the application."""
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

    # Instrument PyMongo
    #PymongoInstrumentor().instrument()  # Enables automatic tracing for MongoDB operations