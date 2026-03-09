from langchain_google_genai import ChatGoogleGenerativeAI
from app.config import GOOGLE_API_KEY
from app.rag.rag_pipeline import run_rag
from app.memory.memory_manager import save_message, get_chat
from app.agent.history_keywords import HISTORY_KEYWORDS

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
    keywords = HISTORY_KEYWORDS
    return any(k in query.lower() for k in keywords)


def handle_query(session_id: str, query: str):

    save_message(session_id, "user", query)

    chat_history = build_conversation_history(session_id)

    if is_conversation_question(query):

        prompt = f"""
Conversation History:
{chat_history}
User Question:
{query}
Instructions:
Answer clearly based ONLY on conversation history.
Rules:
1. Use ONLY information explicitly stated in the Conversation History.
2. Do NOT use external knowledge.
3. Do NOT use web knowledge.
4. Do NOT make assumptions.
5. Do NOT hallucinate missing details.
6. If the answer is not found in the conversation history, respond exactly with:
"The provided conversation history does not contain information to answer this question."
7. Do NOT add extra explanations.
8. Be concise and precise.
Answer:
"""
        response = llm.invoke(prompt)
        save_message(session_id, "assistant", response.content)
        return response.content

    # use RAG / Web 
    rag_result = run_rag(query, session_id)
    mode = rag_result["mode"]
    context = rag_result["context"]
    web_results = rag_result["web_results"]

    for result in web_results:
        context += f"\n\n{result['content']}\nSource: {result['url']}"

    prompt = f"""
You will be explicitly told which mode is active via the "Mode:" field below. Follow it exactly.

Context:{context}

Mode:{mode}

User Question:{query}


Instructions:

You are a research assistant. Your task is to answer the user's question ONLY using the provided context.
---

STRICT RULES:

1. Use ONLY the provided context.
2. NEVER use external knowledge.
3. NEVER hallucinate or invent facts.
4. If the answer is not in the context, respond only with the context message as-is.
5. Follow the formatting rules strictly.

---

Response Format Rules:

If Mode is WEB → start your response with exactly:
Web searched results:

If Mode is RAG → start your response with exactly:
Rag searched items:

Then provide an unordered list (no bullets, no numbers, no dashes).
Each item must be on its own line, separated by a blank line.
If a source URL exists, place it at the end of that item's line.

Example:

Web searched results:

Information about the topic explained clearly here. https://example.com

Another relevant piece of information. https://example.com

---

Restrictions:
- No numbered lists
- No bullet characters (-, *, •)
- No JSON output
- No "Source:" label
- No extra explanation outside the list

---

Confidence:
- If Mode is WEB → end with: Confidence: 0.5
- If Mode is RAG → end with: Confidence: 1.0
"""
    response = llm.invoke(prompt)
    final_answer = response.content
    save_message(session_id, "assistant", final_answer)

    return final_answer
