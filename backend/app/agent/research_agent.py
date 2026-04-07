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


def build_prompt(mode: str, context: str, query: str) -> str:

    if mode == "PDF":
        header_text   = "Pdf searched items:"
        confidence_val = "0.8."
        format_rule   = "Use ## Markdown headings and full paragraphs. Do NOT use bullet points, lists, or dashes."
        example_block = f"""\
Example output:

{header_text}

## Main Topic

A full paragraph explaining the relevant information found in the PDF.

## Supporting Detail (if applicable)

Another paragraph with additional context from the PDF.

Confidence: {confidence_val}"""

    elif mode == "RAG":
        header_text    = "Rag searched items:"
        confidence_val = "1.0"
        format_rule    = "Write each fact as a plain sentence on its own line, separated by a blank line. No bullets, no numbers, no dashes, no symbols."
        example_block  = f"""\
Example output:

{header_text}

First relevant piece of information from the knowledge base.

Second relevant piece of information from the knowledge base. https://example.com

Confidence: {confidence_val}"""

    else:  # WEB
        header_text    = "Web searched results:"
        confidence_val = "0.5"
        format_rule    = "Write each fact as a plain sentence on its own line, separated by a blank line. No bullets, no numbers, no dashes, no symbols."
        example_block  = f"""\
Example output:

{header_text}

Information about the topic explained clearly here. https://example.com

Another relevant piece of information. https://example.com

Confidence: {confidence_val}"""

    return f"""You are a research assistant. Answer the user's question ONLY using the provided context below.

Mode: {mode}
User Question: {query}

Context:
{context}

---

STRICT RULES — follow exactly for mode "{mode}":

1. Start your response with this exact line: {header_text}
2. {format_rule}
3. {"Do NOT include any URLs or source links." if mode == "PDF" else "If a source URL exists in the context, place it at the end of that item's line."}
4. End your response with this exact line: Confidence: {confidence_val}
5. Do NOT write anything after "Confidence: {confidence_val}".
6. Do NOT change the header or confidence value.

---

{example_block}

---

Now write your answer strictly following the format shown above.
"""


def handle_query(session_id: str, query: str):

    chat = get_chat(session_id)
    save_message(session_id, "user", query)

    chat_history = build_conversation_history(session_id)
    is_pdf = chat.get("pdf", False) if chat else False

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
    print(f"[DEBUG] session_id: {session_id}")
    print(f"[DEBUG] chat object: {chat}")          # is it None?
    print(f"[DEBUG] is_pdf flag: {is_pdf}")        # is it True or False?

    # ── RAG / WEB / PDF MODE ─────────────────────────────────
    rag_result = run_rag(query, session_id, pdf_chat=is_pdf)

    # Early exit — no relevant content found
    if rag_result.get("no_results"):
        message = rag_result["context"]
        save_message(session_id, "assistant", message)
        return message

    mode    = rag_result["mode"]
    context = rag_result["context"]

    # Guardrail: if this is a PDF chat session, force PDF output formatting/header.
    # This prevents accidental "Rag searched items:" responses for uploaded-PDF chats.
    if is_pdf and mode in {"RAG", "WEB"}:
        mode = "PDF"

    if mode == "WEB" and rag_result.get("web_results"):
        for result in rag_result["web_results"]:
            content = result.get("content", "")
            url     = result.get("url", "N/A")
            if content:
                context += f"\n\n{content}\nSource: {url}"

    prompt       = build_prompt(mode, context, query)
    response     = llm.invoke(prompt)
    final_answer = response.content

    save_message(session_id, "assistant", final_answer)
    return final_answer