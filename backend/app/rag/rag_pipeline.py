from app.search.tavily_client import search_web
from app.rag.chunker import chunk_text
from app.database.vector_store import load_vectorstore, create_vectorstore
from langchain_core.documents import Document


SIMILARITY_THRESHOLD = 0.6


def run_rag(query: str, k: int = 3):

    vectorstore = load_vectorstore()
    web_results = []
    context = ""
    mode = "RAG"

    if vectorstore:
        docs_with_scores = vectorstore.similarity_search_with_relevance_scores(query, k=k)
        relevant_docs = [doc for doc, score in docs_with_scores if score >= SIMILARITY_THRESHOLD]

        print(f"[RAG] Scores: {[round(float(s), 3) for _, s in docs_with_scores]}")

    if relevant_docs:
        # Build context with source at the end of each document
        context = "\n\n".join([
            f"{doc.page_content}\nSource: {doc.metadata.get('source', 'N/A')}"
            for doc in relevant_docs
        ])
        # Return RAG immediately if relevant docs exist, no length check
        return {"mode": "RAG", "context": context, "web_results": []}

    # Web search fallback
    print("[RAG] No relevant docs found, falling back to web search...")
    mode = "WEB"
    web_results = search_web(query)

    documents = []
    for result in web_results:
        url = result.get("url", "N/A")
        content = result.get("content", "")

        if not content:  
            continue

        chunks = chunk_text(content)  

        for chunk in chunks:
            documents.append(Document(page_content=chunk, metadata={"source": url}))

    if not documents:
        return {"mode": mode, "context": "Sorry, the question is out of context.", "web_results": web_results}

    if vectorstore is None:
        vectorstore = create_vectorstore(documents)
    else:
        vectorstore.add_documents(documents)

    vectorstore.save_local("faiss_index")  
    
    docs_with_scores = vectorstore.similarity_search_with_relevance_scores(query, k=k)
    
    relevant_docs = [doc for doc, score in docs_with_scores if score >= SIMILARITY_THRESHOLD]

    if not relevant_docs:
        context = "Sorry, the question is out of context."
    else:
        context = "\n\n".join([
            f"{doc.page_content}\nSource: {doc.metadata.get('source', 'N/A')}"
            for doc in relevant_docs
        ])

    return {"mode": mode, "context": context, "web_results": web_results}