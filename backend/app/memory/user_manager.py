from app.database.mongo_client import db
from datetime import datetime
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

users_collection = db["users"]

def hash_password(password: str):
    return pwd_context.hash(password[:72])

def verify_password(password: str, hashed: str):
    return pwd_context.verify(password[:72], hashed)

def create_user(email: str, password: str):
    if users_collection.find_one({"email": email}):
        return None

    user = {
        "email": email,
        "password": hash_password(password),
        "created_at": datetime.utcnow(),
        "message_count": 0
    }

    users_collection.insert_one(user)
    return user

def get_user(email: str):
    return users_collection.find_one({"email": email})

def increment_message_count(email: str):
    users_collection.update_one(
        {"email": email},
        {"$inc": {"message_count": 1}}
    )