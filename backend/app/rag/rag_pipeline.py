from app.search.tavily_client import search_web
from app.rag.chunker import chunk_text
from app.database.vector_store import load_vectorstore, create_vectorstore
from langchain_core.documents import Document
import os

SIMILARITY_THRESHOLD = 0.5


def run_rag(query: str, session_id: str, k: int = 3):
    """
    RAG pipeline:
    - First message in a chat → web search + store in vector DB
    - Subsequent messages → RAG search in vector DB
    - If nothing matches → respond with out-of-context message
    """

    index_path = f"faiss_indexes/{session_id}"

    # Load vectorstore for this chat
    vectorstore = load_vectorstore(session_id)

    #  WEB SEARCH
   
    if vectorstore is None:
        print("[CHAT] New chat detected. Running web search once...")

        web_results = search_web(query)
        documents = []

        for result in web_results:
            url = result.get("url", "N/A")
            content = result.get("content", "")
            if not content:
                continue

            chunks = chunk_text(content)
            for chunk in chunks:
                documents.append(
                    Document(
                        page_content=chunk,
                        metadata={"source": url}
                    )
                )

        if not documents:
            return {
                "mode": "WEB",
                "context": "Sorry, no information found.",
                "web_results": web_results
            }

        # Create vectorstore for this chat
        vectorstore = create_vectorstore(documents, session_id)
        os.makedirs("faiss_indexes", exist_ok=True)
        vectorstore.save_local(index_path)

        # Retrieve best chunks for context 
        docs_with_scores = vectorstore.similarity_search_with_relevance_scores(query, k=k)
        context_docs = [doc for doc, _ in docs_with_scores]

        context = "\n\n".join([
            f"{doc.page_content}\nSource: {doc.metadata.get('source','N/A')}"
            for doc in context_docs
        ])

        return {
            "mode": "WEB",
            "context": context,
            "web_results": web_results
        }

    # -----------------------------
    # EXISTING CHAT → RAG ONLY
    # -----------------------------
    docs_with_scores = vectorstore.similarity_search_with_relevance_scores(query, k=k)
    print(f"[RAG] Scores: {[round(float(s),3) for _, s in docs_with_scores]}")

    relevant_docs = [doc for doc, score in docs_with_scores if score >= SIMILARITY_THRESHOLD]

    if not relevant_docs:
        # No relevant chunks found → do not re-run web search
        return {
            "mode": "OOC",
            "context": "This is not in my context memory, please make search in a new chat.",
            "web_results": []
        }

    context = "\n\n".join([
        f"{doc.page_content}\nSource: {doc.metadata.get('source','N/A')}"
        for doc in relevant_docs
    ])

    return {
        "mode": "RAG",
        "context": context,
        "web_results": []
    }