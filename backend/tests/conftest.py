import sys
import types


def _ensure_langchain_community_stub():
    if "langchain_community.vectorstores" in sys.modules:
        return

    langchain_community = sys.modules.get("langchain_community")
    if langchain_community is None:
        langchain_community = types.ModuleType("langchain_community")
        sys.modules["langchain_community"] = langchain_community

    vectorstores = types.ModuleType("langchain_community.vectorstores")

    class DummyFAISS:
        @staticmethod
        def load_local(*_args, **_kwargs):
            return types.SimpleNamespace(
                similarity_search_with_relevance_scores=lambda *_a, **_k: [],
                similarity_search=lambda *_a, **_k: [],
            )

        @staticmethod
        def from_documents(_documents, _embeddings):
            return types.SimpleNamespace(save_local=lambda *_a, **_k: None)

    vectorstores.FAISS = DummyFAISS
    sys.modules["langchain_community.vectorstores"] = vectorstores
    langchain_community.vectorstores = vectorstores


def _ensure_langchain_google_genai_stub():
    if "langchain_google_genai" in sys.modules:
        return

    module = types.ModuleType("langchain_google_genai")

    class ChatGoogleGenerativeAI:
        def __init__(self, *args, **kwargs):
            self.args = args
            self.kwargs = kwargs

        def invoke(self, _prompt):
            return types.SimpleNamespace(content="stub-response")

    class GoogleGenerativeAIEmbeddings:
        def __init__(self, *args, **kwargs):
            self.args = args
            self.kwargs = kwargs

    module.ChatGoogleGenerativeAI = ChatGoogleGenerativeAI
    module.GoogleGenerativeAIEmbeddings = GoogleGenerativeAIEmbeddings
    sys.modules["langchain_google_genai"] = module


def _ensure_tavily_wikipedia_stubs():
    if "tavily" not in sys.modules:
        tavily = types.ModuleType("tavily")

        class TavilyClient:
            def __init__(self, api_key=None):
                self.api_key = api_key

            def search(self, **_kwargs):
                return {"results": []}

        tavily.TavilyClient = TavilyClient
        sys.modules["tavily"] = tavily

    if "wikipedia" not in sys.modules:
        wiki = types.ModuleType("wikipedia")
        wiki.search = lambda *_a, **_k: []
        wiki.page = lambda *_a, **_k: types.SimpleNamespace(url="https://example.com")
        wiki.summary = lambda *_a, **_k: "summary"
        sys.modules["wikipedia"] = wiki


_ensure_langchain_community_stub()
_ensure_langchain_google_genai_stub()
_ensure_tavily_wikipedia_stubs()
