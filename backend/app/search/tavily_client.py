from tavily import TavilyClient
from app.config import TAVILY_API_KEY

tavily_client = TavilyClient(api_key=TAVILY_API_KEY)

def search_web(query: str):
    response = tavily_client.search(query=query, max_results=5)
    return response.get("results", [])
