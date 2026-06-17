from datetime import datetime
from lens.core.utils import get_with_retry

def collect(query: str) -> dict:
    url = f"https://doaj.org/api/v2/search/articles/{query}"
    params = {"pageSize": 10}
    
    response = get_with_retry(url, params=params)
    response.raise_for_status()
    
    data = response.json()
    results = data.get("results", [])
    
    cleaned_results = []
    for item in results:
        bibjson = item.get("bibjson", {})
        cleaned_results.append({
            "id": item.get("id"),
            "title": bibjson.get("title"),
            "authors": [a.get("name") for a in bibjson.get("author", [])],
            "journal": bibjson.get("journal", {}).get("title"),
            "year": bibjson.get("year"),
            "month": bibjson.get("month"),
            "abstract": bibjson.get("abstract"),
            "doi": next((id.get("id") for id in bibjson.get("identifier", []) if id.get("type") == "doi"), None),
            "link": next((l.get("url") for l in bibjson.get("link", []) if l.get("type") == "fulltext"), None)
        })

    return {
        "query": query,
        "source": "doaj",
        "collected_at": datetime.now().isoformat(),
        "total_results": len(cleaned_results),
        "results": cleaned_results,
    }
