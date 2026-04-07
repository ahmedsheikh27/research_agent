import pytest

pytest.importorskip("fastapi")
TestClient = pytest.importorskip("fastapi.testclient").TestClient


def _client_with_mocks(monkeypatch):
    from app import main

    chats = {}

    def create_chat(session_id, pdf=False, title="New Chat"):
        chats[session_id] = {"session_id": session_id, "pdf": pdf, "title": title, "messages": []}

    def get_chat(session_id):
        return chats.get(session_id)

    def get_all_chats():
        return [{"_id": "x", **v} for v in chats.values()]

    def delete_chat(session_id):
        existed = session_id in chats
        chats.pop(session_id, None)
        return type("Result", (), {"deleted_count": 1 if existed else 0})()

    monkeypatch.setattr(main, "create_chat", create_chat)
    monkeypatch.setattr(main, "get_chat", get_chat)
    monkeypatch.setattr(main, "get_all_chats", get_all_chats)
    monkeypatch.setattr(main, "delete_chat", delete_chat)
    monkeypatch.setattr(main, "handle_query", lambda session_id, query: f"{session_id}:{query}")
    monkeypatch.setattr(main, "create_pdf_vectorstore", lambda *_a, **_k: None)
    monkeypatch.setattr(main.os.path, "exists", lambda _p: False)

    return TestClient(main.app), chats


def test_root_endpoint(monkeypatch):
    client, _ = _client_with_mocks(monkeypatch)
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["message"] == "Hello World"


def test_chat_lifecycle_endpoints(monkeypatch):
    client, chats = _client_with_mocks(monkeypatch)

    new_chat_res = client.post("/chat/new")
    assert new_chat_res.status_code == 200
    session_id = new_chat_res.json()["session_id"]
    assert session_id in chats

    chat_res = client.post("/chat", json={"session_id": session_id, "query": "hello"})
    assert chat_res.status_code == 200
    assert chat_res.json()["response"] == f"{session_id}:hello"

    list_res = client.get("/chat")
    assert list_res.status_code == 200
    assert "_id" not in list_res.json()["chats"][0]

    one_res = client.get(f"/chat/{session_id}")
    assert one_res.status_code == 200
    assert one_res.json()["session_id"] == session_id

    delete_res = client.delete(f"/chat/{session_id}")
    assert delete_res.status_code == 200


def test_get_nonexistent_chat_returns_404(monkeypatch):
    client, _ = _client_with_mocks(monkeypatch)
    response = client.get("/chat/not-found")
    assert response.status_code == 404
