from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uuid
import shutil
import os
from app.agent.research_agent import handle_query
from app.rag.pdf_chunks import create_pdf_vectorstore
from app.memory.memory_manager import create_chat, get_chat, get_all_chats, delete_chat
from app.database.vector_store import load_vectorstore
import gc

app = FastAPI(title="Research Agent")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite default
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class QueryRequest(BaseModel):
    session_id: str
    query: str


PDF_TEMP_FOLDER = "temp_pdf"
os.makedirs(PDF_TEMP_FOLDER, exist_ok=True)


@app.get("/")
def read_root():
    return {"message": "Hello World"}


@app.post("/chat/new")
def new_chat():
    session_id = str(uuid.uuid4())
    create_chat(session_id, title="New Chat")
    return {"session_id": session_id,}


@app.post("/chat")
def chat(request: QueryRequest):
    response = handle_query(session_id=request.session_id, query=request.query)
    return {"response": response}


@app.get("/chat")
def list_chats():
    chats = get_all_chats()

    for chat in chats:
        chat.pop("_id", None)

    return {"chats": chats}


@app.get("/chat/{session_id}")
def get_single_chat(session_id: str):
    chat = get_chat(session_id)

    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    chat.pop("_id", None)
    return chat

@app.delete("/chat/{session_id}")
def remove_chat(session_id: str):
    result = delete_chat(session_id)

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Chat not found")

    paths_to_check = [f"faiss_indexes/{session_id}", f"faiss_indexes/pdf/{session_id}"]

   
    gc.collect()

    for path in paths_to_check:
        if os.path.exists(path):
            try:
                shutil.rmtree(path)
                print(f"Successfully deleted: {path}")
            except PermissionError:
                print(
                    f"Windows lock detected on {path}. Try manual delete if it persists."
                )
            except Exception as e:
                print(f"Error deleting {path}: {e}")

    return {"message": "Chat and files removed"}


@app.post("/chat/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    """
    Upload a PDF and create a new chat session for it.
    The chat will only use PDF chunks for RAG.
    """
    # Save PDF temporarily
    temp_file_path = os.path.join(PDF_TEMP_FOLDER, file.filename)
    with open(temp_file_path, "wb") as f:
        f.write(await file.read())

    session_id = str(uuid.uuid4())
    create_chat(session_id, pdf=True, title=file.filename)

    create_pdf_vectorstore(temp_file_path, session_id)

    os.remove(temp_file_path)

    return {"message": "PDF uploaded and processed.", "session_id": session_id}
