from langchain_google_genai import ChatGoogleGenerativeAI
from app.config import GOOGLE_API_KEY
from app.rag.rag_pipeline import run_rag
from app.memory.memory_manager import save_message
from app.citations.citation_manager import format_citations

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=GOOGLE_API_KEY,
    temperature=0.3
)

def handle_query(session_id: str, query: str):

    # Save user message
    save_message(session_id, "user", query)

    # Run RAG
    context, sources = run_rag(query)

    prompt = f"""
You are a research assistant.

Use the context below to answer clearly and professionally.

Context:
{context}

Question:
{query}
"""

    response = llm.invoke(prompt)

    citations = format_citations(sources)

    final_answer = f"{response.content}\n\nSources:\n{citations}"

    # Save AI response
    save_message(session_id, "assistant", final_answer)

    return final_answer
