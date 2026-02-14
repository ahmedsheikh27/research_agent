def retrieve_documents(vectorstore, query: str, k: int = 4):
    return vectorstore.similarity_search(query, k=k)
