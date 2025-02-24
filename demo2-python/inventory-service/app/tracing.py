import os
from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
#from opentelemetry.instrumentation.motor import MotorInstrumentor
from opentelemetry.exporter.otlp.proto.grpc.exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from fastapi import FastAPI

# Function to initialize OpenTelemetry tracing
def init_otel_tracing(app: FastAPI):
    # Set up trace provider and exporter
    trace.set_tracer_provider(
        TracerProvider(
            resource=Resource.create({SERVICE_NAME: "inventory-service"})
        )
    )
    tracer_provider = trace.get_tracer_provider()

    # Set up OTLP exporter (to send traces to a trace collector)
    otlp_exporter = OTLPSpanExporter(
        endpoint=os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317")
    )

    # Set up BatchSpanProcessor
    span_processor = BatchSpanProcessor(otlp_exporter)
    tracer_provider.add_span_processor(span_processor)

    # Enable FastAPI instrumentation
    FastAPIInstrumentor.instrument_app(app)

    # Enable MongoDB instrumentation
    #MotorInstrumentor().instrument()
