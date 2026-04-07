from tavily import TavilyClient
from app.config import TAVILY_API_KEY
import wikipedia

tavily_client = TavilyClient(api_key=TAVILY_API_KEY)


def search_web(query: str):
    # Tavily search
    tavily_response = tavily_client.search(
        query=query,
        include_answer="advanced",
        search_depth="advanced",
        max_results=5
    )

    tavily_results = tavily_response.get("results", [])
    simplified_tavily = []

    for r in tavily_results:
        simplified_tavily.append({
            "url": r.get("url"),
            "content": r.get("content"),
            "score": r.get("score")
        })

    print("Tavily API used")

    # Wikipedia search
    try:
        wiki_titles = wikipedia.search(query, results=3)
        wiki_results = []

        for title in wiki_titles:
            try:
                page = wikipedia.page(title)
                wiki_results.append({
                    "url": page.url,
                    "content": wikipedia.summary(title, sentences=2),
                    "score": 1.0
                })
            except:
                continue

        print("Wikipedia API used")

    except Exception as e:
        print(f"Wikipedia error: {e}")
        wiki_results = []

    # 🔥 Combine both
    combined_results = simplified_tavily + wiki_results

    # Optional: sort by score
    combined_results = sorted(
        combined_results,
        key=lambda x: x.get("score", 0),
        reverse=True
    )

    print("Final Combined Results")
    print(combined_results)

    return combined_results