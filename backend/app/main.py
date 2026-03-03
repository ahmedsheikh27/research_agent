from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.responses import RedirectResponse
import uuid

from app.agent.research_agent import handle_query
from app.memory.memory_manager import (
    create_chat,
    get_chat,
    get_all_chats,
    delete_chat
)

app = FastAPI(title="Research Agent")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",   # Vite default
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "http://localhost:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    session_id: str
    query: str



@app.get("/")
def read_root():
    return {"message": "Hello World"}


@app.post("/chat/new")
def new_chat():
    session_id = str(uuid.uuid4())
    create_chat(session_id)
    return {"session_id": session_id}


@app.post("/chat")
def chat(request: QueryRequest):
    response = handle_query(
        session_id=request.session_id,
        query=request.query
    )
    return {"response": response}


@app.get("/chat")
def list_chats():
    chats = get_all_chats()

    for chat in chats:
        chat.pop("_id", None)

    return {"chats": chats}


@app.get("/chat/{session_id}")
def get_single_chat(session_id: str):
    chat = get_chat(session_id)

    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    chat.pop("_id", None)
    return chat


@app.delete("/chat/{session_id}")
def remove_chat(session_id: str):
    result = delete_chat(session_id)

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Chat not found")

    return {"message": "Chat deleted"}
