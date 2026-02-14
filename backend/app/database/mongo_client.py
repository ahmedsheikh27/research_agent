from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from app.config import MONGO_URI, DB_NAME

try:
    # Connect to MongoDB
    client = MongoClient(MONGO_URI)

    # Force connection check
    client.admin.command("ping")
    print(" MongoDB connected successfully")

    # Select database
    db = client[DB_NAME]

    # Create collection only if it doesn't exist
    if "conversations" not in db.list_collection_names():
        db.create_collection("conversations")
        print("'conversations' collection created")
    else:
        print("'conversations' collection already exists")

    # Reference collection
    conversation_collection = db["conversations"]

except ConnectionFailure as e:
    print("MongoDB connection failed")
    print(e)
