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

    rag_result = run_rag(query)

    mode = rag_result["mode"]
    context = rag_result["context"]
    web_results = rag_result["web_results"]
    for result in web_results:
        context += f"\n\n{result['content']}\nSource: {result['url']}"

    
    prompt = f"""
Conversation History:
{chat_history}

RAG Context:
{context}

Mode Used:
{mode}

User Question:
{query}

Instructions:

Formatting Rules (VERY STRICT):
1. If mode is WEB, answer ONLY from Web Context and your answer format is EXACTLY with:
Web searched results:

2. If mode is RAG, answer ONLY from RAG Context and your answer format is EXACTLY with:
Rag searched items:

3. After the heading, provide a numbered ordered list.

4. Each numbered item must:
   - Be on a new line.
   - Contain complete information.
   - End with the source URL in this exact format:
     https://example.com

5. Leave one blank line between each numbered item.

Correct Format Example:

Web searched results:

1. Some information here with explanation. https://example.com

2. Another piece of information here. https://example.com

3. Third piece of information here. https://example.com

Important Rules:

- Do NOT use bullet points.
- Do NOT return JSON.
- Do NOT write "Source:".
- Do NOT add text before or after the list.
- If no URL exists in RAG context, omit the URL completely.
- Do NOT hallucinate any information.
- Use ONLY provided context.

Confidence scoring rules:

- 1.0 → your confidense is 1.0 if you used Pure RAG
- 0.5 → your confidense is 0.5 if you used Pure WEB

After the list, add exactly:

Confidence: X
"""

    response = llm.invoke(prompt)

    final_answer = response.content

    save_message(session_id, "assistant", final_answer)

    return final_answer