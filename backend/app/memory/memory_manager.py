from app.database.mongo_client import conversation_collection
from datetime import datetime

from datetime import datetime
from app.database.mongo_client import conversation_collection

def create_chat(session_id: str, user_id: str, pdf: bool = False, title: str = "New Chat"):
    chat = {
        "session_id": session_id,
        "user_id": user_id,
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
        create_chat(session_id, user_id="guest_fallback")
        chat = conversation_collection.find_one({"session_id": session_id})

    # TITLE:
    if role == "user" and chat.get("title") == "New Chat" and not chat.get("is_pdf", False):
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

def get_all_chats(user_id: str):
    chats = conversation_collection.find(
        {"user_id": user_id},
        {"messages": 0}
    )
    return list(chats)


def get_chat(session_id: str, user_id: str):
    return conversation_collection.find_one({
        "session_id": session_id,
        "user_id": user_id
    })


def delete_chat(session_id: str, user_id: str):
    return conversation_collection.delete_one({
        "session_id": session_id,
        "user_id": user_id
    })