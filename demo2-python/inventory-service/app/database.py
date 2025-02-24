import motor.motor_asyncio
import os
from dotenv import load_dotenv

load_dotenv()

# Load environment variables
MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongo:27017/inventorydb")

# Create a MongoDB client
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
database = client.get_database()

# Get the products collection
products_collection = database.get_collection("products")

# Dependency to access the database
async def get_db():
    return products_collection
