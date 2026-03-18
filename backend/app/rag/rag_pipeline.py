import os
from app.search.tavily_client import search_web
from app.rag.chunker import chunk_text
from app.database.vector_store import load_vectorstore, create_vectorstore
from langchain_core.documents import Document

SIMILARITY_THRESHOLD = 0.5

def run_rag(query: str, session_id: str, k: int = 3, pdf_chat: bool = False):
    
    # PDF MODE

    if pdf_chat:

        pdf_index_path = f"faiss_indexes/pdf/{session_id}" 
        
        pdf_vectorstore = load_vectorstore(pdf_index_path) 
        
        if pdf_vectorstore is None:
            return {
                "mode": "PDF",
                "context": "Error: PDF index not found for this session.",
                "web_results": []
            }

        docs_with_scores = pdf_vectorstore.similarity_search_with_relevance_scores(query, k=k)
        
        relevant_docs = [doc for doc, score in docs_with_scores if score >= SIMILARITY_THRESHOLD]

        if not relevant_docs:
            return {
                "mode": "PDF",
                "context": "No relevant information found in the uploaded PDF.",
                "web_results": []
            }

        context = "\n\n".join([
            f"{doc.page_content}\nSource: PDF"
            for doc in relevant_docs
        ])
        return {
            "mode": "PDF",
            "context": context,
            "web_results": []
        }

    # WEB / RAG MODE

    index_path = f"faiss_indexes/{session_id}"
    vectorstore = load_vectorstore(session_id)

    if vectorstore is None:
        print("[CHAT] New chat detected. Running web search once...")
        web_results = search_web(query)
        documents = []

        for result in web_results:
            url = result.get("url", "N/A")
            content = result.get("content", "")
            if not content: continue

            chunks = chunk_text(content)
            for chunk in chunks:
                documents.append(Document(page_content=chunk, metadata={"source": url}))

        if not documents:
            return {"mode": "WEB", "context": "No information found.", "web_results": web_results}

        vectorstore = create_vectorstore(documents, session_id)
        os.makedirs("faiss_indexes", exist_ok=True)
        vectorstore.save_local(index_path)

        docs_with_scores = vectorstore.similarity_search_with_relevance_scores(query, k=k)
        context = "\n\n".join([f"{doc.page_content}\nSource: {doc.metadata.get('source','N/A')}" for doc, _ in docs_with_scores])

        return {"mode": "WEB", "context": context, "web_results": web_results}

    # EXISTING RAG
    docs_with_scores = vectorstore.similarity_search_with_relevance_scores(query, k=k)
    relevant_docs = [doc for doc, score in docs_with_scores if score >= SIMILARITY_THRESHOLD]

    if not relevant_docs:
        return {"mode": "OOC", "context": "Not in context memory. Start new chat for web search.", "web_results": []}

    context = "\n\n".join([f"{doc.page_content}\nSource: {doc.metadata.get('source','N/A')}" for doc in relevant_docs])
    return {"mode": "RAG", "context": context, "web_results": []}