import xml.etree.ElementTree as ET
from datetime import datetime
from lens.core.utils import get_with_retry

def collect(query: str) -> dict:
    url = "https://export.arxiv.org/api/query"
    params = {"search_query": f"all:{query}", "start": 0, "max_results": 25}

    response = get_with_retry(url, params=params)
    response.raise_for_status()

    root = ET.fromstring(response.text)
    namespace = {"atom": "http://www.w3.org/2005/Atom"}

    papers = []
    for entry in root.findall("atom:entry", namespace):
        authors = []
        for author in entry.findall("atom:author", namespace):
            authors.append(author.find("atom:name", namespace).text)

        paper = {
            "title": entry.find("atom:title", namespace).text.strip(),
            "summary": entry.find("atom:summary", namespace).text.strip(),
            "published": entry.find("atom:published", namespace).text,
            "updated": entry.find("atom:updated", namespace).text,
            "authors": authors,
            "url": entry.find("atom:id", namespace).text,
        }
        papers.append(paper)

    return {
        "query": query,
        "source": "arxiv",
        "collected_at": datetime.now().isoformat(),
        "total_results": len(papers),
        "results": papers,
    }
