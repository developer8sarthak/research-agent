from lens.collectors.wiki import collect as wiki_collect
from lens.collectors.github import collect as github_collect
from lens.collectors.arxiv import collect as arxiv_collect
from lens.collectors.openalex import collect as openalex_collect
from lens.collectors.crossref import collect as crossref_collect
from lens.collectors.reddit import collect as reddit_collect
from lens.collectors.semantic_scholar import collect as ssc_collect

from lens.collectors.pubmed import collect as pubmed_collect
from lens.collectors.doaj import collect as doaj_collect

COLLECTORS = {
    "wikipedia": wiki_collect,
    "github": github_collect,
    "arxiv": arxiv_collect,
    "openalex": openalex_collect,
    "crossref": crossref_collect,
    "reddit": reddit_collect,
    "semantic_scholar": ssc_collect,
    "pubmed": pubmed_collect,
    "doaj": doaj_collect
}
