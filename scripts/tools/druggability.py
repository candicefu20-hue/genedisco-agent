"""Druggability scoring tool."""
from typing import List, Dict, Any


class DruggabilityTool:
    """Score candidate genes by simple druggability heuristics."""

    # A small curated set of known druggable genes for demo.
    KNOWN_DRUGGABLE = {
        "TNF": {"class": "cytokine / biologic", "evidence": "approved antibody inhibitors"},
        "IL6": {"class": "cytokine / biologic", "evidence": "approved antibody inhibitors"},
        "PPARG": {"class": "nuclear receptor / small molecule", "evidence": "thiazolidinediones"},
        "MTOR": {"class": "kinase / small molecule", "evidence": "rapamycin analogs"},
        "STAT3": {"class": "transcription factor / small molecule", "evidence": "inhibitors in clinical trials"},
        "FASN": {"class": "enzyme / small molecule", "evidence": "C75, C93 inhibitors in preclinical"},
        "ACACA": {"class": "enzyme / small molecule", "evidence": "small-molecule inhibitors investigated"},
        "CYP2E1": {"class": "enzyme / small molecule", "evidence": "inhibitors such as chlormethiazole"},
        "DGAT2": {"class": "enzyme / small molecule", "evidence": "preclinical inhibitors"},
        "SCD": {"class": "enzyme / small molecule", "evidence": "preclinical inhibitors"},
        "SREBF1": {"class": "transcription factor / small molecule", "evidence": "challenging but emerging approaches"},
    }

    def run(self, genes: List[str]) -> List[Dict[str, Any]]:
        results = []
        for g in genes:
            info = self.KNOWN_DRUGGABLE.get(g, {})
            is_druggable = bool(info)
            # Simple heuristic score: known druggable gets 0.8; otherwise a default 0.3
            score = 0.8 if is_druggable else 0.3
            results.append({
                "gene_symbol": g,
                "druggable": is_druggable,
                "druggability_score": score,
                "protein_class": info.get("class", "unknown"),
                "evidence": info.get("evidence", "limited evidence"),
            })
        return results
