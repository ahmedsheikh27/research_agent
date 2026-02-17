from tavily import TavilyClient
from app.config import TAVILY_API_KEY

tavily_client = TavilyClient(api_key=TAVILY_API_KEY)


def search_web(query: str):
    response = tavily_client.search(
        query=query, include_answer="advanced", search_depth="advanced", max_results=5
    )
    results = response.get("results", [])
    simplified_results = []
    for r in results:
        simplified_results.append({
            "url": r.get("url"),
            "content": r.get("content"),
            "score": r.get("score")
        })
    
    print(simplified_results)
    return simplified_results
