import pytest
import os
import shutil
import pytest
from unittest.mock import patch

from langchain_classic.schema import Document

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
# 1️⃣ RAG returns correct answer
# -----------------------------------

def test_rag_hit():
    docs = [Document(page_content="Paris is the capital of France.", metadata={"source": "local"})]
    create_vectorstore(docs)

    result = run_rag("What is the capital of France?")

    assert result["mode"] == "RAG"
    assert "Paris" in result["context"]


# -----------------------------------
# 2️⃣ RAG miss triggers WEB
# -----------------------------------

@patch("app.rag.rag_pipeline.search_web")
def test_rag_miss_triggers_web(mock_web):
    docs = [Document(page_content="Python is a programming language.", metadata={"source": "local"})]
    create_vectorstore(docs)

    mock_web.return_value = [
        {"url": "https://example.com", "content": "Berlin is the capital of Germany."}
    ]

    result = run_rag("What is the capital of Germany?")

    assert result["mode"] == "WEB"
    assert len(result["web_results"]) > 0


# -----------------------------------
# 3️⃣ Metadata (URL) stored correctly
# -----------------------------------

def test_metadata_storage():
    docs = [
        Document(
            page_content="AI was founded in 1956.",
            metadata={"source": "https://example.com"}
        )
    ]
    create_vectorstore(docs)

    result = run_rag("When was AI founded?")

    assert "https://example.com" in result["context"]


# -----------------------------------
# 4️⃣ Web fallback when vectorstore empty
# -----------------------------------

@patch("app.rag.rag_pipeline.search_web")
def test_web_fallback_when_no_vectorstore(mock_web):
    mock_web.return_value = [
        {"url": "https://news.com", "content": "Breaking news in New York."}
    ]

    result = run_rag("Latest news in New York")

    assert result["mode"] == "WEB"
    assert result["web_results"] is not None


# -----------------------------------
# 5️⃣ Web returns empty list
# -----------------------------------

@patch("app.rag.rag_pipeline.search_web")
def test_web_empty_response(mock_web):
    mock_web.return_value = []

    result = run_rag("Random question")

    assert result["mode"] == "WEB"
    assert result["context"] is not None


# -----------------------------------
# 6️⃣ Web results stored into vectorstore
# -----------------------------------

@patch("app.rag.rag_pipeline.search_web")
def test_web_results_stored(mock_web):
    mock_web.return_value = [
        {"url": "https://example.com", "content": "Tesla stock is rising."}
    ]

    run_rag("Tesla stock price")

    vectorstore = load_vectorstore()
    assert vectorstore is not None


# -----------------------------------
# 7️⃣ Vectorstore persistence works
# -----------------------------------

def test_vectorstore_persistence():
    docs = [Document(page_content="Machine learning is AI.", metadata={"source": "local"})]
    create_vectorstore(docs)

    reloaded = load_vectorstore()

    assert reloaded is not None
    results = reloaded.similarity_search("machine learning")
    assert len(results) > 0


# -----------------------------------
# 8️⃣ Similarity threshold filters irrelevant docs
# -----------------------------------

def test_similarity_filtering():
    docs = [
        Document(page_content="Machine learning is part of AI.", metadata={"source": "local"}),
        Document(page_content="Bananas are yellow fruits.", metadata={"source": "local"})
    ]
    create_vectorstore(docs)

    result = run_rag("Explain machine learning")

    assert "Machine learning" in result["context"]
    assert "Bananas" not in result["context"]


# -----------------------------------
# 9️⃣ RAG does not hallucinate when no match
# -----------------------------------

@patch("app.rag.rag_pipeline.search_web")
def test_no_relevant_docs(mock_web):
    docs = [Document(page_content="Cats are animals.", metadata={"source": "local"})]
    create_vectorstore(docs)

    mock_web.return_value = []

    result = run_rag("Quantum physics theory")

    assert result["mode"] == "WEB"


# -----------------------------------
# 🔟 Multiple documents returned
# -----------------------------------

def test_multiple_rag_results():
    docs = [
        Document(page_content="AI was founded in 1956.", metadata={"source": "a"}),
        Document(page_content="AI research expanded in 1980.", metadata={"source": "b"})
    ]
    create_vectorstore(docs)

    result = run_rag("Tell me about AI history")

    assert result["mode"] == "RAG"
    assert "1956" in result["context"]
    assert "1980" in result["context"]