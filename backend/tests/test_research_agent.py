import sys
import types
from app.agent import research_agent as ra


class FakeLLM:
    def __init__(self, content):
        self.content = content
        self.prompts = []

    def invoke(self, prompt):
        self.prompts.append(prompt)
        return type("Resp", (), {"content": self.content})()


def _install_stub_modules():
    if "wikipedia" not in sys.modules:
        wiki = types.ModuleType("wikipedia")
        wiki.search = lambda *_a, **_k: []
        wiki.page = lambda *_a, **_k: types.SimpleNamespace(url="https://example.com")
        wiki.summary = lambda *_a, **_k: "summary"
        sys.modules["wikipedia"] = wiki

    if "tavily" not in sys.modules:
        tavily = types.ModuleType("tavily")

        class TavilyClient:
            def __init__(self, api_key=None):
                self.api_key = api_key

            def search(self, **_kwargs):
                return {"results": []}

        tavily.TavilyClient = TavilyClient
        sys.modules["tavily"] = tavily


def test_build_conversation_history(monkeypatch):
    _install_stub_modules()
    monkeypatch.setattr(
        ra,
        "get_chat",
        lambda _sid: {"messages": [{"role": "user", "content": "hello"}]},
    )
    history = ra.build_conversation_history("s1")
    assert "user: hello" in history


def test_is_conversation_question_matches_keywords():
    _install_stub_modules()
    assert ra.is_conversation_question("What was my first question?")
    assert ra.is_conversation_question("what we discuss first in chat")
    assert ra.is_conversation_question("on which topic we discus before")
    assert not ra.is_conversation_question("Explain transformers")


def test_handle_query_history_mode(monkeypatch):
    _install_stub_modules()
    fake_llm = FakeLLM("history answer")
    calls = []

    monkeypatch.setattr(ra, "llm", fake_llm)
    monkeypatch.setattr(
        ra,
        "get_chat",
        lambda _sid: {"messages": [{"role": "user", "content": "hi"}], "pdf": False},
    )
    monkeypatch.setattr(
        ra,
        "save_message",
        lambda sid, role, content: calls.append((sid, role, content)),
    )
    monkeypatch.setattr(ra, "is_conversation_question", lambda _q: True)

    output = ra.handle_query("s1", "what did i ask first")
    assert output == "history answer"
    assert calls[0] == ("s1", "user", "what did i ask first")
    assert calls[-1] == ("s1", "assistant", "history answer")


def test_handle_query_rag_no_results(monkeypatch):
    _install_stub_modules()
    calls = []
    monkeypatch.setattr(ra, "get_chat", lambda _sid: {"messages": [], "pdf": False})
    monkeypatch.setattr(
        ra,
        "save_message",
        lambda sid, role, content: calls.append((sid, role, content)),
    )
    monkeypatch.setattr(ra, "is_conversation_question", lambda _q: False)
    monkeypatch.setattr(ra, "run_rag", lambda *_a, **_k: {"no_results": True, "context": "No info"})

    output = ra.handle_query("s2", "new query")
    assert output == "No info"
    assert calls[-1] == ("s2", "assistant", "No info")
