from langchain_google_genai import ChatGoogleGenerativeAI
from app.config import GOOGLE_API_KEY
from app.rag.rag_pipeline import run_rag
from app.memory.memory_manager import save_message
from app.citations.citation_manager import format_citations
from app.memory.memory_manager import get_chat

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash", google_api_key=GOOGLE_API_KEY, temperature=0.3
)




def build_conversation_history(session_id: str):
    chat = get_chat(session_id)
    if not chat:
        return ""

    messages = chat["messages"]
    history = ""

    for msg in messages:
        history += f"{msg['role']}: {msg['content']}\n"

    return history


def is_conversation_question(query: str):
    keywords = [
        "earlier",
        "before",
        "start of chat",
        "discuss",
        "search first",
        "conversation",
    ]
    return any(k in query.lower() for k in keywords)


def handle_query(session_id: str, query: str):

    chat_history = build_conversation_history(session_id)

    if is_conversation_question(query):
        prompt = f"""
Conversation History:
{chat_history}

User Question:
{query}

Answer clearly based only on conversation history.
Do not use web context.
"""
        response = llm.invoke(prompt)

        save_message(session_id, "assistant", response.content)
        return response.content
    context, sources = run_rag(query)

    prompt = f"""
Conversation History:
{chat_history}

Research Context:
{context}

Question:
{query}

Return response in strict JSON format:
{{
  "answer": "...",
  "confidence": float,
  "unsupported_claims": true/false,
  "reasoning": "..."
}}
"""

    response = llm.invoke(prompt)

    citations = format_citations(sources)

    final_answer = f"{response.content}\n\nSources:\n{citations}"

    save_message(session_id, "assistant", final_answer)

    return final_answer
