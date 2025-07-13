from duckduckgo_search import DDGS

def web_search(query: str) -> str:
    results = []
    with DDGS() as ddgs:
        for r in ddgs.text(query, region="wt-wt", safesearch="Moderate", timelimit="d"):
            results.append(f"🔹 <b>{r['title']}</b>\n{r['href']}")
            if len(results) >= 3:
                break
    return "\n\n".join(results) if results else "Ничего не найдено."