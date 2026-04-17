import os
from langchain_community.vectorstores import FAISS
from app.embeddings.hf_embeddings import get_embeddings

BASE_PATH = "faiss_indexes"


def get_base_path(user_id: str):
    if user_id.startswith("guest_"):
        return f"{BASE_PATH}/guests/{user_id}"
    return f"{BASE_PATH}/users/{user_id}"


def load_vectorstore(session_id: str, user_id: str, is_pdf: bool = False):
    embeddings = get_embeddings()

    base_path = get_base_path(user_id)
    subfolder = "pdf" if is_pdf else "chats"

    path = f"{base_path}/{subfolder}/{session_id}"

    if os.path.exists(path):
        return FAISS.load_local(
            path,
            embeddings,
            allow_dangerous_deserialization=True
        )

    return None


def create_vectorstore(documents, session_id: str, user_id: str, is_pdf: bool = False):
    embeddings = get_embeddings()
    vectorstore = FAISS.from_documents(documents, embeddings)

    base_path = get_base_path(user_id)
    subfolder = "pdf" if is_pdf else "chats"

    path = f"{base_path}/{subfolder}/{session_id}"

    os.makedirs(path, exist_ok=True)
    vectorstore.save_local(path)

    return vectorstore