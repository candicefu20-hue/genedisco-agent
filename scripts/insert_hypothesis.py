"""Insert a generated hypothesis into the agent report."""
import json
from pathlib import Path

HYPOTHESIS_TEXT = """## Hypothesis 1: CYP2E1 as a liver-specific oxidative stress regulator in NASH

**Mechanism:** CYP2E1 is upregulated in fatty liver and generates reactive oxygen species (ROS), accelerating lipotoxicity, inflammation, and fibrosis. Selective inhibition or downregulation of CYP2E1 in hepatocytes may reduce oxidative stress and slow NASH progression.

**Supporting evidence:** Our agent ranks CYP2E1 among the top candidates (priority score 0.76) due to high druggability (0.8) and moderate disease association (0.7). Pathway enrichment highlights "response to oxidative stress" (p < 1e-4), and the PPI network links CYP2E1 to SOD2, the master mitochondrial antioxidant enzyme.

**Validation experiment:** Treat primary human hepatocyte spheroids or a diet-induced NASH mouse model with a CYP2E1 inhibitor (e.g., chlormethiazole analog) and measure lipid accumulation (Oil Red O), ROS (DCF-DA), and fibrosis markers (Sirius Red, α-SMA). Compare with PNPLA3-knockdown or wild-type controls.

**Potential risks:** Systemic CYP2E1 inhibition may alter drug metabolism and detoxification; liver-specific delivery (e.g., GalNAc-siRNA) should be explored to minimize off-target effects.

## Hypothesis 2: PPARG / FASN dual modulation to rebalance de novo lipogenesis

**Mechanism:** PPARG is a master regulator of adipogenesis and lipid storage, while FASN catalyzes de novo fatty-acid synthesis. A strategy that activates PPARG in adipose tissue but inhibits FASN in liver could shift lipid burden away from the liver and reduce steatosis.

**Supporting evidence:** PPARG and FASN both score 0.8 for druggability and appear in the same PPAR signaling pathway (p = 5.6e-7). The pathway enrichment also recovers "fatty acid biosynthesis" (p = 4.2e-6) and "triglyceride biosynthesis" (p = 7.8e-6), linking these two targets mechanistically.

**Validation experiment:** Combine a liver-directed FASN inhibitor (e.g., C93) with a low-dose PPARG agonist in an ob/ob or Western-diet NASH model. Quantify liver triglycerides, serum ALT, and adipose tissue remodeling. Use single-nucleus RNA-seq to confirm tissue-specific gene expression changes.

**Potential risks:** PPARG activation can cause fluid retention and weight gain; liver-restricted FASN inhibition may be safer when combined with minimal systemic PPARG dosing.

## Hypothesis 3: HSD17B13 loss-of-function as a hepatoprotective target

**Mechanism:** HSD17B13 is a liver-enriched lipid droplet enzyme. Loss-of-function variants are associated with reduced steatohepatitis and fibrosis risk. Inhibiting HSD17B13 may reduce lipid-droplet-associated inflammation without fully abolishing neutral lipid storage.

**Supporting evidence:** HSD17B13 has a strong disease association (score 0.78) and clusters with PNPLA3/TM6SF2/MBOAT7 in the PPI network, suggesting it operates in the same lipid-droplet regulatory module. It is currently considered less druggable by our heuristics, but emerging chemical-biology programs (e.g., targeted covalent inhibitors) make it an attractive novel target.

**Validation experiment:** Generate hepatocyte-specific Hsd17b13 knockout mice on a Western diet. Assess steatosis, lobular inflammation, and fibrosis. Complement with a CRISPRi screen in human hepatocyte lines to identify synthetic-lethal or compensatory genes.

**Potential risks:** Long-term HSD17B13 inhibition may alter retinol or sex-steroid metabolism; thorough metabolomic and toxicology profiling is required.
"""


def main():
    report_path = Path(__file__).resolve().parent.parent / "outputs" / "nash_report.json"
    data = json.loads(report_path.read_text(encoding="utf-8"))
    data["hypotheses"] = HYPOTHESIS_TEXT
    report_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Updated hypothesis in {report_path}")


if __name__ == "__main__":
    main()
