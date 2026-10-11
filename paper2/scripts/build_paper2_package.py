from __future__ import annotations

import json
import os
from pathlib import Path

import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
MANUSCRIPT = ROOT / "manuscript"
FIGURES = MANUSCRIPT / "figures"
SUBMISSION = ROOT / "submission"
os.environ.setdefault("MPLCONFIGDIR", str(ROOT / ".matplotlib"))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


def ensure_dirs() -> None:
    for path in [MANUSCRIPT, FIGURES, SUBMISSION]:
        path.mkdir(parents=True, exist_ok=True)


def save_bar(path_stem: Path, labels: list[str], values: list[float], title: str, ylabel: str) -> None:
    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    colors = ["#4C78A8", "#F58518", "#54A24B", "#B279A2", "#E45756"][: len(labels)]
    ax.bar(labels, values, color=colors)
    ax.set_title(title)
    ax.set_ylabel(ylabel)
    ax.tick_params(axis="x", rotation=20)
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(path_stem.with_suffix(".png"), dpi=180)
    fig.savefig(path_stem.with_suffix(".pdf"))
    plt.close(fig)


def make_figures() -> None:
    primary = pd.read_csv(RESULTS / "paper2_primary_metrics.csv")
    e97 = pd.read_csv(RESULTS / "e9_7_dataset_c_model_comparison.csv")
    attribution = pd.read_csv(RESULTS / "e9_5_failure_attribution.csv")
    subject = pd.read_csv(RESULTS / "e9_7_dataset_c_subject_effects.csv")

    e90 = primary[(primary["experiment"] == "E9.0") & (primary["variant"] == "raw_failure_reproduction")]
    save_bar(
        FIGURES / "figure_1_failure_reproduction",
        e90["model"].tolist(),
        e90["mse"].astype(float).tolist(),
        "E9.0 A -> B Failure Reproduction",
        "MSE",
    )

    top = attribution.head(6)
    save_bar(
        FIGURES / "figure_2_failure_attribution",
        top["variant"].tolist(),
        top["gap_reduction_vs_raw"].astype(float).tolist(),
        "E9.5 Diagnostic Gap Reduction",
        "CWP-vs-Task Gap Reduction",
    )

    save_bar(
        FIGURES / "figure_3_dataset_c_final_holdout",
        e97["model"].tolist(),
        e97["mse"].astype(float).tolist(),
        "E9.7 Dataset C Final Holdout",
        "MSE",
    )

    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    ax.hist(subject["cwp_v2_minus_strong_task_mse"].astype(float), bins=24, color="#4C78A8", alpha=0.85)
    ax.axvline(0, color="#222222", linewidth=1.5)
    ax.set_title("Dataset C Subject-Level Heterogeneity")
    ax.set_xlabel("CWP_v2_medium MSE - StrongTask MSE")
    ax.set_ylabel("Subjects")
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(FIGURES / "figure_4_subject_heterogeneity.png", dpi=180)
    fig.savefig(FIGURES / "figure_4_subject_heterogeneity.pdf")
    plt.close(fig)


def manuscript_text() -> str:
    e90 = json.loads((RESULTS / "e9_0_failure_reproduction_summary.json").read_text(encoding="utf-8"))
    e96 = json.loads((RESULTS / "e9_6_frozen_v2_candidate.json").read_text(encoding="utf-8"))
    e97 = json.loads((RESULTS / "e9_7_dataset_c_holdout_summary.json").read_text(encoding="utf-8"))
    e98 = json.loads((RESULTS / "e9_8_claim_audit.json").read_text(encoding="utf-8"))

    return f"""# Cross-Dataset Failure and Generalization of CWP-style Brain-State Models

Authors: [TO BE FILLED]  
Affiliations: [TO BE FILLED]  
Correspondence: [TO BE FILLED]

## Abstract

Paper 1 found within-dataset out-of-distribution signal for CWP-style compositional representations, but failed external validation from OpenNeuro ds001635 to ds001634. Here we treat that failure as the object of study. We reproduced the A-to-B failure, decomposed candidate sources across measurement scaling, state representation, task context, and ontology granularity, froze an A/B-derived v2 candidate, and evaluated it once on a newly selected Dataset C, OpenNeuro ds004469 v1.1.3. The A/B diagnostics identified plausible measurement, state-representation, and ontology candidates, but also revealed null risk because random ontology structure could reduce the CWP-vs-task gap. On Dataset C, CWP_v2_medium beat RandomOntology but did not beat the StrongTask baseline. The current evidence therefore does not support CWP-specific cross-dataset generalization or a rescue of the CWP strong hypothesis.

## 1. Introduction

The central question is why a CWP-style representation can show local compositional advantage but fail across independent datasets. This manuscript does not reinterpret Paper 1 as successful. Dataset B is treated as a failure-analysis dataset, while Dataset C is the final external holdout.

The sharpened question is whether semantic ontology matters beyond generic compositional structure. If a pseudo ontology performs similarly, any improvement may reflect compression, regularization, or representation geometry rather than CWP-specific cognitive semantics.

## 2. Methods

Dataset A was OpenNeuro ds001635. Dataset B was OpenNeuro ds001634 and was used only for failure analysis because its external failure was already observed in Paper 1. Dataset C was locked as OpenNeuro ds004469 v1.1.3 after metadata/event audit. Its Sternberg task events were mapped as Coding to ENCODE, Retention to MAINTAIN, and Test to PROBE. Dataset C does not test TRANSFORM.

All models predicted next brain state from current brain state and categorical descriptors. The main comparison included M2 StrongTask, M3 CWP v1, CWP_v2_medium, and RandomOntology. The CWP-specific success rule required CWP_v2_medium to beat both StrongTask and RandomOntology on Dataset C.

## 3. Results

### 3.1 Failure Reproduction

Paper 1 external failure was reproduced:

```text
M2_strong_task MSE: {e90["m2_mse"]}
M3_cwp MSE: {e90["m3_mse"]}
status: {e90["status"]}
```

### 3.2 A/B Diagnostic Candidate

The frozen v2 candidate was:

```text
selected_factor_family: {e96["selected_factor_family"]}
selected_variant: {e96["selected_variant"]}
status: {e96["status"]}
null_risk: {e96["null_risk"]}
```

This is diagnostic only, not independent replication.

### 3.3 Dataset C Final Holdout

Dataset C produced 2,268 stage states and {e97["n_dataset_c_transitions"]} transitions. Final comparison:

```text
M2_strong_task MSE: {e97["strong_task_mse"]}
M3_cwp v1 MSE: {e97["cwp_v1_mse"]}
CWP_v2_medium MSE: {e97["cwp_v2_medium_mse"]}
RandomOntology MSE: {e97["random_ontology_mse"]}
```

CWP_v2_medium beat RandomOntology: {e97["cwp_v2_beats_random_ontology"]}.  
CWP_v2_medium beat M2_strong_task: {e97["cwp_v2_beats_strong_task"]}.  
Final status: {e97["status"]}.

Subject-level effects were heterogeneous: CWP_v2_medium beat StrongTask for {e97["subjects_cwp_v2_better_than_strong_task"]}/{e97["n_dataset_c_subjects_with_transitions"]} subjects, but aggregate MSE was worse than StrongTask.

## 4. Discussion

The evidence supports a constrained failure-analysis story. Measurement scaling, state representation, and ontology granularity can reduce the A/B CWP-vs-task gap, but the Dataset C final holdout does not support a CWP-specific rescue. The strongest allowed interpretation is that compositional structure may sometimes help transfer, but the current semantic CWP ontology is not validated as a dataset-invariant neural primitive.

The negative result is scientifically useful because it prevents conflating local OOD advantage with general cognitive primitives. Future work should treat v3 ontology or alignment changes as exploratory until tested on a new clean holdout.

## 5. Conclusion

Paper 2 reproduces the Paper 1 external failure, identifies plausible diagnostic mechanisms, and rejects the current CWP-specific cross-dataset generalization claim on Dataset C.

## Data Availability

OpenNeuro ds001635, ds001634, and ds004469 were used. Dataset C DOI: doi:10.18112/openneuro.ds004469.v1.1.3.

## Code Availability

[TO BE FILLED]

## Ethics Statement

This study uses public de-identified datasets. Dataset-specific ethics statements are reported by the original data providers.

## Conflicts of Interest

[TO BE FILLED]

## Claim Audit

```json
{json.dumps(e98, indent=2)}
```
"""


def build_pdf(markdown_text: str) -> None:
    doc = SimpleDocTemplate(str(SUBMISSION / "PAPER2_BIORXIV_DRAFT_CURRENT.pdf"), pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    for line in markdown_text.splitlines():
        stripped = line.strip()
        if not stripped:
            story.append(Spacer(1, 8))
            continue
        style = styles["Heading1"] if stripped.startswith("# ") else styles["Heading2"] if stripped.startswith("## ") else styles["BodyText"]
        clean = stripped.lstrip("#").strip()
        story.append(Paragraph(clean.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"), style))
    doc.build(story)


def main() -> None:
    ensure_dirs()
    make_figures()
    text = manuscript_text()
    (MANUSCRIPT / "PAPER2_MANUSCRIPT_CURRENT.md").write_text(text, encoding="utf-8")
    build_pdf(text)


if __name__ == "__main__":
    main()
