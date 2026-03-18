from app.database.mongo_client import conversation_collection
from datetime import datetime

from datetime import datetime
from app.database.mongo_client import conversation_collection

def create_chat(session_id: str, pdf: bool = False, title: str = "New Chat"):
    # If it's a PDF, we use the filename passed from main.py
    # Otherwise, it stays as "New Chat" until the first message
    chat = {
        "session_id": session_id,
        "is_pdf": pdf,
        "title": title, 
        "created_at": datetime.utcnow(),
        "messages": []
    }
    conversation_collection.insert_one(chat)

def save_message(session_id: str, role: str, content: str):
    chat = conversation_collection.find_one({"session_id": session_id})

    if not chat:
        # Fallback if chat wasn't created yet
        create_chat(session_id)
        chat = conversation_collection.find_one({"session_id": session_id})

    # TITLE UPDATE LOGIC:
    # Only update if it's the user's first message AND it's NOT a PDF chat
    if role == "user" and chat.get("title") == "New Chat" and not chat.get("is_pdf", False):
        # Clean up the title (remove newlines, limit length)
        clean_title = content.split('\n')[0][:40].strip()
        conversation_collection.update_one(
            {"session_id": session_id},
            {"$set": {"title": clean_title}}
        )

    # Save the actual message
    conversation_collection.update_one(
        {"session_id": session_id},
        {
            "$push": {
                "messages": {
                    "role": role,
                    "content": content,
                    "timestamp": datetime.utcnow()
                }
            }
        }
    )

def get_chat(session_id: str):
    return conversation_collection.find_one({"session_id": session_id})


def get_all_chats():
    chats = conversation_collection.find({}, {"messages": 0})
    return list(chats)


def delete_chat(session_id: str):
    return conversation_collection.delete_one({"session_id": session_id})
