import os
from PyPDF2 import PdfReader
from langchain_core.documents import Document
from app.rag.chunker import chunk_text
from app.database.vector_store import create_vectorstore

PDF_INDEX_FOLDER = "faiss_indexes/pdf"

def ensure_pdf_folder():
    os.makedirs(PDF_INDEX_FOLDER, exist_ok=True)

def create_pdf_vectorstore(file_path: str, session_id: str):
    ensure_pdf_folder()
    reader = PdfReader(file_path)
    full_text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            full_text += page_text + "\n"

    chunks = chunk_text(full_text)
    documents = [Document(page_content=chunk, metadata={"source": "PDF"}) for chunk in chunks]

    vectorstore = create_vectorstore(documents, session_id)
    
    save_path = f"{PDF_INDEX_FOLDER}/{session_id}"
    vectorstore.save_local(save_path)
    
    return vectorstore