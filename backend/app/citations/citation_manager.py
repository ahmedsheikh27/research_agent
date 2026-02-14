def format_citations(results):
    citations = []
    for i, r in enumerate(results):
        citations.append(f"[{i+1}] {r.get('url')}")
    return "\n".join(citations)
