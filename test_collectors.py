import time
import pytest
from lens.collectors import (
    arxiv, semantic_scholar, reddit, wiki, github, openalex, crossref, pubmed, doaj
)

@pytest.mark.parametrize("name, collector_module", [
    ("ArXiv", arxiv),
    ("Semantic Scholar", semantic_scholar),
    ("Reddit", reddit),
    ("Wikipedia", wiki),
    ("GitHub", github),
    ("OpenAlex", openalex),
    ("CrossRef", crossref),
    ("PubMed", pubmed),
    ("DOAJ", doaj)
])
def test_collector(name, collector_module, query="AI"):
    print(f"Testing {name}...")
    try:
        # Each collector module has a 'collect' function
        result = collector_module.collect(query)
        assert result is not None
        assert "results" in result or isinstance(result, list)
        print(f"  {name} success!")
    except Exception as e:
        pytest.fail(f"{name} failed: {e}")
    time.sleep(1) # Respect rate limits
