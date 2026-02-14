from app.search.tavily_client import search_web
from app.rag.chunker import chunk_text
from app.rag.retriever import retrieve_documents
from app.database.vector_store import load_or_create_vectorstore

def run_rag(query: str):
    vectorstore = load_or_create_vectorstore()

    # Step 1: search web
    web_results = search_web(query)

    all_text = ""
    for result in web_results:
        all_text += result.get("content", "") + "\n"

    # Step 2: chunk
    chunks = chunk_text(all_text)

    # Step 3: add to vectorstore
    if chunks:
        vectorstore.add_texts(chunks)
        vectorstore.save_local("faiss_index")

    # Step 4: retrieve relevant docs
    docs = retrieve_documents(vectorstore, query)

    context = "\n".join([doc.page_content for doc in docs])

    return context, web_results
