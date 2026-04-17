from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
import uuid

from app.database.mongo_client import user_collection
from app.auth.auth import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["Auth"])


# Schemas
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# 📝 Register
@router.post("/register")
def register(data: RegisterRequest):
    existing_user = user_collection.find_one({"email": data.email})

    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    user_id = str(uuid.uuid4())

    user_collection.insert_one({
        "user_id": user_id,
        "email": data.email,
        "password_hash": hash_password(data.password)
    })

    token = create_access_token({"user_id": user_id})

    return {
        "message": "User registered successfully",
        "token": token
    }


# 🔐 Login
@router.post("/login")
def login(data: LoginRequest):
    user = user_collection.find_one({"email": data.email})

    if not user or not verify_password(data.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token({"user_id": user["user_id"]})

    return {
        "message": "Login successful",
        "token": token
    }


# 👻 Guest
@router.post("/guest")
def create_guest():
    guest_id = "guest_" + str(uuid.uuid4())

    token = create_access_token({"user_id": guest_id})

    return {
        "message": "Guest session created",
        "token": token
    }