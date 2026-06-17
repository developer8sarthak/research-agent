from datetime import datetime
from lens.core.utils import get_with_retry

def collect(query: str) -> dict:
    url = "https://api.semanticscholar.org/graph/v1/paper/search"
    params = {
        "query": query,
        "limit": 25,
        "fields": "title,abstract,year,citationCount,influentialCitationCount,authors,fieldsOfStudy,url",
    }
    headers = {"User-Agent": "Lens/1.0"}

    response = get_with_retry(url, params=params, headers=headers)
    response.raise_for_status()

    raw_data = response.json()
    papers = []

    for paper in raw_data.get("data", []):
        authors = []
        for author in paper.get("authors", []):
            authors.append(author.get("name"))

        papers.append(
            {
                "title": paper.get("title"),
                "abstract": paper.get("abstract"),
                "year": paper.get("year"),
                "citation_count": paper.get("citationCount"),
                "influential_citation_count": paper.get("influentialCitationCount"),
                "authors": authors,
                "fields_of_study": paper.get("fieldsOfStudy", []),
                "url": paper.get("url"),
            }
        )

    return {
        "query": query,
        "source": "semantic_scholar",
        "collected_at": datetime.now().isoformat(),
        "total_results": len(papers),
        "results": papers,
    }
