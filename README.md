# GeneDisco Agent

A modular Biomedical AI Agent for therapeutic target discovery, designed for the "AI Agent for Biomedicine" course project.

## Overview

GeneDisco Agent takes a disease name as input and automatically:

1. Retrieves disease-associated genes from public databases.
2. Builds a protein-protein interaction (PPI) subnetwork.
3. Performs pathway enrichment analysis.
4. Searches the relevant literature.
5. Scores candidate genes by druggability.
6. Ranks therapeutic targets and generates testable hypotheses via LLM reasoning.

## Repository Structure

```
.
├── scripts/
│   ├── agent.py                     # Main agent
│   ├── insert_hypothesis.py          # Helper to inject LLM hypotheses into the report
│   └── tools/
│       ├── __init__.py
│       ├── disease_gene.py
│       ├── ppi_network.py
│       ├── pathway_enrichment.py
│       ├── literature_search.py
│       └── druggability.py
├── data/                              # Local cache for API responses (created on first run)
├── outputs/                           # Generated reports
├── logs/                              # Execution logs
├── 报告.md                            # Technical report (Chinese)
└── conversation.jsonl                 # AI conversation log
```

## Quick Start

### 1. Install dependencies

This project only requires the Python standard library plus `requests`. If `requests` is not installed:

```bash
pip install requests
```

### 2. Run the agent

```bash
python scripts/agent.py 'Non-alcoholic steatohepatitis' --top-n 15 --output outputs/nash_report.json
```

### 3. Optional: generate real LLM hypotheses

Set the LLM API key as an environment variable before running:

```bash
export LLM_API_KEY='your-api-key'
export LLM_API_BASE='https://llmapi.paratera.com/v1'
python scripts/agent.py 'Non-alcoholic steatohepatitis' --top-n 15 --output outputs/nash_report.json
```

If no key is provided, the agent will still run and produce a structured report; the hypothesis field will contain a placeholder that can be replaced with real LLM output (see `scripts/insert_hypothesis.py`).

## Case Study

The default case study uses **Non-alcoholic steatohepatitis (NASH)**. The agent proposes three testable hypotheses:

- **CYP2E1** as a liver-specific oxidative stress regulator.
- **PPARG / FASN** dual modulation to rebalance de novo lipogenesis.
- **HSD17B13** loss-of-function as a hepatoprotective mechanism.

See `报告.md` for the full technical report.

## Notes

- All external API calls include a curated fallback dataset so the agent can run offline or when APIs are unavailable.
- API keys are read from environment variables and are never stored in this repository.

## License

MIT License (for academic use only).
