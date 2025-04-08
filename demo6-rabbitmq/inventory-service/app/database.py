import os
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/inventorydb")

# Initialize PyMongo
client = MongoClient(MONGO_URI)
db = client["inventorydb"]
products_collection = db["products"]
