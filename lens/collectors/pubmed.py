from datetime import datetime
from lens.core.utils import get_with_retry

def collect(query: str) -> dict:
    # PubMed E-search to get IDs
    search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    search_params = {
        "db": "pubmed",
        "term": query,
        "retmode": "json",
        "retmax": 10
    }
    
    response = get_with_retry(search_url, params=search_params)
    response.raise_for_status()
    
    search_data = response.json()
    ids = search_data.get("esearchresult", {}).get("idlist", [])
    
    cleaned_results = []
    if ids:
        # PubMed E-summary to get details
        summary_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
        summary_params = {
            "db": "pubmed",
            "id": ",".join(ids),
            "retmode": "json"
        }
        
        sum_response = get_with_retry(summary_url, params=summary_params)
        sum_response.raise_for_status()
        
        sum_data = sum_response.json()
        result_uids = sum_data.get("result", {}).get("uids", [])
        
        for uid in result_uids:
            item = sum_data.get("result", {}).get(uid, {})
            cleaned_results.append({
                "id": uid,
                "title": item.get("title"),
                "authors": [a.get("name") for a in item.get("authors", [])],
                "source": item.get("source"),
                "pubdate": item.get("pubdate"),
                "epubdate": item.get("epubdate"),
                "doi": next((v.get("value") for v in item.get("articleids", []) if v.get("idtype") == "doi"), None),
                "url": f"https://pubmed.ncbi.nlm.nih.gov/{uid}/"
            })

    return {
        "query": query,
        "source": "pubmed",
        "collected_at": datetime.now().isoformat(),
        "total_results": len(cleaned_results),
        "results": cleaned_results,
    }
