from app.search.tavily_client import search_web
from app.rag.chunker import chunk_text
from app.rag.retriever import retrieve_documents
from app.database.vector_store import load_vectorstore, create_vectorstore


def run_rag(query: str):

    vectorstore = load_vectorstore()

    web_results = search_web(query)

    all_text = ""
    for result in web_results:
        all_text += result.get("content", "") + "\n"

    chunks = chunk_text(all_text)

    if vectorstore is None and chunks:
        vectorstore = create_vectorstore(chunks)

    elif vectorstore and chunks:
        vectorstore.add_texts(chunks)
        vectorstore.save_local("faiss_index")

    context = ""
    if vectorstore:
        docs = retrieve_documents(vectorstore, query)
        context = "\n".join([doc.page_content for doc in docs])

    return context, web_results
