"""GeneDisco Agent: Multi-tool AI agent for therapeutic target discovery."""
import json
import os
import logging
from pathlib import Path
from typing import Dict, Any, List
import requests

from tools.disease_gene import DiseaseGeneTool
from tools.ppi_network import PPINetworkTool
from tools.pathway_enrichment import PathwayEnrichmentTool
from tools.literature_search import LiteratureSearchTool
from tools.druggability import DruggabilityTool

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


class GeneDiscoAgent:
    """Multi-step agent that discovers and prioritizes therapeutic targets for a disease."""

    def __init__(
        self,
        disease: str,
        top_n_genes: int = 30,
        llm_api_base: str = None,
        llm_api_key: str = None,
        model: str = "Kimi-K2.7",
        cache_dir: str = None,
        use_cache: bool = True,
    ):
        self.disease = disease
        self.top_n_genes = top_n_genes
        self.cache_dir = Path(cache_dir) if cache_dir else Path(__file__).resolve().parent.parent / "data"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.use_cache = use_cache

        # LLM config: prefer env vars, then arguments.
        self.llm_api_base = llm_api_base or os.environ.get("LLM_API_BASE", "https://llmapi.paratera.com/v1")
        self.llm_api_key = llm_api_key or os.environ.get("LLM_API_KEY")
        self.model = model

        # Tool instances
        self.disease_tool = DiseaseGeneTool(cache_dir=str(self.cache_dir))
        self.ppi_tool = PPINetworkTool(cache_dir=str(self.cache_dir))
        self.pathway_tool = PathwayEnrichmentTool(cache_dir=str(self.cache_dir))
        self.literature_tool = LiteratureSearchTool(cache_dir=str(self.cache_dir))
        self.druggability_tool = DruggabilityTool()

        # Working memory
        self.memory: Dict[str, Any] = {
            "disease": disease,
            "genes": [],
            "ppi": {},
            "pathways": [],
            "papers": [],
            "druggability": [],
            "ranked_targets": [],
            "hypotheses": [],
        }

    def _call_llm(self, system: str, user: str, temperature: float = 0.3) -> str:
        """Call the configured LLM. Falls back to a stub if no key is available."""
        if not self.llm_api_key:
            logger.warning("LLM_API_KEY not set; returning placeholder text.")
            return "[LLM output omitted because no API key was configured.]"
        try:
            resp = requests.post(
                f"{self.llm_api_base}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.llm_api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": system},
                        {"role": "user", "content": user},
                    ],
                    "temperature": temperature,
                },
                timeout=60,
            )
            resp.raise_for_status()
            return resp.json()["choices"][0]["message"]["content"]
        except Exception as exc:
            logger.error(f"LLM call failed: {exc}")
            return f"[LLM call failed: {exc}]"

    def step_retrieve_genes(self) -> None:
        logger.info("Step 1/5: Retrieve disease-associated genes...")
        genes = self.disease_tool.run(self.disease, self.top_n_genes, self.use_cache)
        self.memory["genes"] = genes
        logger.info("  -> Retrieved %d genes.", len(genes))

    def step_build_ppi(self) -> None:
        logger.info("Step 2/5: Build PPI subnetwork...")
        symbols = [g["gene_symbol"] for g in self.memory["genes"]]
        network = self.ppi_tool.run(symbols, self.use_cache)
        self.memory["ppi"] = network
        logger.info("  -> PPI has %d nodes and %d edges.", len(network.get("nodes", [])), len(network.get("edges", [])))

    def step_pathway_enrichment(self) -> None:
        logger.info("Step 3/5: Pathway enrichment...")
        symbols = [g["gene_symbol"] for g in self.memory["genes"]]
        pathways = self.pathway_tool.run(symbols, self.use_cache)
        self.memory["pathways"] = pathways
        logger.info("  -> Found %d enriched pathways.", len(pathways))

    def step_literature(self) -> None:
        logger.info("Step 4/5: Literature search...")
        papers = self.literature_tool.run(f"{self.disease} therapeutic target", 10, self.use_cache)
        self.memory["papers"] = papers
        logger.info("  -> Found %d papers.", len(papers))

    def step_druggability(self) -> None:
        logger.info("Step 5/5: Druggability scoring...")
        symbols = [g["gene_symbol"] for g in self.memory["genes"]]
        scores = self.druggability_tool.run(symbols)
        self.memory["druggability"] = scores
        logger.info("  -> Scored %d genes.", len(scores))

    def step_prioritize(self) -> None:
        logger.info("Prioritizing targets...")
        gene_scores = {g["gene_symbol"]: g["score"] for g in self.memory["genes"]}
        drug_scores = {d["gene_symbol"]: d["druggability_score"] for d in self.memory["druggability"]}
        combined = []
        for g in self.memory["genes"]:
            sym = g["gene_symbol"]
            assoc = gene_scores.get(sym, 0)
            drug = drug_scores.get(sym, 0)
            combined.append({
                "gene_symbol": sym,
                "gene_name": g["gene_name"],
                "association_score": assoc,
                "druggability_score": drug,
                "priority_score": round(0.6 * drug + 0.4 * assoc, 3),
            })
        combined.sort(key=lambda x: x["priority_score"], reverse=True)
        self.memory["ranked_targets"] = combined

    def step_generate_hypotheses(self) -> None:
        logger.info("Generating hypotheses via LLM...")
        top5 = self.memory["ranked_targets"][:5]
        top5_text = "\n".join(
            f"- {t['gene_symbol']} ({t['gene_name']}): priority={t['priority_score']}, "
            f"association={t['association_score']}, druggability={t['druggability_score']}"
            for t in top5
        )
        pathway_text = "\n".join(
            f"- {p['pathway_name']} ({p['source']}, p={p['p_value']:.2e})"
            for p in self.memory["pathways"][:8]
        )
        user_prompt = (
            f"Disease: {self.disease}\n\n"
            f"Top candidate therapeutic targets:\n{top5_text}\n\n"
            f"Enriched pathways:\n{pathway_text}\n\n"
            "Based on the above evidence, propose 3 novel, testable biological hypotheses "
            "about which target(s) would be most promising for therapeutic intervention and why. "
            "For each hypothesis, include: (1) proposed mechanism, (2) supporting evidence, "
            "(3) a validation experiment, and (4) potential risks."
        )
        system_prompt = (
            "You are an expert computational biologist and drug discovery scientist. "
            "Be concise but rigorous. Prioritize novelty balanced with biological plausibility."
        )
        response = self._call_llm(system_prompt, user_prompt)
        self.memory["hypotheses"] = response

    def run(self) -> Dict[str, Any]:
        self.step_retrieve_genes()
        self.step_build_ppi()
        self.step_pathway_enrichment()
        self.step_literature()
        self.step_druggability()
        self.step_prioritize()
        self.step_generate_hypotheses()
        return self.memory

    def save_report(self, output_path: str = None) -> Path:
        if output_path is None:
            output_dir = Path(__file__).resolve().parent.parent / "outputs"
            output_dir.mkdir(parents=True, exist_ok=True)
            output_path = output_dir / f"{self.disease.replace(' ', '_')}_report.json"
        else:
            output_path = Path(output_path)
        output_path.write_text(json.dumps(self.memory, indent=2, ensure_ascii=False), encoding="utf-8")
        logger.info("Report saved to %s", output_path)
        return output_path


def main():
    import argparse
    parser = argparse.ArgumentParser(description="GeneDisco Agent for therapeutic target discovery.")
    parser.add_argument("disease", help="Disease name to investigate, e.g., 'Non-alcoholic steatohepatitis'.")
    parser.add_argument("--top-n", type=int, default=15, help="Number of top disease genes to retrieve.")
    parser.add_argument("--output", default=None, help="Path to save the JSON report.")
    parser.add_argument("--no-cache", action="store_true", help="Disable reading/writing cache files.")
    args = parser.parse_args()

    agent = GeneDiscoAgent(
        disease=args.disease,
        top_n_genes=args.top_n,
        use_cache=not args.no_cache,
    )
    agent.run()
    agent.save_report(args.output)


if __name__ == "__main__":
    main()
