from __future__ import annotations

import json
import math
import os
import re
from pathlib import Path
from typing import Any, Iterable

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parent
RESULTS = ROOT / "results"
ATTACHMENTS = ROOT / "attachments"
PROTOCOL = ROOT / "protocol"
MANUSCRIPT = ROOT / "manuscript"
FIGURES = MANUSCRIPT / "figures"
SUBMISSION = ROOT / "submission"
HCP_ROOT = ROOT / "data_hcp_ya_2025"
HCP_CONNECTOMES = ROOT / "hcp_connectomes"
BALSA_PROBE = RESULTS / "balsa_hcp_access_probe.json"

HCP_RELEASE_URL = "https://www.humanconnectome.org/study/hcp-young-adult/document/hcp-young-adult-2025-release"
TARGET_N = 200
DEV_N = 100
HOLDOUT_N = 100
PRIMARY_LAG = "4TR_2.88s"
SECONDARY_LAGS = ["1TR_0.72s", "2TR_1.44s", "7TR_5.04s"]


def ensure_dirs() -> None:
    for path in [RESULTS, ATTACHMENTS, PROTOCOL, MANUSCRIPT, FIGURES, SUBMISSION, HCP_ROOT, HCP_CONNECTOMES]:
        path.mkdir(parents=True, exist_ok=True)


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_csv(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    pd.DataFrame(list(rows)).to_csv(path, index=False)


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(WORKSPACE))
    except ValueError:
        return str(path)


def all_files(root: Path) -> list[Path]:
    if not root.exists():
        return []
    return [p for p in root.rglob("*") if p.is_file()]


def subject_from_path(path: Path) -> str | None:
    parts = [p for p in path.parts]
    for part in parts:
        if re.fullmatch(r"\d{6}", part):
            return part
        match = re.fullmatch(r"sub-([A-Za-z0-9]+)", part)
        if match:
            return match.group(1)
    return None


def classify_hcp_file(path: Path) -> set[str]:
    text = str(path).replace("\\", "/").lower()
    name = path.name.lower()
    kinds: set[str] = set()
    if "t1w" in text or "t2w" in text:
        kinds.add("t1_t2")
    if "/diffusion/" in text or "diffusion" in text or "bedpostx" in text or "dwi" in text:
        kinds.add("dwi")
    if name in {"bvals", "bvecs"} or name.endswith(".bval") or name.endswith(".bvec"):
        kinds.add("dwi_vectors")
    if "eddy" in text and ("qc" in text or "eddy" in name):
        kinds.add("eddy_qc")
    if "bedpostx" in text:
        kinds.add("bedpostx")
    if "tfmri_wm_lr" in text:
        kinds.add("wm_lr")
    if "tfmri_wm_rl" in text:
        kinds.add("wm_rl")
    if name == "movement_regressors.txt" or "movement_regressors" in name:
        kinds.add("movement")
    if "wm" in text and ("evs" in text or "eprime" in text or "event" in text):
        kinds.add("wm_events")
    return kinds


def e0_dataset_cohort_lock() -> dict[str, Any]:
    files = all_files(HCP_ROOT)
    by_subject: dict[str, dict[str, Any]] = {}
    for path in files:
        subject = subject_from_path(path)
        if not subject:
            continue
        row = by_subject.setdefault(
            subject,
            {
                "subject": subject,
                "has_t1_t2": False,
                "has_dwi": False,
                "has_bvals_bvecs": False,
                "has_eddy_qc": False,
                "has_bedpostx": False,
                "has_wm_lr": False,
                "has_wm_rl": False,
                "has_movement_regressors": False,
                "has_wm_events": False,
                "n_files": 0,
            },
        )
        row["n_files"] += 1
        kinds = classify_hcp_file(path)
        row["has_t1_t2"] = row["has_t1_t2"] or "t1_t2" in kinds
        row["has_dwi"] = row["has_dwi"] or "dwi" in kinds
        row["has_bvals_bvecs"] = row["has_bvals_bvecs"] or "dwi_vectors" in kinds
        row["has_eddy_qc"] = row["has_eddy_qc"] or "eddy_qc" in kinds
        row["has_bedpostx"] = row["has_bedpostx"] or "bedpostx" in kinds
        row["has_wm_lr"] = row["has_wm_lr"] or "wm_lr" in kinds
        row["has_wm_rl"] = row["has_wm_rl"] or "wm_rl" in kinds
        row["has_movement_regressors"] = row["has_movement_regressors"] or "movement" in kinds
        row["has_wm_events"] = row["has_wm_events"] or "wm_events" in kinds

    rows = sorted(by_subject.values(), key=lambda r: r["subject"])
    for row in rows:
        row["complete_for_p5"] = all(
            [
                row["has_t1_t2"],
                row["has_dwi"],
                row["has_bvals_bvecs"],
                row["has_wm_lr"],
                row["has_wm_rl"],
                row["has_movement_regressors"],
            ]
        )

    complete = [row for row in rows if row["complete_for_p5"]]
    for idx, row in enumerate(complete):
        row["split"] = "development" if idx < DEV_N else "locked_holdout" if idx < TARGET_N else "unused_extra"
    for row in rows:
        row.setdefault("split", "not_eligible")

    if not rows:
        rows = [
            {
                "subject": "NO_HCP_YA_2025_FILES_FOUND",
                "has_t1_t2": False,
                "has_dwi": False,
                "has_bvals_bvecs": False,
                "has_eddy_qc": False,
                "has_bedpostx": False,
                "has_wm_lr": False,
                "has_wm_rl": False,
                "has_movement_regressors": False,
                "has_wm_events": False,
                "n_files": 0,
                "complete_for_p5": False,
                "split": "not_eligible",
            }
        ]

    write_csv(RESULTS / "e0_hcp_cohort_lock.csv", rows)
    payload = {
        "experiment": "P5-E0",
        "status": "READY_FOR_HCP_ANALYSIS" if len(complete) >= TARGET_N else "HCP_YA_2025_DATA_NOT_AVAILABLE_LOCALLY",
        "hcp_root": rel(HCP_ROOT),
        "target_n": TARGET_N,
        "development_n": DEV_N,
        "locked_holdout_n": HOLDOUT_N,
        "n_subjects_detected": len(by_subject),
        "n_complete_subjects": len(complete),
        "release_rule": "Use HCP-YA 2025 only; do not mix with S1200.",
        "official_release_url": HCP_RELEASE_URL,
        "required_modalities": [
            "T1w/T2w anatomy",
            "preprocessed dMRI",
            "bvals/bvecs",
            "WM LR/RL task-fMRI",
            "Movement_Regressors.txt",
            "WM event/E-Prime timing",
        ],
    }
    write_json(RESULTS / "e0_hcp_cohort_lock.json", payload)
    return payload


def e1_structural_connectome_gate(e0: dict[str, Any]) -> dict[str, Any]:
    files = all_files(HCP_CONNECTOMES)
    accepted = [
        p
        for p in files
        if p.suffix.lower() in {".csv", ".tsv", ".npy", ".npz", ".json", ".mat"}
        and ("connectome" in str(p).lower() or "schaefer" in str(p).lower() or "matrix" in str(p).lower())
    ]
    rows = [
        {"file": rel(p), "suffix": p.suffix, "size_bytes": p.stat().st_size, "accepted_candidate": p in accepted}
        for p in files
    ] or [{"file": "NO_HCP_CONNECTOME_FILES_FOUND", "suffix": "NA", "size_bytes": 0, "accepted_candidate": False}]
    write_csv(RESULTS / "e1_hcp_structural_connectome_inventory.csv", rows)
    payload = {
        "experiment": "P5-E1",
        "status": "READY_CONNECTOMES_FOUND" if accepted and e0["status"] == "READY_FOR_HCP_ANALYSIS" else "BLOCKED_HCP_CONNECTOMES_NOT_AVAILABLE",
        "connectome_dir": rel(HCP_CONNECTOMES),
        "n_candidate_files": len(accepted),
        "frozen_tractography": "HCP preprocessed dMRI -> MSMT-CSD -> ACT -> iFOD2 -> SIFT2 -> Schaefer-200+subcortex matrix",
        "primary_edge_weight": "SIFT2-weighted connectivity",
        "sensitivity_edge_weights": ["FA", "streamline_count"],
        "claim_boundary": "No subject-level structural constraint can be tested until connectome matrices are present or generated.",
    }
    write_json(RESULTS / "e1_hcp_structural_connectome_gate.json", payload)
    return payload


def blocked(name: str, reason: str, out_name: str) -> dict[str, Any]:
    payload = {
        "experiment": name,
        "status": "BLOCKED_HCP_YA_2025_INPUTS_MISSING",
        "reason": reason,
        "claim_boundary": "This experiment is specified and implemented as a gate, but no scientific result is reported.",
    }
    write_json(RESULTS / out_name, payload)
    return payload


def e8_claim_audit(e0: dict[str, Any], e1: dict[str, Any]) -> dict[str, Any]:
    ready = e0["status"] == "READY_FOR_HCP_ANALYSIS" and e1["status"] == "READY_CONNECTOMES_FOUND"
    balsa_probe = json.loads(BALSA_PROBE.read_text(encoding="utf-8")) if BALSA_PROBE.exists() else {}
    payload = {
        "experiment": "P5-E8",
        "status": "P5_HCP_READY_TO_RUN" if ready else "P5_HCP_YA_2025_DATA_NOT_AVAILABLE_LOCALLY",
        "paper5_primary_dataset": "HCP-YA 2025",
        "phase0_openneuro_status": "ARCHIVED_AS_FEASIBILITY_AUDIT_NOT_PRIMARY_P5",
        "balsa_access_status": balsa_probe.get("status", "NOT_PROBED_THIS_RUN"),
        "balsa_login_to_agree_detected": balsa_probe.get("login_to_agree_detected", None),
        "claim_allowed_structure_matters": False,
        "claim_allowed_individual_structure_matters": False,
        "claim_allowed_anatomical_specificity": False,
        "claim_allowed_locked_replication": False,
        "claim_allowed_cwp_validated": False,
        "required_before_claims": [
            "200 eligible HCP-YA 2025 subjects locked into 100 development and 100 final holdout",
            "subject-level structural connectomes aligned to the fMRI state atlas",
            "E2 fMRI state extraction with measured motion residualization",
            "M1/M2/M3 and structural falsification comparisons",
            "subject-level final holdout statistics",
        ],
        "no_invented_results": True,
    }
    write_json(RESULTS / "e8_hcp_claim_audit.json", payload)
    write_json(RESULTS / "e8_claim_audit.json", payload)
    return payload


def table_markdown(path: Path, max_rows: int = 20) -> str:
    try:
        df = pd.read_csv(path)
    except pd.errors.EmptyDataError:
        return "| status |\n| --- |\n| EMPTY_TABLE |"
    if len(df) > max_rows:
        df = df.head(max_rows)
    cols = list(df.columns)

    def cell(value: Any) -> str:
        if isinstance(value, float) and math.isnan(value):
            return ""
        text = str(value)
        if len(text) > 140:
            text = text[:137] + "..."
        return text.replace("|", "\\|").replace("\n", " ")

    lines = ["| " + " | ".join(cell(c) for c in cols) + " |", "| " + " | ".join("---" for _ in cols) + " |"]
    for _, row in df.iterrows():
        lines.append("| " + " | ".join(cell(row[c]) for c in cols) + " |")
    return "\n".join(lines)


def write_protocol() -> None:
    (PROTOCOL / "PAPER5_HCP_YA_2025_FROZEN_PROTOCOL_v1.md").write_text(
        f"""# Paper 5 HCP-YA 2025 Frozen Protocol v1

Title: Individual Structural Connectomes as Predictive Constraints on Macroscopic Task-State Transitions

## Central Model

```text
G_i + S_t + X_t -> S_(t+tau)
```

`G_i` is a diffusion-derived subject-level structural connectome. `S_t` and `S_(t+tau)` are macroscopic brain states extracted from HCP-YA 2025 Working Memory task-fMRI. `X_t` contains 0/2-back, stimulus category, block position, run, measured motion, and time covariates.

## Dataset Lock

Use HCP-Young Adult 2025 only. Do not mix HCP-YA 2025 processing with the 2017 S1200 release.

Official release page: {HCP_RELEASE_URL}

Target cohort:

```text
N = 200 eligible subjects
100 development subjects
100 locked final holdout subjects
```

Eligibility requires T1w/T2w anatomy, preprocessed dMRI with bvals/bvecs, WM LR/RL task-fMRI, movement files, and WM event timing.

## E0-E8

E0 - Dataset / cohort lock.
E1 - Build subject structural connectome G_i using Schaefer-200 + subcortex, MSMT-CSD, ACT, iFOD2, SIFT2.
E2 - Extract WM task-fMRI brain states in the same atlas and residualize measured motion, run drift, and nuisance terms.
E3 - Strong no-structure baseline: S_(t+tau) = F(S_t, X_t).
E4 - Structural models using group mean and true G_i S_t.
E5 - Structural falsification: swapped, randomized, and distance-only graphs.
E6 - Subject-specificity rank test.
E7 - Locked holdout statistics.
E8 - Claim audit and one-command reproduction.

## Lags

Primary: {PRIMARY_LAG}

Secondary: {", ".join(SECONDARY_LAGS)}

## Gates

Gate A: M3 > M1, structure matters.
Gate B: M3 > M2, individual structure matters.
Gate C: M3 > swapped/random/distance, anatomical specificity.
Gate D: gates replicate in locked final holdout.
""",
        encoding="utf-8",
    )
    (HCP_ROOT / "README.md").write_text(
        """# HCP-YA 2025 Local Data Root

Place authorized HCP-YA 2025 packages here after logging into BALSA/ConnectomeDB and agreeing to the applicable Data Use Terms.

Expected subject-level contents:

```text
T1w/T2w anatomy
preprocessed dMRI / Diffusion
bvals and bvecs
tfMRI_WM_LR
tfMRI_WM_RL
Movement_Regressors.txt
WM event or E-Prime timing files
```

Do not place older S1200 processed data here.
""",
        encoding="utf-8",
    )
    (HCP_CONNECTOMES / "README.md").write_text(
        """# HCP-YA 2025 Subject-Level Connectomes

Place generated or authorized subject-level structural connectome matrices here.

Expected primary matrix:

```text
subject x Schaefer-200+subcortex parcel-by-parcel SIFT2-weighted connectivity
```

Acceptable inventory file types:

```text
.csv .tsv .npy .npz .json .mat
```

The matrix atlas must match the fMRI state extraction atlas.
""",
        encoding="utf-8",
    )


def write_current_results(audit: dict[str, Any]) -> None:
    text = f"""# Paper 5 Current Results

Status:

```text
{audit["status"]}
```

Paper 5 has been switched to HCP-YA 2025 as the primary dataset. No structural-connectome scientific result has been run yet because the required HCP-YA 2025 packages are not present locally.

## BALSA / ConnectomeDB Access Probe

```json
{json.dumps(json.loads(BALSA_PROBE.read_text(encoding="utf-8")), indent=2) if BALSA_PROBE.exists() else "NOT_PROBED_THIS_RUN"}
```

## E0 HCP Cohort Lock

{table_markdown(RESULTS / "e0_hcp_cohort_lock.csv")}

## E1 Structural Connectome Inventory

{table_markdown(RESULTS / "e1_hcp_structural_connectome_inventory.csv")}

## E2-E7 Status

```text
E2 fMRI state extraction: blocked until HCP-YA 2025 WM data are local.
E3 no-structure baseline: blocked until E2.
E4 structural models: blocked until E1 and E2.
E5 structural falsification: blocked until E4.
E6 subject-specificity rank test: blocked until E4.
E7 locked holdout statistics: blocked until E4-E6.
```

## Claim Audit

```json
{json.dumps(audit, indent=2)}
```
"""
    (RESULTS / "CURRENT_RESULTS.md").write_text(text, encoding="utf-8")


def make_figures() -> None:
    os.environ.setdefault("MPLCONFIGDIR", str(ROOT / ".matplotlib"))
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    e0 = json.loads((RESULTS / "e0_hcp_cohort_lock.json").read_text(encoding="utf-8"))
    labels = ["Detected", "Complete", "Target"]
    vals = [e0["n_subjects_detected"], e0["n_complete_subjects"], e0["target_n"]]
    fig, ax = plt.subplots(figsize=(6.8, 4.0))
    ax.bar(labels, vals, color=["#4d7c8a", "#70a37f", "#c44536"])
    ax.set_title("E0 HCP-YA 2025 Cohort Availability")
    ax.set_ylabel("Subjects")
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(FIGURES / "figure_1_hcp_cohort_gate.png", dpi=180)
    fig.savefig(FIGURES / "figure_1_hcp_cohort_gate.pdf")
    plt.close(fig)

    gates = ["A\nM3>M1", "B\nM3>M2", "C\nNulls", "D\nHoldout"]
    vals = [0, 0, 0, 0]
    fig, ax = plt.subplots(figsize=(6.8, 4.0))
    ax.bar(gates, vals, color="#c44536")
    ax.set_ylim(0, 1)
    ax.set_title("Paper 5 Claim Gates Not Yet Tested")
    ax.set_ylabel("Gate passed")
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(FIGURES / "figure_2_hcp_claim_gates.png", dpi=180)
    fig.savefig(FIGURES / "figure_2_hcp_claim_gates.pdf")
    plt.close(fig)


def write_attachments(audit: dict[str, Any]) -> None:
    (ATTACHMENTS / "A1_Frozen_Protocol.md").write_text((PROTOCOL / "PAPER5_HCP_YA_2025_FROZEN_PROTOCOL_v1.md").read_text(encoding="utf-8"), encoding="utf-8")
    (ATTACHMENTS / "A2_Dataset_Manifest.md").write_text("# A2 Dataset Manifest\n\n" + table_markdown(RESULTS / "e0_hcp_cohort_lock.csv") + "\n", encoding="utf-8")
    (ATTACHMENTS / "A3_Full_Pipeline.md").write_text(
        """# A3 Full Pipeline

```text
HCP-YA 2025 cohort lock
-> structural connectome construction or inventory
-> WM task-fMRI state extraction
-> measured-motion residualization
-> M1 no-structure baseline
-> M2 group-mean structural model
-> M3 individual G_i model
-> swapped/random/distance nulls
-> subject-specificity rank test
-> locked final holdout statistics
-> claim audit
```
""",
        encoding="utf-8",
    )
    (ATTACHMENTS / "A4_Full_Baseline_Results.md").write_text("# A4 Full Baseline Results\n\n[NOT YET RUN] HCP-YA 2025 inputs are not local.\n", encoding="utf-8")
    (ATTACHMENTS / "A5_Holdout_Audit.md").write_text("# A5 Holdout Audit\n\nTarget split: 100 development subjects and 100 locked final holdout subjects. Current status: [NOT YET RUN].\n", encoding="utf-8")
    (ATTACHMENTS / "A6_Statistics.md").write_text("# A6 Statistics\n\nPrimary subject-level statistic: paired delta MSE_i = MSE(M1) - MSE(M3), with sign-flip permutation, bootstrap 95% CI, effect size, and FDR for secondary analyses. Current status: [NOT YET RUN].\n", encoding="utf-8")
    (ATTACHMENTS / "A7_Null_Falsification_Tests.md").write_text("# A7 Null / Falsification Tests\n\nPlanned: subject-connectome swap, group-mean connectome, edge-shuffled graph, degree/weight-matched random graph, and distance-only graph. Current status: [NOT YET RUN].\n", encoding="utf-8")
    (ATTACHMENTS / "A8_QC_Leakage_Audit.md").write_text("# A8 QC & Leakage Audit\n\nLeakage controls: subject-disjoint development/final split, frozen atlas, frozen lag, frozen regularization rules, measured motion residualization, and no S1200/2025 mixing. Current status: [NOT YET RUN].\n", encoding="utf-8")
    (ATTACHMENTS / "A9_Limitations_Failed_Analyses.md").write_text(
        f"""# A9 Limitations & Failed Analyses

Current limitation:

```text
{audit["status"]}
```

No claim is made that structure matters, individual structure matters, anatomical specificity holds, or locked replication succeeded.
""",
        encoding="utf-8",
    )
    (ATTACHMENTS / "A10_One_Command_Reproduction.md").write_text(
        """# A10 One-command Reproduction

Run:

```powershell
powershell -ExecutionPolicy Bypass -File paper5\\scripts\\reproduce-paper5.ps1
```

The command audits local HCP-YA 2025 inputs and either runs the ready gates or reports the exact missing inputs.

Optional access probe:

```powershell
powershell -ExecutionPolicy Bypass -File paper5\\scripts\\reproduce-paper5-balsa-access-probe.ps1
```
""",
        encoding="utf-8",
    )


def manuscript_text(audit: dict[str, Any]) -> str:
    return f"""# Individual Structural Connectomes as Predictive Constraints on Macroscopic Task-State Transitions

Authors: [TO BE FILLED]  
Affiliations: [TO BE FILLED]  
Correspondence: [TO BE FILLED]

## Abstract

This Paper 5 protocol tests whether diffusion-derived individual structural connectomes provide additional predictive constraint on macroscopic task-fMRI brain-state transitions. The primary model is `G_i + S_t + X_t -> S_(t+tau)`, evaluated in HCP-YA 2025 Working Memory task-fMRI and diffusion data. The central comparison is `P(S_(t+tau) | S_t, X_t, G_i) > P(S_(t+tau) | S_t, X_t)`. The analysis is frozen around a 200-subject HCP-YA 2025 cohort, with 100 development subjects and 100 locked final-holdout subjects. Current status is `{audit["status"]}`; BALSA access probe status is `{audit.get("balsa_access_status", "NOT_PROBED_THIS_RUN")}`. The HCP structural hypothesis has not yet been tested because the required HCP-YA 2025 data packages are not available locally.

## 1. Introduction

Papers 3 and 4 established reproducible macroscopic stage-transition signals and tested several falsification routes. Paper 5 no longer tries to validate CWP itself. It asks a narrower biological question: whether anatomical wiring constrains which future macroscopic state follows a current task-state.

## 2. Methods

### 2.1 Dataset

The primary dataset is HCP-YA 2025. HCP-YA 2025 must not be mixed with older S1200 processing.

### 2.2 Cohort Lock

Target cohort: 200 eligible subjects, split into 100 development subjects and 100 locked final-holdout subjects. Eligibility requires T1w/T2w anatomy, dMRI, bvals/bvecs, WM LR/RL task-fMRI, movement regressors, and task event timing.

### 2.3 Structural Connectome

The frozen structural pipeline is HCP preprocessed dMRI -> MSMT-CSD -> ACT -> iFOD2 probabilistic tractography -> SIFT2 -> Schaefer-200 + subcortex parcel-by-parcel structural matrix. Primary edge weight is SIFT2-weighted connectivity. FA and streamline count are sensitivity analyses.

### 2.4 fMRI Brain States

Brain states are extracted from HCP Working Memory LR/RL runs using the same atlas as `G_i`. `X_t` includes 0/2-back, stimulus category, block position, run, motion, and time terms. Primary lag is {PRIMARY_LAG}; secondary lags are {", ".join(SECONDARY_LAGS)}.

### 2.5 Models

M1: `S_(t+tau) = F(S_t, X_t)`.

M2: `S_(t+tau) = F(S_t, X_t, group_mean_G S_t)`.

M3: `S_(t+tau) = F(S_t, X_t, G_i S_t)`.

### 2.6 Falsification

Structural nulls are swapped-subject connectomes, group-mean connectome, degree/weight-matched random graphs, edge-shuffled graphs, and distance-only graphs.

## 3. Current Results

### 3.1 E0 HCP Cohort Gate

{table_markdown(RESULTS / "e0_hcp_cohort_lock.csv")}

### 3.2 E1 Structural Connectome Gate

{table_markdown(RESULTS / "e1_hcp_structural_connectome_inventory.csv")}

### 3.3 E2-E7

E2-E7 are specified but not run because HCP-YA 2025 inputs are not local.

## 4. Claim Gates

Gate A: M3 > M1. Gate B: M3 > M2. Gate C: M3 > swapped/random/distance nulls. Gate D: all prior gates hold in the locked final-holdout subjects.

Current status: none of these gates has been tested.

## 5. Conclusion

Paper 5 has been redefined as an HCP-YA 2025 structural-connectome constraint study. The implementation package and frozen protocol are in place. The scientific hypothesis remains untested until HCP-YA 2025 task-fMRI and diffusion/connectome inputs are available locally.

## Data Availability

HCP-YA 2025 data require authorized access through the HCP/ConnectomeDB/BALSA distribution path. No HCP data are redistributed here.

## Code Availability

[TO BE FILLED]

## Ethics Statement

This planned analysis uses public controlled-access/de-identified HCP data under the applicable HCP data-use terms.

## Conflicts of Interest

[TO BE FILLED]

## Claim Audit

```json
{json.dumps(audit, indent=2)}
```
"""


def build_pdf(markdown_text: str) -> None:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

    doc = SimpleDocTemplate(str(SUBMISSION / "PAPER5_BIORXIV_DRAFT_CURRENT.pdf"), pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    in_fence = False
    for line in markdown_text.splitlines():
        stripped = line.strip()
        if stripped.startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence and not stripped:
            continue
        if not stripped:
            story.append(Spacer(1, 8))
            continue
        style = styles["Heading1"] if stripped.startswith("# ") else styles["Heading2"] if stripped.startswith("## ") or stripped.startswith("### ") else styles["BodyText"]
        clean = stripped.lstrip("#").strip()
        safe = clean.replace("`", "").replace("\\_", "_").replace("\\", "")
        safe = safe.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        story.append(Paragraph(safe, style))
    doc.build(story)


def write_submission(audit: dict[str, Any]) -> None:
    text = manuscript_text(audit)
    (MANUSCRIPT / "PAPER5_MANUSCRIPT_CURRENT.md").write_text(text, encoding="utf-8")
    build_pdf(text)
    (SUBMISSION / "SUBMISSION_READINESS.md").write_text(
        f"""# Paper 5 Submission Readiness

Current status:

```text
{audit["status"]}
```

This is not ready as a results preprint. It is ready as a frozen HCP-YA 2025 protocol package.

Required before a results manuscript:

```text
Log into BALSA/ConnectomeDB and agree to the WU-Minn HCP Consortium Open Access Data Use Terms.
Place authorized HCP-YA 2025 data under paper5/data_hcp_ya_2025.
Place or generate subject-level connectomes under paper5/hcp_connectomes.
Run E2-E7 and regenerate E8 claim audit.
Add literature review, citations, authors, affiliations, funding, COI, and code URL.
```
""",
        encoding="utf-8",
    )
    (SUBMISSION / "FIGURE_CAPTIONS.md").write_text(
        """# Figure Captions

Figure 1. Local HCP-YA 2025 cohort availability against the N=200 target.

Figure 2. Paper 5 claim gates. All gates are currently untested.
""",
        encoding="utf-8",
    )


def main() -> None:
    ensure_dirs()
    write_protocol()
    e0 = e0_dataset_cohort_lock()
    e1 = e1_structural_connectome_gate(e0)
    blocked("P5-E2", "HCP-YA 2025 WM task-fMRI and movement/event files are not available locally.", "e2_hcp_fmri_state_extraction.json")
    blocked("P5-E3", "No-structure baseline requires E2 state extraction outputs.", "e3_hcp_no_structure_baseline.json")
    blocked("P5-E4", "Structural models require E1 connectomes and E2 state extraction outputs.", "e4_hcp_structural_models.json")
    blocked("P5-E5", "Structural falsification requires E4 model outputs.", "e5_hcp_structural_falsification.json")
    blocked("P5-E6", "Subject-specificity rank test requires E4 model outputs.", "e6_hcp_subject_specificity.json")
    blocked("P5-E7", "Locked holdout statistics require E4-E6 outputs.", "e7_hcp_locked_holdout_statistics.json")
    audit = e8_claim_audit(e0, e1)
    write_json(RESULTS / "e0_e8_hcp_run_summary.json", {"experiment": "P5-HCP-E0-E8", "status": audit["status"], "claim_audit": audit})
    write_current_results(audit)
    make_figures()
    write_attachments(audit)
    write_submission(audit)
    print(json.dumps(audit, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
