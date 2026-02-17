from langchain_google_genai import ChatGoogleGenerativeAI
from app.config import GOOGLE_API_KEY
from app.rag.rag_pipeline import run_rag
from app.memory.memory_manager import save_message, get_chat
from app.citations.citation_manager import format_citations

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash", google_api_key=GOOGLE_API_KEY, temperature=0.3
)


def build_conversation_history(session_id: str):
    chat = get_chat(session_id)
    if not chat:
        return ""

    history = ""
    for msg in chat["messages"]:
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
    """
    Handles a user query with RAG / Web context.
    source_mode:
        - "rag": Only RAG context → confidence 1.0
        - "rag_web": RAG + Web Search → confidence 0.5
        - "web": Only Web Search → confidence 0.3
    """

    save_message(session_id, "user", query)

    chat_history = build_conversation_history(session_id)

    if is_conversation_question(query):
        prompt = f"""
Conversation History:
{chat_history}

User Question:
{query}

Answer clearly based ONLY on conversation history.
Do NOT use RAG or web context.
"""
        response = llm.invoke(prompt)
        save_message(session_id, "assistant", response.content)
        return response.content

    context, sources = run_rag(query)

    citations = format_citations(sources)

    prompt = f"""
Conversation History:
{chat_history}

Research Context:
{context}

User Question:
{query}

Instructions:

- Answer using ONLY the Research Context provided above.
- Format the response as a **numbered ordered list**.
- Each sentence in a point must be on a **new line**.
- Provide **complete information**. Do not truncate or shorten; if additional relevant context can be logically inferred, include it as well.
- After each point, include the **source URL only** at the end of the point in this exact format: ([https://source-url.com])
  - If the source URL is not available, do NOT write anything — simply omit the source entirely.
  - Do NOT write "Source:", "Information not found in provided sources.", or any other label.
- At the end of the list, provide a **confidence score** in the format: `Confidence: X`, where:
  - 1.0 → Information comes from full web search
  - 0.5 → Information comes from RAG + web search
  - 0.0 → Information comes entirely from the provided context (RAG)
- Do NOT return JSON.
- Do NOT add explanations outside the numbered list.
- Do NOT include any source label text — only bare URLs inside ([]).
- Ensure each sentence ends with a line break before the next sentence.
- Number each key point properly in sequence.

Example format:
{{

1. First key point here.
   Second sentence of the first point if needed.
   ([https://examplesource1.com])

2. Second key point here.
   Additional info if relevant.
   ([https://example-source2.com])

3. Third key point here.
   ([https://examplesource3.com])

Confidence: 1.0
}}

Now generate the response.
"""

    response = llm.invoke(prompt)

    final_answer = f"{response.content}\nSources:\n{citations}"

    save_message(session_id, "assistant", final_answer)

    return final_answer
