"""Protein-protein interaction (PPI) subnetwork construction tool."""
import json
from pathlib import Path
from typing import List, Dict, Any
import requests


class PPINetworkTool:
    """Build a PPI subnetwork from a gene list using STRING or a cached fallback."""

    def __init__(self, cache_dir: str = None):
        self.cache_dir = Path(cache_dir) if cache_dir else Path(__file__).resolve().parents[2] / "data"
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _cache_path(self, seed_genes: List[str]) -> Path:
        safe = "_".join(sorted(seed_genes))[:80]
        return self.cache_dir / f"ppi_{hash(safe)}.json"

    def _fetch_string(self, genes: List[str], species: int = 9606) -> Dict[str, Any]:
        try:
            identifiers = "%2C".join(genes)
            url = (
                f"https://string-db.org/api/json/network?identifiers={identifiers}&species={species}"
            )
            resp = requests.get(url, timeout=20)
            resp.raise_for_status()
            rows = resp.json()
            nodes = list({n for r in rows for n in (r.get("preferredName_A"), r.get("preferredName_B"))})
            edges = [
                {"source": r["preferredName_A"], "target": r["preferredName_B"], "score": r["score"]}
                for r in rows
            ]
            return {"nodes": nodes, "edges": edges, "source": "STRING"}
        except Exception as exc:
            print(f"[PPINetworkTool] STRING request failed: {exc}; using fallback.")
            return self._fallback(genes)

    def _fallback(self, genes: List[str]) -> Dict[str, Any]:
        """Return a hand-curated realistic subnetwork for demo purposes."""
        # Edges represent known/plausible interactions among NASH/metabolic genes.
        curated_edges = [
            ("PNPLA3", "TM6SF2", 0.78),
            ("PNPLA3", "MBOAT7", 0.72),
            ("TM6SF2", "MBOAT7", 0.65),
            ("PNPLA3", "SREBF1", 0.60),
            ("SREBF1", "FASN", 0.82),
            ("SREBF1", "ACACA", 0.79),
            ("PPARG", "FASN", 0.68),
            ("PPARG", "SREBF1", 0.71),
            ("TNF", "IL6", 0.88),
            ("TNF", "PPARG", 0.55),
            ("APOE", "PNPLA3", 0.52),
            ("MTTP", "APOE", 0.74),
            ("CYP2E1", "SOD2", 0.50),
            ("DGAT2", "FASN", 0.61),
            ("SCD", "FASN", 0.77),
            ("HSD17B13", "PNPLA3", 0.69),
            ("HSD17B13", "TM6SF2", 0.57),
        ]
        gene_set = set(genes)
        edges = [
            {"source": a, "target": b, "score": s}
            for a, b, s in curated_edges
            if a in gene_set and b in gene_set
        ]
        nodes = list(gene_set | {e["target"] for e in edges} | {e["source"] for e in edges})
        return {"nodes": nodes, "edges": edges, "source": "fallback-curated"}

    def run(self, genes: List[str], use_cache: bool = True) -> Dict[str, Any]:
        cache = self._cache_path(genes)
        if use_cache and cache.exists():
            return json.loads(cache.read_text(encoding="utf-8"))
        network = self._fetch_string(genes)
        if use_cache:
            cache.write_text(json.dumps(network, indent=2, ensure_ascii=False), encoding="utf-8")
        return network
