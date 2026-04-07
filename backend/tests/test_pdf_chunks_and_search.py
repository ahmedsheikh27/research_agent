import sys
import types
from types import SimpleNamespace
from app.rag import pdf_chunks
from app.search import tavily_client as tavily_client_module


def test_create_pdf_vectorstore_builds_documents(monkeypatch, tmp_path):
    class FakePage:
        def __init__(self, text):
            self._text = text

        def extract_text(self):
            return self._text

    class FakeReader:
        def __init__(self, _path):
            self.pages = [FakePage("first page"), FakePage("second page")]

    captured = {}

    class FakeStore:
        def __init__(self):
            self.saved_paths = []

        def save_local(self, path):
            self.saved_paths.append(path)

    def fake_create_vectorstore(documents, session_id):
        captured["documents"] = documents
        captured["session_id"] = session_id
        return FakeStore()

    monkeypatch.setattr(pdf_chunks, "PdfReader", FakeReader)
    monkeypatch.setattr(pdf_chunks, "chunk_text", lambda txt: [txt[:10], txt[10:]])
    monkeypatch.setattr(pdf_chunks, "create_vectorstore", fake_create_vectorstore)

    file_path = tmp_path / "a.pdf"
    file_path.write_text("placeholder")
    store = pdf_chunks.create_pdf_vectorstore(str(file_path), "session-1")

    assert captured["session_id"] == "session-1"
    assert len(captured["documents"]) == 2
    assert all(doc.metadata["source"] == "PDF" for doc in captured["documents"])
    assert store.saved_paths == ["faiss_indexes/session-1"]


def test_search_web_combines_and_sorts(monkeypatch):
    if "wikipedia" not in sys.modules:
        wiki = types.ModuleType("wikipedia")
        wiki.search = lambda *_a, **_k: []
        wiki.page = lambda *_a, **_k: SimpleNamespace(url="https://wiki/fallback")
        wiki.summary = lambda *_a, **_k: "fallback"
        sys.modules["wikipedia"] = wiki

    if "tavily" not in sys.modules:
        tavily_stub = types.ModuleType("tavily")

        class TavilyClient:
            def __init__(self, api_key=None):
                self.api_key = api_key

            def search(self, **_kwargs):
                return {"results": []}

        tavily_stub.TavilyClient = TavilyClient
        sys.modules["tavily"] = tavily_stub

    class FakeTavily:
        def search(self, **_kwargs):
            return {
                "results": [
                    {"url": "https://a", "content": "A", "score": 0.2},
                    {"url": "https://b", "content": "B", "score": 0.9},
                ]
            }

    monkeypatch.setattr(tavily_client_module, "tavily_client", FakeTavily())
    monkeypatch.setattr(tavily_client_module.wikipedia, "search", lambda _q, results=3: ["WikiTitle"])
    monkeypatch.setattr(
        tavily_client_module.wikipedia,
        "page",
        lambda _title: SimpleNamespace(url="https://wiki/title"),
    )
    monkeypatch.setattr(
        tavily_client_module.wikipedia,
        "summary",
        lambda _title, sentences=2: "wiki summary",
    )

    results = tavily_client_module.search_web("topic")

    assert len(results) == 3
    assert results[0]["score"] >= results[1]["score"] >= results[2]["score"]
    assert any(r["url"] == "https://wiki/title" for r in results)
