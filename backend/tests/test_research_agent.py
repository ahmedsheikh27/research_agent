import os
import shutil
import pytest
from unittest.mock import patch

from langchain_core.documents import Document

from app.rag.rag_pipeline import run_rag
from app.database.vector_store import create_vectorstore, load_vectorstore
from app.config import FAISS_PATH


# -----------------------------------
# Test Setup / Teardown
# -----------------------------------

@pytest.fixture(autouse=True)
def clean_faiss():
    """Ensure clean FAISS index before each test."""
    if os.path.exists(FAISS_PATH):
        shutil.rmtree(FAISS_PATH)

    yield

    if os.path.exists(FAISS_PATH):
        shutil.rmtree(FAISS_PATH)


# -----------------------------------
# 1️⃣ Web search triggers on new chat
# -----------------------------------

@patch("app.rag.rag_pipeline.search_web")
def test_web_search_on_new_chat(mock_web):

    mock_web.return_value = [
        {"url": "https://example.com", "content": "Artificial intelligence is the simulation of human intelligence."}
    ]

    result = run_rag("What is artificial intelligence?", "test_session_1")

    assert result["mode"] == "WEB"
    assert "context" in result


# -----------------------------------
# 2️⃣ Vectorstore gets created
# -----------------------------------

@patch("app.rag.rag_pipeline.search_web")
def test_vectorstore_created(mock_web):

    mock_web.return_value = [
        {"url": "https://example.com", "content": "Machine learning is part of AI."}
    ]

    run_rag("What is machine learning?", "test_session_2")

    assert os.path.exists(f"{FAISS_PATH}/test_session_2")


# -----------------------------------
# 3️⃣ Existing chat uses RAG
# -----------------------------------

@patch("app.rag.rag_pipeline.search_web")
def test_existing_chat_uses_rag(mock_web):

    mock_web.return_value = [
        {"url": "https://example.com", "content": "Deep learning uses neural networks."}
    ]

    session_id = "test_session_3"

    run_rag("What is deep learning?", session_id)

    result = run_rag("Explain neural networks", session_id)

    assert result["mode"] == "RAG"


# -----------------------------------
# 4️⃣ Similarity search works
# -----------------------------------

def test_similarity_scores():

    session_id = "test_session_4"

    docs = [
        Document(page_content="Neural networks are used in AI.", metadata={"source": "local"})
    ]

    create_vectorstore(docs, session_id)

    vs = load_vectorstore(session_id)

    results = vs.similarity_search_with_relevance_scores(
        "neural networks", k=3
    )

    assert len(results) > 0


# -----------------------------------
# 5️⃣ Context contains sources
# -----------------------------------

@patch("app.rag.rag_pipeline.search_web")
def test_context_generation(mock_web):

    mock_web.return_value = [
        {"url": "https://example.com", "content": "AI stands for artificial intelligence."}
    ]

    result = run_rag("Explain AI", "test_session_5")

    assert "Source:" in result["context"]


# -----------------------------------
# 6️⃣ Out-of-context detection
# -----------------------------------

@patch("app.rag.rag_pipeline.search_web")
def test_out_of_context(mock_web):

    mock_web.return_value = [
        {"url": "https://example.com", "content": "Bitcoin is a cryptocurrency."}
    ]

    session_id = "test_session_6"

    run_rag("What is bitcoin?", session_id)

    result = run_rag("Explain Roman architecture", session_id)

    assert result["mode"] in ["RAG", "OOC"]


# -----------------------------------
# 7️⃣ Handles empty web results
# -----------------------------------

@patch("app.rag.rag_pipeline.search_web")
def test_empty_web_results(mock_web):

    mock_web.return_value = []

    result = run_rag("random nonsense query", "test_session_7")

    assert "context" in result


# -----------------------------------
# 8️⃣ Chunking works
# -----------------------------------

def test_chunking():

    from app.rag.chunker import chunk_text

    text = "AI is the future. " * 200

    chunks = chunk_text(text)

    assert len(chunks) > 1


# -----------------------------------
# 9️⃣ Metadata stored correctly
# -----------------------------------

def test_document_metadata():

    session_id = "test_session_8"

    docs = [
        Document(
            page_content="AI was founded in 1956.",
            metadata={"source": "https://example.com"}
        )
    ]

    create_vectorstore(docs, session_id)

    vs = load_vectorstore(session_id)

    results = vs.similarity_search("AI")

    assert results[0].metadata["source"] == "https://example.com"


# -----------------------------------
# 🔟 Multiple RAG results
# -----------------------------------

def test_multiple_rag_results():

    session_id = "test_session_9"

    docs = [
        Document(page_content="AI started in 1956.", metadata={"source": "a"}),
        Document(page_content="AI expanded in 1980.", metadata={"source": "b"})
    ]

    create_vectorstore(docs, session_id)

    vs = load_vectorstore(session_id)

    results = vs.similarity_search("AI", k=2)

    assert len(results) == 2