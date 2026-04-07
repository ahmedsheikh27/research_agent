import types
from app.memory import memory_manager as mm


class FakeCollection:
    def __init__(self):
        self.chat = None
        self.updated = []
        self.deleted = []

    def insert_one(self, chat):
        self.chat = chat

    def find_one(self, query):
        if self.chat and self.chat.get("session_id") == query.get("session_id"):
            return self.chat
        return None

    def update_one(self, query, update):
        self.updated.append((query, update))
        if "$set" in update and self.chat:
            self.chat.update(update["$set"])
        if "$push" in update and self.chat:
            self.chat.setdefault("messages", []).append(update["$push"]["messages"])

    def find(self, _query, _projection):
        return [self.chat] if self.chat else []

    def delete_one(self, query):
        self.deleted.append(query)
        return types.SimpleNamespace(deleted_count=1 if self.chat else 0)


def _setup_fake_collection(monkeypatch):
    fake_collection = FakeCollection()
    monkeypatch.setattr(mm, "conversation_collection", fake_collection)
    return fake_collection


def test_create_chat_and_get_chat(monkeypatch):
    fake_collection = _setup_fake_collection(monkeypatch)
    mm.create_chat("s1", pdf=True, title="doc.pdf")

    chat = mm.get_chat("s1")
    assert chat["session_id"] == "s1"
    assert chat["is_pdf"] is True
    assert chat["title"] == "doc.pdf"
    assert fake_collection.chat["messages"] == []


def test_save_message_updates_title_for_first_user_message(monkeypatch):
    _setup_fake_collection(monkeypatch)
    mm.create_chat("s2", pdf=False, title="New Chat")

    mm.save_message("s2", "user", "My first question\nline two")

    chat = mm.get_chat("s2")
    assert chat["title"] == "My first question"
    assert len(chat["messages"]) == 1
    assert chat["messages"][0]["role"] == "user"


def test_delete_chat_delegates_to_collection(monkeypatch):
    _setup_fake_collection(monkeypatch)
    mm.create_chat("s3")
    result = mm.delete_chat("s3")
    assert result.deleted_count == 1
