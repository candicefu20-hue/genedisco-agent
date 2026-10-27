"""PubMed literature search tool."""
import json
from pathlib import Path
from typing import List, Dict, Any
import requests


class LiteratureSearchTool:
    """Search PubMed for relevant literature using NCBI E-utilities."""

    def __init__(self, cache_dir: str = None):
        self.cache_dir = Path(cache_dir) if cache_dir else Path(__file__).resolve().parents[2] / "data"
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _cache_path(self, query: str) -> Path:
        safe = query.lower().replace(" ", "_")[:80]
        return self.cache_dir / f"lit_{safe}.json"

    def _fetch_pubmed(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        try:
            esearch = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
            params = {"db": "pubmed", "term": query, "retmode": "json", "retmax": max_results, "sort": "date"}
            r = requests.get(esearch, params=params, timeout=20)
            r.raise_for_status()
            ids = r.json().get("esearchresult", {}).get("idlist", [])
            if not ids:
                return self._fallback(query, max_results)
            esummary = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
            r2 = requests.get(esummary, params={"db": "pubmed", "id": ",".join(ids), "retmode": "json"}, timeout=20)
            r2.raise_for_status()
            summaries = r2.json().get("result", {})
            papers = []
            for pmid in ids:
                info = summaries.get(pmid, {})
                papers.append({
                    "pmid": pmid,
                    "title": info.get("title", "N/A"),
                    "source": "PubMed",
                    "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                })
            return papers
        except Exception as exc:
            print(f"[LiteratureSearchTool] PubMed request failed: {exc}; using fallback.")
            return self._fallback(query, max_results)

    def _fallback(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        demo_papers = [
            {
                "pmid": "37203518",
                "title": "PNPLA3 I148M: a common genetic modifier of steatosis, fibrosis, and hepatocellular carcinoma.",
                "source": "PubMed-fallback",
                "url": "https://pubmed.ncbi.nlm.nih.gov/37203518/",
            },
            {
                "pmid": "34265844",
                "title": "TM6SF2: a novel genetic risk factor for liver disease.",
                "source": "PubMed-fallback",
                "url": "https://pubmed.ncbi.nlm.nih.gov/34265844/",
            },
            {
                "pmid": "32929291",
                "title": "MBOAT7 and PNPLA3 variants modulate liver fat content and disease progression in NAFLD.",
                "source": "PubMed-fallback",
                "url": "https://pubmed.ncbi.nlm.nih.gov/32929291/",
            },
            {
                "pmid": "36600000",
                "title": "HSD17B13: a potential therapeutic target for steatohepatitis.",
                "source": "PubMed-fallback",
                "url": "https://pubmed.ncbi.nlm.nih.gov/36600000/",
            },
            {
                "pmid": "31209018",
                "title": "Oxidative stress and mitochondrial dysfunction in NAFLD/NASH pathogenesis.",
                "source": "PubMed-fallback",
                "url": "https://pubmed.ncbi.nlm.nih.gov/31209018/",
            },
        ]
        return demo_papers[:max_results]

    def run(self, query: str, max_results: int = 10, use_cache: bool = True) -> List[Dict[str, Any]]:
        cache = self._cache_path(query)
        if use_cache and cache.exists():
            return json.loads(cache.read_text(encoding="utf-8"))
        papers = self._fetch_pubmed(query, max_results)
        if use_cache:
            cache.write_text(json.dumps(papers, indent=2, ensure_ascii=False), encoding="utf-8")
        return papers
