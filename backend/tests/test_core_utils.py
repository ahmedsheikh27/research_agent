from app.citations.citation_manager import format_citations
from app.rag.chunker import chunk_text
from app.rag.retriever import retrieve_documents


def test_format_citations_builds_numbered_lines():
    results = [{"url": "https://a.com"}, {"url": "https://b.com"}]

    formatted = format_citations(results)

    assert formatted == "[1] https://a.com\n[2] https://b.com"


def test_chunk_text_splits_long_text():
    text = "x" * 2000

    chunks = chunk_text(text)

    assert len(chunks) >= 2
    assert all(isinstance(c, str) for c in chunks)


def test_retrieve_documents_delegates_to_vectorstore():
    class DummyStore:
        def __init__(self):
            self.calls = []

        def similarity_search(self, query, k=3):
            self.calls.append((query, k))
            return ["doc-1", "doc-2"]

    store = DummyStore()
    docs = retrieve_documents(store, "test query", k=5)

    assert docs == ["doc-1", "doc-2"]
    assert store.calls == [("test query", 5)]
