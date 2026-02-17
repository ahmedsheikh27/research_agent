from app.database.mongo_client import conversation_collection
from datetime import datetime

def create_chat(session_id: str):
    conversation_collection.insert_one({
        "session_id": session_id,
        "title": "New Chat",
        "created_at": datetime.utcnow(),
        "messages": []
    })


def save_message(session_id: str, role: str, content: str):

    chat = conversation_collection.find_one({"session_id": session_id})

    if not chat:
        create_chat(session_id)
        chat = conversation_collection.find_one({"session_id": session_id})

    if role == "user" and chat["title"] == "New Chat":
        conversation_collection.update_one(
            {"session_id": session_id},
            {"$set": {"title": content[:40]}}
        )

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
