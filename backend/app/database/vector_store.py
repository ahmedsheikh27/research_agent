from langchain_community.vectorstores import FAISS
from app.config import FAISS_PATH
from app.embeddings.hf_embeddings import get_embeddings
import os

def load_or_create_vectorstore():
    embeddings = get_embeddings()

    if os.path.exists(FAISS_PATH):
        return FAISS.load_local(
            FAISS_PATH,
            embeddings,
            allow_dangerous_deserialization=True
        )
    else:
        return FAISS.from_texts([], embeddings)
