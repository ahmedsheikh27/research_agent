import re

from app.agent import research_agent as ra


class SmartFakeLLM:
    def __init__(self):
        self.prompts = []

    def invoke(self, prompt):
        self.prompts.append(prompt)

        if "Conversation History:" in prompt:
            if "renewable energy in Egypt" in prompt:
                content = "You said the project is about renewable energy in Egypt."
            else:
                content = "The provided conversation history does not contain information to answer this question."
            return type("Resp", (), {"content": content})()

        content = (
            "Rag searched items:\n\n"
            "Egypt plans to increase renewable energy to 42 percent by 2030. https://energy.gov.eg\n\n"
            "Solar capacity is expanding in Benban with government-backed projects. https://energy.gov.eg/benban\n\n"
            "Confidence: 1.0"
        )
        return type("Resp", (), {"content": content})()


def _extract_urls(text):
    return re.findall(r"https?://[^\s]+", text)


def _score_followup_answer(answer, required_phrases):
    score = 0
    for phrase in required_phrases:
        if phrase.lower() in answer.lower():
            score += 1
    return score / max(len(required_phrases), 1)


def _citation_relevance_score(answer, allowed_urls):
    urls = _extract_urls(answer)
    if not urls:
        return 0.0
    valid = [u for u in urls if u in allowed_urls]
    return len(valid) / len(urls)


def _e2e_answer_quality_score(answer, required_header, required_confidence, factual_phrases):
    checks = [
        required_header in answer,
        required_confidence in answer,
    ]
    checks.extend(phrase.lower() in answer.lower() for phrase in factual_phrases)
    return sum(checks) / len(checks)


def test_followup_question_answered_correctly(monkeypatch):
    fake_llm = SmartFakeLLM()
    saved_messages = []

    monkeypatch.setattr(ra, "llm", fake_llm)
    monkeypatch.setattr(
        ra,
        "get_chat",
        lambda _sid: {
            "pdf": False,
            "messages": [
                {"role": "user", "content": "My project is about renewable energy in Egypt."},
                {"role": "assistant", "content": "Great topic, let us research policy and targets."},
            ],
        },
    )
    monkeypatch.setattr(
        ra,
        "save_message",
        lambda sid, role, content: saved_messages.append((sid, role, content)),
    )
    monkeypatch.setattr(ra, "is_conversation_question", lambda _q: True)

    answer = ra.handle_query("quality-session-1", "What did I say my project is about?")

    score = _score_followup_answer(answer, ["renewable energy", "Egypt"])
    assert score >= 1.0
    assert saved_messages[-1] == ("quality-session-1", "assistant", answer)


def test_citations_point_to_relevant_sources(monkeypatch):
    fake_llm = SmartFakeLLM()
    monkeypatch.setattr(ra, "llm", fake_llm)
    monkeypatch.setattr(
        ra,
        "get_chat",
        lambda _sid: {"pdf": False, "messages": []},
    )
    monkeypatch.setattr(ra, "save_message", lambda *_a, **_k: None)
    monkeypatch.setattr(ra, "is_conversation_question", lambda _q: False)
    monkeypatch.setattr(
        ra,
        "run_rag",
        lambda *_a, **_k: {
            "mode": "RAG",
            "context": (
                "Egypt plans to increase renewable energy.\nSource: https://energy.gov.eg\n\n"
                "Benban is a major solar park.\nSource: https://energy.gov.eg/benban"
            ),
            "web_results": [],
        },
    )

    answer = ra.handle_query("quality-session-2", "Give me renewable energy updates in Egypt")
    allowed_urls = {"https://energy.gov.eg", "https://energy.gov.eg/benban"}
    score = _citation_relevance_score(answer, allowed_urls)
    assert score == 1.0


def test_end_to_end_query_answer_quality(monkeypatch):
    fake_llm = SmartFakeLLM()
    monkeypatch.setattr(ra, "llm", fake_llm)
    monkeypatch.setattr(ra, "save_message", lambda *_a, **_k: None)
    monkeypatch.setattr(ra, "is_conversation_question", lambda _q: False)
    monkeypatch.setattr(ra, "get_chat", lambda _sid: {"pdf": False, "messages": []})
    monkeypatch.setattr(
        ra,
        "run_rag",
        lambda *_a, **_k: {
            "mode": "RAG",
            "context": (
                "Egypt plans to increase renewable energy to 42 percent by 2030.\n"
                "Source: https://energy.gov.eg\n\n"
                "Solar capacity is expanding in Benban.\n"
                "Source: https://energy.gov.eg/benban"
            ),
            "web_results": [],
        },
    )

    answer = ra.handle_query("quality-session-3", "Summarize Egypt renewable energy targets")
    score = _e2e_answer_quality_score(
        answer=answer,
        required_header="Rag searched items:",
        required_confidence="Confidence: 1.0",
        factual_phrases=["42 percent by 2030", "Benban"],
    )
    assert score >= 0.8
