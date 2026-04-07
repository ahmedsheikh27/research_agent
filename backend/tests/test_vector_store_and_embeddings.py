def test_get_embeddings_constructs_expected_model(monkeypatch):
    from app.embeddings import hf_embeddings
    emb_module = hf_embeddings

    captured = {}

    class FakeEmbeddings:
        def __init__(self, model, google_api_key):
            captured["model"] = model
            captured["google_api_key"] = google_api_key

    monkeypatch.setattr(emb_module, "GoogleGenerativeAIEmbeddings", FakeEmbeddings)

    emb_module.get_embeddings()

    assert captured["model"] == "gemini-embedding-001"
    assert "google_api_key" in captured


def test_load_vectorstore_returns_none_when_path_missing(monkeypatch):
    from app.database import vector_store
    vs_module = vector_store

    monkeypatch.setattr(vs_module.os.path, "exists", lambda _p: False)
    loaded = vs_module.load_vectorstore("session-1")
    assert loaded is None


def test_load_vectorstore_calls_faiss(monkeypatch):
    from app.database import vector_store
    vs_module = vector_store

    called = {}

    class FakeFaiss:
        @staticmethod
        def load_local(path, embeddings, allow_dangerous_deserialization):
            called["path"] = path
            called["embeddings"] = embeddings
            called["allow"] = allow_dangerous_deserialization
            return "loaded"

    monkeypatch.setattr(vs_module.os.path, "exists", lambda _p: True)
    monkeypatch.setattr(vs_module, "FAISS", FakeFaiss)
    monkeypatch.setattr(vs_module, "get_embeddings", lambda: "emb")

    loaded = vs_module.load_vectorstore("abc")

    assert loaded == "loaded"
    assert called["path"] == "faiss_indexes/abc"
    assert called["embeddings"] == "emb"
    assert called["allow"] is True


def test_create_vectorstore_saves_local(monkeypatch):
    from app.database import vector_store
    vs_module = vector_store

    class FakeStore:
        def __init__(self):
            self.saved_path = None

        def save_local(self, path):
            self.saved_path = path

    class FakeFaiss:
        @staticmethod
        def from_documents(documents, embeddings):
            assert documents == ["d1"]
            assert embeddings == "emb"
            return FakeStore()

    monkeypatch.setattr(vs_module, "FAISS", FakeFaiss)
    monkeypatch.setattr(vs_module, "get_embeddings", lambda: "emb")

    store = vs_module.create_vectorstore(["d1"], "s1")
    assert store.saved_path == "faiss_indexes/s1"
