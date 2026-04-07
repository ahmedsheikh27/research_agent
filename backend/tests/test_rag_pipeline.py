from types import SimpleNamespace
from app.rag import rag_pipeline as rag


class DummyVectorStore:
    def __init__(self, docs_with_scores):
        self.docs_with_scores = docs_with_scores

    def similarity_search_with_relevance_scores(self, query, k=3):
        return self.docs_with_scores

    def save_local(self, _path):
        pass


def _doc(content, source="N/A"):
    return SimpleNamespace(page_content=content, metadata={"source": source})


def test_pdf_mode_missing_index(monkeypatch):
    monkeypatch.setattr(rag, "load_vectorstore", lambda _sid: None)

    result = rag.run_rag("q", "s1", pdf_chat=True)
    assert result["mode"] == "PDF"
    assert "PDF index not found" in result["context"]


def test_pdf_mode_no_relevant_docs(monkeypatch):
    store = DummyVectorStore([(_doc("x"), 0.1)])
    monkeypatch.setattr(rag, "load_vectorstore", lambda _sid: store)

    result = rag.run_rag("q", "s1", pdf_chat=True)
    assert result["mode"] == "PDF"
    assert result["no_results"] is True


def test_new_chat_uses_web_and_creates_store(monkeypatch):
    web_results = [{"url": "https://x", "content": "alpha beta gamma"}]
    monkeypatch.setattr(rag, "load_vectorstore", lambda _sid: None)
    monkeypatch.setattr(rag, "search_web", lambda _q: web_results)
    monkeypatch.setattr(rag, "chunk_text", lambda txt: [txt])

    created = {}

    def fake_create_vectorstore(documents, session_id):
        created["documents"] = documents
        created["session_id"] = session_id
        return DummyVectorStore([(documents[0], 0.9)])

    monkeypatch.setattr(rag, "create_vectorstore", fake_create_vectorstore)
    monkeypatch.setattr(rag.os, "makedirs", lambda *_a, **_k: None)

    result = rag.run_rag("my query", "s2")

    assert result["mode"] == "WEB"
    assert "alpha beta gamma" in result["context"]
    assert created["session_id"] == "s2"


def test_existing_rag_returns_ooc_when_irrelevant(monkeypatch):
    monkeypatch.setattr(rag, "load_vectorstore", lambda _sid: DummyVectorStore([(_doc("x"), 0.2)]))

    result = rag.run_rag("q", "s3")
    assert result["mode"] == "OOC"


def test_existing_rag_returns_context_when_relevant(monkeypatch):
    monkeypatch.setattr(
        rag,
        "load_vectorstore",
        lambda _sid: DummyVectorStore([(_doc("relevant content", "https://src"), 0.8)]),
    )

    result = rag.run_rag("q", "s4")
    assert result["mode"] == "RAG"
    assert "relevant content" in result["context"]
    assert "https://src" in result["context"]
