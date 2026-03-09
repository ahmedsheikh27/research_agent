import os
from langchain_community.vectorstores import FAISS
from app.embeddings.hf_embeddings import get_embeddings

BASE_PATH = "faiss_indexes"


def load_vectorstore(session_id: str):

    embeddings = get_embeddings()
    path = f"{BASE_PATH}/{session_id}"

    if os.path.exists(path):
        return FAISS.load_local(
            path,
            embeddings,
            allow_dangerous_deserialization=True
        )

    return None


def create_vectorstore(documents, session_id: str):

    embeddings = get_embeddings()
    vectorstore = FAISS.from_documents(documents, embeddings)

    path = f"{BASE_PATH}/{session_id}"
    vectorstore.save_local(path)

    return vectorstore