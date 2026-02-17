from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from app.config import MONGO_URI, DB_NAME

try:
    # Connect to MongoDB
    client = MongoClient(MONGO_URI)

    client.admin.command("ping")
    print(" MongoDB connected successfully")

    db = client[DB_NAME]

    conversation_collection = db["conversations"]

except ConnectionFailure as e:
    print("MongoDB connection failed")
    print(e)
