import os
from pymongo import MongoClient
from opentelemetry.instrumentation.pymongo import PymongoInstrumentor
from opentelemetry import trace
from opentelemetry.trace import SpanKind
from dotenv import load_dotenv
from opentelemetry.context import attach
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, SimpleSpanProcessor

# Load environment variables
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/inventorydb")

# Initialize tracer
trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)

# Enable OpenTelemetry instrumentation for PyMongo BEFORE opening the connection
#PymongoInstrumentor().instrument()

# Initialize PyMongo
client = MongoClient(MONGO_URI)
db = client["inventorydb"]
products_collection = db["products"]
