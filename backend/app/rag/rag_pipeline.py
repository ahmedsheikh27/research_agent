from app.search.tavily_client import search_web
from app.rag.chunker import chunk_text
from app.database.vector_store import load_vectorstore, create_vectorstore
from langchain_core.documents import Document

SIMILARITY_THRESHOLD = 0.5

def run_rag(query: str, session_id: str, user_id: str, k: int = 3, pdf_chat: bool = False):
    web_results = []

    # PDF MODE

    if pdf_chat:
        pdf_vectorstore = load_vectorstore(session_id, user_id, is_pdf=True)
        if pdf_vectorstore is None:
            return {
                "mode": "PDF",
                "context": "Error: PDF index not found for this session.",
                "web_results": [],
                "no_results": True
            }

        docs_with_scores = pdf_vectorstore.similarity_search_with_relevance_scores(query, k=k)
        relevant_docs = [doc for doc, score in docs_with_scores if score >= SIMILARITY_THRESHOLD]

        if not relevant_docs:
            return {
                "mode": "PDF",
                "context": "No relevant information found in the uploaded PDF for your query.",
                "web_results": [],
                "no_results": True
            }

        context = "\n\n".join([
            f"{doc.page_content}\nSource: PDF"
            for doc in relevant_docs
        ])
        return {
            "mode": "PDF",
            "context": context,
            "web_results": [],
            "no_results": False
        }

    # WEB / RAG MODE
    vectorstore = load_vectorstore(session_id, user_id)
    documents = []

    if vectorstore is None:
        print("[CHAT] New chat detected. Running web search once...")
        web_results = search_web(query)

        for result in web_results:
            url = result.get("url", "N/A")
            content = result.get("content", "")
            if not content:
                continue

            chunks = chunk_text(content)
            for chunk in chunks:
                documents.append(Document(page_content=chunk, metadata={"source": url}))

        if not documents:
            return {
                "mode": "WEB",
                "context": "No information found from web search.",
                "web_results": web_results,
                "no_results": True
            }

        vectorstore = create_vectorstore(documents, session_id, user_id)
        mode = "WEB"
    else:
        mode = "RAG"

    docs_with_scores = vectorstore.similarity_search_with_relevance_scores(query, k=k)
    relevant_docs = [doc for doc, score in docs_with_scores if score >= SIMILARITY_THRESHOLD]

    if not relevant_docs:
        return {
            "mode": mode,
            "context": "This question looks out of context for the current chat. Please start a new chat to run a fresh web search.",
            "web_results": web_results,
            "no_results": True
        }

    context = "\n\n".join([
        f"{doc.page_content}\nSource: {doc.metadata.get('source','N/A')}"
        for doc in relevant_docs
    ])
    return {"mode": mode, "context": context, "web_results": web_results, "no_results": False}