from __future__ import annotations

import json
import math
import os
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable, Sequence

import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parent
PAPER1 = WORKSPACE / "paper1"
sys.path.insert(0, str(PAPER1 / "scripts"))

from common import build_transitions, load_stage_states  # noqa: E402


RESULTS = ROOT / "results"
ATTACHMENTS = ROOT / "attachments"
PROTOCOL = ROOT / "protocol"
MANUSCRIPT = ROOT / "manuscript"
FIGURES = MANUSCRIPT / "figures"
SUBMISSION = ROOT / "submission"
STRUCTURAL = ROOT / "structural_connectomes"
ONLINE_AUDIT = ROOT / "online_structural_audit" / "openneuro_structural_metadata_audit.json"
HCP_RELEASE_URL = "https://www.humanconnectome.org/study/hcp-young-adult/document/hcp-young-adult-2025-release"

DATASETS = {
    "ds001635": {
        "states": WORKSPACE / "paper1" / "state_extraction" / "stage_states.csv",
        "raw": WORKSPACE / "paper1" / "data_raw" / "ds001635",
    },
    "ds001634": {
        "states": WORKSPACE / "paper1" / "external_validation" / "stage_states_external.csv",
        "raw": WORKSPACE / "paper1" / "data_raw" / "ds001634",
    },
    "ds004469": {
        "states": WORKSPACE / "paper2" / "external_holdout" / "stage_states_dataset_c.csv",
        "raw": WORKSPACE / "paper2" / "external_holdout" / "ds004469_final_input",
    },
}

PRIMARY_TRANSITIONS = ["ENCODE_TO_MAINTAIN", "MAINTAIN_TO_PROBE"]


def ensure_dirs() -> None:
    for path in [RESULTS, ATTACHMENTS, PROTOCOL, MANUSCRIPT, FIGURES, SUBMISSION, STRUCTURAL]:
        path.mkdir(parents=True, exist_ok=True)


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_csv(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(list(rows)).to_csv(path, index=False)


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(WORKSPACE))
    except ValueError:
        return str(path)


def count_files(root: Path, patterns: Sequence[str]) -> int:
    if not root.exists():
        return 0
    files: set[Path] = set()
    for pattern in patterns:
        files.update(p for p in root.rglob(pattern) if p.is_file())
    return len(files)


def load_online_audit() -> dict[str, dict[str, Any]]:
    if not ONLINE_AUDIT.exists():
        return {}
    rows = json.loads(ONLINE_AUDIT.read_text(encoding="utf-8"))
    return {str(row.get("dataset")): row for row in rows}


def e1_modality_audit() -> dict[str, Any]:
    online = load_online_audit()
    rows: list[dict[str, Any]] = []
    for dataset, spec in DATASETS.items():
        raw = spec["raw"]
        states = spec["states"]
        online_row = online.get(dataset, {})
        online_counts = online_row.get("structural_candidate_counts_by_type", {}) or {}
        local_anat = count_files(raw, ["*T1w.nii.gz", "*T2w.nii.gz", "*T1w.json", "*T2w.json"])
        local_dwi = count_files(raw, ["*dwi.nii.gz", "*.bvec", "*.bval", "*dwi.json"])
        local_connectome = count_files(raw, ["*connectome*", "*tract*", "*fiber*", "*fibre*"])
        rows.append(
            {
                "dataset": dataset,
                "state_file": rel(states),
                "state_file_exists": states.exists(),
                "raw_root": rel(raw),
                "raw_root_exists": raw.exists(),
                "local_t1_t2_file_count": local_anat,
                "local_dwi_file_count": local_dwi,
                "local_connectome_file_count": local_connectome,
                "online_metadata_status": online_row.get("status", ""),
                "online_snapshot_id": online_row.get("snapshot_id", ""),
                "online_anat_candidate_count": online_counts.get("anat", 0),
                "online_dwi_candidate_count": online_counts.get("dwi", 0),
                "online_connectome_or_tract_candidate_count": online_counts.get("connectome_or_tract", 0),
                "individual_structural_connectome_available": bool(local_connectome > 0 or local_dwi > 0 or online_counts.get("dwi", 0) > 0 or online_counts.get("connectome_or_tract", 0) > 0),
            }
        )
    write_csv(RESULTS / "e1_modality_audit.csv", rows)
    status = "STRUCTURAL_CONNECTOME_OR_DWI_AVAILABLE" if all(r["individual_structural_connectome_available"] for r in rows) else "ANATOMY_ONLY_NO_CONNECTOME_OR_DWI_FOR_PRIMARY_DATASETS"
    payload = {
        "experiment": "P5-E1",
        "status": status,
        "datasets": rows,
        "online_audit": rel(ONLINE_AUDIT) if ONLINE_AUDIT.exists() else "",
        "claim_boundary": "T1w anatomy availability is not sufficient for the Paper 5 individual structural-connectome constraint test. The primary G_i test requires subject-level dMRI-derived or otherwise valid structural connectomes.",
    }
    write_json(RESULTS / "e1_modality_audit.json", payload)
    return payload


def load_transition_rows() -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for dataset, spec in DATASETS.items():
        rows, roi_cols = load_stage_states(str(spec["states"]))
        meta, x_state, y_state = build_transitions(rows, roi_cols)
        x_arr = np.asarray(x_state, dtype=float)
        y_arr = np.asarray(y_state, dtype=float)
        for idx, m in enumerate(meta):
            transition_type = f"{m.get('source_cwp', 'NA')}_TO_{m.get('target_cwp', 'NA')}"
            if transition_type not in PRIMARY_TRANSITIONS:
                continue
            out.append(
                {
                    "dataset": dataset,
                    "subject": m.get("subject", "NA"),
                    "run": m.get("run", "NA"),
                    "trial_id": m.get("trial_id", "NA"),
                    "transition_type": transition_type,
                    "domain": m.get("domain", "NA") or "NA",
                    "load": m.get("load", "NA") or "NA",
                    "x": x_arr[idx],
                    "y": y_arr[idx],
                    "delta": y_arr[idx] - x_arr[idx],
                }
            )
    return out


def e2_structural_connectome_audit() -> dict[str, Any]:
    files = sorted([p for p in STRUCTURAL.rglob("*") if p.is_file()])
    accepted = [p for p in files if p.suffix.lower() in {".csv", ".tsv", ".npy", ".npz", ".json"}]
    rows = (
        [
            {
                "file": rel(path),
                "suffix": path.suffix,
                "size_bytes": path.stat().st_size,
                "accepted_candidate": path in accepted,
            }
            for path in files
        ]
        or [
            {
                "file": "NO_CONNECTOME_FILES_FOUND",
                "suffix": "NA",
                "size_bytes": 0,
                "accepted_candidate": False,
            }
        ]
    )
    write_csv(RESULTS / "e2_structural_connectome_inventory.csv", rows)
    payload = {
        "experiment": "P5-E2",
        "status": "STRUCTURAL_CONNECTOME_FILES_FOUND" if accepted else "NO_SUBJECT_LEVEL_STRUCTURAL_CONNECTOME_FILES_FOUND",
        "structural_connectome_dir": rel(STRUCTURAL),
        "n_files": len(files),
        "n_accepted_candidate_files": len(accepted),
        "accepted_candidate_files": [rel(p) for p in accepted[:200]],
        "required_schema": "subject-level connectome matrices aligned to the 216-ROI state representation, or a reproducible dMRI pipeline that generates them.",
    }
    write_json(RESULTS / "e2_structural_connectome_audit.json", payload)
    return payload


def e3_transition_inventory(rows: Sequence[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for dataset in sorted({r["dataset"] for r in rows}):
        block = [r for r in rows if r["dataset"] == dataset]
        for transition_type in PRIMARY_TRANSITIONS:
            subset = [r for r in block if r["transition_type"] == transition_type]
            out.append(
                {
                    "dataset": dataset,
                    "transition_type": transition_type,
                    "n_transitions": len(subset),
                    "n_subjects": len({r["subject"] for r in subset}),
                    "n_runs": len({(r["subject"], r["run"]) for r in subset}),
                    "n_roi_features": len(subset[0]["x"]) if subset else 0,
                }
            )
    write_csv(RESULTS / "e3_functional_transition_inventory.csv", out)
    return out


def one_hot(rows: Sequence[dict[str, Any]], fields: Sequence[str], levels: dict[str, list[str]] | None = None) -> tuple[np.ndarray, dict[str, list[str]]]:
    if levels is None:
        levels = {field: sorted({str(r.get(field, "NA") or "NA") for r in rows}) for field in fields}
    if not fields:
        return np.zeros((len(rows), 0)), levels
    encoded = []
    for row in rows:
        vals: list[float] = []
        for field in fields:
            value = str(row.get(field, "NA") or "NA")
            vals.extend(1.0 if level == value else 0.0 for level in levels[field])
        encoded.append(vals)
    return np.asarray(encoded, dtype=float), levels


def evaluate_cv(rows: Sequence[dict[str, Any]], fields: Sequence[str]) -> list[float]:
    subjects = sorted({r["subject"] for r in rows})
    mses: list[float] = []
    for subject in subjects:
        train = [r for r in rows if r["subject"] != subject]
        test = [r for r in rows if r["subject"] == subject]
        if not train or not test:
            continue
        x_train_state = np.vstack([r["x"] for r in train])
        x_test_state = np.vstack([r["x"] for r in test])
        cat_train, levels = one_hot(train, fields)
        cat_test, _ = one_hot(test, fields, levels)
        x_train = np.hstack([x_train_state, cat_train])
        x_test = np.hstack([x_test_state, cat_test])
        y_train = np.vstack([r["y"] for r in train])
        y_test = np.vstack([r["y"] for r in test])
        scaler = StandardScaler().fit(x_train)
        pred = Ridge(alpha=1.0, fit_intercept=True).fit(scaler.transform(x_train), y_train).predict(scaler.transform(x_test))
        mses.append(float(np.mean((y_test - pred) ** 2)))
    return mses


def e4_state_only_baselines(rows: Sequence[dict[str, Any]]) -> list[dict[str, Any]]:
    specs = {
        "state_only": [],
        "state_plus_transition_type": ["transition_type"],
        "state_plus_context": ["transition_type", "domain", "load"],
    }
    out: list[dict[str, Any]] = []
    for dataset in sorted({r["dataset"] for r in rows}):
        block = [r for r in rows if r["dataset"] == dataset]
        for model, fields in specs.items():
            mses = evaluate_cv(block, fields)
            out.append(
                {
                    "dataset": dataset,
                    "model": model,
                    "fields": "+".join(fields) or "none",
                    "n_subject_folds": len(mses),
                    "mean_subject_mse": float(np.mean(mses)) if mses else float("nan"),
                    "median_subject_mse": float(np.median(mses)) if mses else float("nan"),
                    "std_subject_mse": float(np.std(mses, ddof=1)) if len(mses) > 1 else 0.0,
                }
            )
    write_csv(RESULTS / "e4_state_only_baselines.csv", out)
    return out


def blocked_experiment(name: str, reason: str, output: Path) -> dict[str, Any]:
    payload = {
        "experiment": name,
        "status": "BLOCKED_NO_SUBJECT_LEVEL_STRUCTURAL_CONNECTOME",
        "reason": reason,
        "claim_boundary": "No individual structural-connectome effect can be estimated without subject-level structural connectomes aligned to the functional state ROI space.",
    }
    write_json(output, payload)
    return payload


def e8_claim_audit(e1: dict[str, Any], e2: dict[str, Any]) -> dict[str, Any]:
    structural_ready = e1["status"] == "STRUCTURAL_CONNECTOME_OR_DWI_AVAILABLE" and e2["status"] == "STRUCTURAL_CONNECTOME_FILES_FOUND"
    payload = {
        "experiment": "P5-E8",
        "status": "P5_STRUCTURAL_CONSTRAINT_NOT_TESTED_CONNECTOME_MISSING" if not structural_ready else "P5_READY_FOR_STRUCTURAL_MODELING",
        "claim_allowed_structural_constraint": False,
        "claim_allowed_individual_gi_improves_prediction": False,
        "claim_allowed_cwp_validated": False,
        "structural_connectome_ready": structural_ready,
        "anatomy_only_available_online": any(
            row.get("online_anat_candidate_count", 0) > 0 and row.get("online_dwi_candidate_count", 0) == 0
            for row in e1["datasets"]
        ),
        "dwi_or_connectome_available_for_primary_test": all(row.get("individual_structural_connectome_available", False) for row in e1["datasets"]),
        "critical_limitation": "OpenNeuro metadata shows T1w anatomy candidates for the current datasets, but no dMRI/bvec/bval/connectome candidates. T1w anatomy alone is not a subject-level structural connectome. The Paper 5 primary G_i test is therefore not run.",
        "no_invented_results": True,
    }
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
    if not cols:
        return ""

    def cell(value: Any) -> str:
        if isinstance(value, float) and math.isnan(value):
            return ""
        text = str(value)
        if len(text) > 160:
            text = text[:157] + "..."
        return text.replace("|", "\\|").replace("\n", " ")

    lines = [
        "| " + " | ".join(cell(c) for c in cols) + " |",
        "| " + " | ".join("---" for _ in cols) + " |",
    ]
    for _, row in df.iterrows():
        lines.append("| " + " | ".join(cell(row[c]) for c in cols) + " |")
    return "\n".join(lines)


def write_protocol() -> None:
    (PROTOCOL / "PAPER5_FROZEN_PROTOCOL_v1.md").write_text(
        """# Paper 5 Phase 0 Frozen Protocol v1

Title: Structural Data Availability Gate for Reproducible Stage-Conditioned Brain-State Transitions

Paper type: Method Paper / feasibility gate

## Core Question

Do the datasets used in Papers 1-4 contain the subject-level structural connectomes required to test whether `G_i` constrains reproducible stage-conditioned transitions?

## Required Primary Input

```text
Subject-level structural connectome matrices aligned to the 216-ROI functional state representation.
```

T1w anatomy alone is not sufficient for the primary `G_i` test.

## Experiment Chain

```text
E1 Dataset / modality audit
E2 Structural connectome inventory
E3 Functional transition inventory
E4 State-only/context baseline
E5 Individual G_i model
E6 Group-average/random/distance nulls
E7 Subject-holdout statistics
E8 Claim audit + paper package
```
""",
        encoding="utf-8",
    )
    (PROTOCOL / "PAPER5_HCP_PHASE1_PROTOCOL_v1.md").write_text(
        f"""# Paper 5 Phase 1 HCP-YA 2025 Protocol v1

Title: Individual Structural Connectomes as Constraints on Cognitive Brain-State Transitions

## Status

```text
PENDING_HCP_YA_2025_DATA_ACCESS_AND_DOWNLOAD
```

## Rationale

The OpenNeuro datasets used in Papers 1-4 do not contain dMRI-derived subject-level structural connectomes. The proper continuation of Paper 5 is therefore a new HCP-YA 2025 analysis, not a post-hoc reinterpretation of T1w anatomy as `G_i`.

## Dataset Rule

Use HCP-Young Adult 2025 only. Do not mix HCP-YA 2025 processed outputs with the 2017 S1200 processing in the same analysis.

Official release page:

```text
{HCP_RELEASE_URL}
```

Known release facts from the official documentation checked during setup:

```text
Release date: 2025-08-11
Processed participants without processing errors and with at least one rfMRI run for MSMAll: 1071
Retest participants: 45
Unprocessed imaging participants: 1113
Available modality target: 3T task-fMRI + diffusion MRI / connectivity-relevant structural data
```

## Primary Hypothesis

```text
P(S_next | S_t, CognitiveState, G_i) > P(S_next | S_t, CognitiveState)
```

## Required Inputs

```text
HCP-YA 2025 subject list
3T Working Memory task-fMRI runs
task event timing / E-Prime variables
dMRI-derived subject-level structural connectomes or reproducible dMRI-to-connectome pipeline
ROI atlas shared by fMRI state extraction and structural connectome matrices
```

## Model Chain

```text
HCP-YA 2025 task-fMRI
-> stage/event-aligned brain states S_t and S_next
-> HCP-YA 2025 dMRI/connectivity-derived G_i
-> state/context baseline
-> individual G_i model
-> structural nulls
-> subject-level statistics
```

## Baselines

```text
M0: S_next = f(S_t)
M1: S_next = f(S_t, CognitiveState)
M2: S_next = f(S_t, CognitiveState, group_mean_G)
M3: S_next = f(S_t, CognitiveState, G_i)
```

## Structural Nulls

```text
subject-connectome swap
group-mean connectome
edge-shuffled connectome
degree-preserving randomized graph
distance-only graph
```

## Success Gate

The structural claim is allowed only if individual `G_i` improves subject-held-out prediction over the state/context baseline and beats the structural nulls under subject-level statistics.

## Failure Gate

If individual `G_i` does not beat group/random/swapped connectomes, the conclusion is that current evidence does not support individual structural-connectome constraint on the extracted transitions.
""",
        encoding="utf-8",
    )


def hcp_phase1_requirements() -> dict[str, Any]:
    payload = {
        "experiment": "P5-Phase1-HCP-Setup",
        "status": "PENDING_HCP_YA_2025_DATA_ACCESS_AND_DOWNLOAD",
        "official_release_url": HCP_RELEASE_URL,
        "release_date": "2025-08-11",
        "processed_participants_documented": 1071,
        "retest_participants_documented": 45,
        "do_not_mix_with_s1200": True,
        "required_inputs": [
            "HCP-YA 2025 subject list",
            "3T Working Memory task-fMRI runs",
            "task event timing / E-Prime variables",
            "subject-level dMRI-derived structural connectomes or raw dMRI sufficient to construct them",
            "common ROI atlas for fMRI states and structural matrices",
        ],
        "blocked_until": "ConnectomeDB/BALSA data access and authorized HCP-YA 2025 package download are available locally.",
        "claim_boundary": "No HCP structural constraint result has been run yet.",
    }
    write_json(RESULTS / "hcp_phase1_access_requirements.json", payload)
    return payload


def make_figures() -> None:
    os.environ.setdefault("MPLCONFIGDIR", str(ROOT / ".matplotlib"))
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    audit = pd.read_csv(RESULTS / "e1_modality_audit.csv")
    x = np.arange(len(audit))
    width = 0.28
    fig, ax = plt.subplots(figsize=(7.6, 4.2))
    ax.bar(x - width, audit["online_anat_candidate_count"].astype(float), width, label="Online T1/T2 anatomy")
    ax.bar(x, audit["online_dwi_candidate_count"].astype(float), width, label="Online dMRI")
    ax.bar(x + width, audit["online_connectome_or_tract_candidate_count"].astype(float), width, label="Online connectome/tract")
    ax.set_xticks(x, audit["dataset"])
    ax.set_title("E1 Structural Modality Availability")
    ax.set_ylabel("Candidate files")
    ax.legend()
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(FIGURES / "figure_1_structural_modality_audit.png", dpi=180)
    fig.savefig(FIGURES / "figure_1_structural_modality_audit.pdf")
    plt.close(fig)

    base = pd.read_csv(RESULTS / "e4_state_only_baselines.csv")
    pivot = base.pivot(index="dataset", columns="model", values="mean_subject_mse")
    fig, ax = plt.subplots(figsize=(7.8, 4.2))
    pivot.plot(kind="bar", ax=ax)
    ax.set_title("E4 Functional Baselines Without Structural Connectomes")
    ax.set_ylabel("Leave-subject-out mean MSE")
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(FIGURES / "figure_2_state_only_baselines.png", dpi=180)
    fig.savefig(FIGURES / "figure_2_state_only_baselines.pdf")
    plt.close(fig)


def write_attachments(audit: dict[str, Any]) -> None:
    (ATTACHMENTS / "A1_Frozen_Protocol.md").write_text(
        f"""# A1 Frozen Protocol

Status: E1-E8 implemented and run.

Primary endpoint:

```text
Held-out S_next prediction improvement from individual structural connectome G_i over state-only/context baselines.
```

Current status:

```text
{audit["status"]}
```

Phase 1 continuation:

```text
HCP-YA 2025 structural-connectome test is frozen but not yet run.
```
""",
        encoding="utf-8",
    )
    (ATTACHMENTS / "A2_Dataset_Manifest.md").write_text("# A2 Dataset Manifest\n\n" + table_markdown(RESULTS / "e1_modality_audit.csv") + "\n", encoding="utf-8")
    (ATTACHMENTS / "A3_Full_Pipeline.md").write_text(
        """# A3 Full Pipeline

```text
OpenNeuro metadata audit
-> local modality audit
-> structural connectome inventory
-> functional transition inventory
-> state-only/context baseline
-> structural-model gate
-> claim audit
```
""",
        encoding="utf-8",
    )
    (ATTACHMENTS / "A4_Full_Baseline_Results.md").write_text("# A4 Full Baseline Results\n\n" + table_markdown(RESULTS / "e4_state_only_baselines.csv") + "\n", encoding="utf-8")
    (ATTACHMENTS / "A5_Holdout_Audit.md").write_text(
        """# A5 Holdout Audit

Subject holdout is implemented for E4 functional baselines.

The structural primary holdout was not run because no subject-level structural connectome files were available.
""",
        encoding="utf-8",
    )
    (ATTACHMENTS / "A6_Statistics.md").write_text(
        "# A6 Statistics\n\nNo structural effect statistics are reported because the primary structural model was not run.\n\n" + table_markdown(RESULTS / "e4_state_only_baselines.csv") + "\n",
        encoding="utf-8",
    )
    (ATTACHMENTS / "A7_Null_Falsification_Tests.md").write_text(
        """# A7 Null / Falsification Tests

Planned nulls:

```text
group-average connectome
degree-preserving randomized connectome
edge-shuffled connectome
distance-only network
subject-connectome swap
```

Status: not run because subject-level structural connectomes are missing.
""",
        encoding="utf-8",
    )
    (ATTACHMENTS / "A8_QC_Leakage_Audit.md").write_text(
        f"""# A8 QC & Leakage Audit

Critical limitation:

```text
{audit["critical_limitation"]}
```

No structural model was fit, so no structural leakage claim is made.
""",
        encoding="utf-8",
    )
    (ATTACHMENTS / "A9_Limitations_Failed_Analyses.md").write_text(
        f"""# A9 Limitations & Failed Analyses

Failed primary analysis:

```text
Individual G_i structural constraint model was not run because subject-level structural connectomes are unavailable.
```

Unsupported claims:

```text
Structural connectivity constrains the transitions.
Individual G_i improves S_next prediction.
CWP is validated.
```

Observed status:

```text
{audit["status"]}
```
""",
        encoding="utf-8",
    )
    (ATTACHMENTS / "A10_One_Command_Reproduction.md").write_text(
        """# A10 One-command Reproduction

Run the local Paper 5 package:

```powershell
powershell -ExecutionPolicy Bypass -File paper5\\scripts\\reproduce-paper5.ps1
```

Refresh OpenNeuro structural metadata first:

```powershell
powershell -ExecutionPolicy Bypass -File paper5\\scripts\\reproduce-paper5-online-structural-audit.ps1
```
""",
        encoding="utf-8",
    )


def current_results_md(audit: dict[str, Any]) -> str:
    return f"""# Paper 5 Current Results

Status:

```text
{audit["status"]}
```

## E1 Modality Audit

{table_markdown(RESULTS / "e1_modality_audit.csv")}

## E2 Structural Connectome Inventory

{table_markdown(RESULTS / "e2_structural_connectome_inventory.csv")}

## E3 Functional Transition Inventory

{table_markdown(RESULTS / "e3_functional_transition_inventory.csv")}

## E4 Functional Baselines

{table_markdown(RESULTS / "e4_state_only_baselines.csv")}

## Claim Audit

```json
{json.dumps(audit, indent=2)}
```

## Phase 1 HCP Continuation

```text
PENDING_HCP_YA_2025_DATA_ACCESS_AND_DOWNLOAD
```

The next valid Paper 5 test is HCP-YA 2025 only, using task-fMRI plus dMRI-derived subject-level structural connectomes. This has not been run.
"""


def manuscript_text(audit: dict[str, Any]) -> str:
    return f"""# Phase 0 Structural-Data Gate for Testing Structural Constraints on Reproducible Brain-State Transitions

Authors: [TO BE FILLED]  
Affiliations: [TO BE FILLED]  
Correspondence: [TO BE FILLED]

## Abstract

Papers 3 and 4 established that extracted macroscopic stage-transition vectors are reproducible and survive several proxy falsification tests, while leaving strong CWP and full noise-exclusion claims unsupported. The original Paper 5 question asks whether those transition vectors are constrained by individual structural connectomes. We implemented the Phase 0 structural-data gate, audited local and OpenNeuro metadata for structural modalities, inventoried available functional transitions, and ran state-only/context functional baselines. OpenNeuro metadata shows T1w anatomy candidates for the current datasets, but no dMRI/bvec/bval/connectome candidates. Because T1w anatomy alone is not a subject-level structural connectome, the individual `G_i` model and structural nulls were not run. Current status: `{audit["status"]}`. The real structural hypothesis remains pending and is now frozen as an HCP-YA 2025 Phase 1 protocol.

## 1. Introduction

The next scientific question after reproducibility and falsification is whether individual brain structure constrains the observed transition geometry. This paper therefore treats `G_i` as a required input, not as a label that can be approximated by task timing or functional states.

## 2. Methods

The planned primary model was:

```text
S_next = f(S_t, StageTransition, Context, G_i)
```

where `G_i` must be a subject-level structural connectome aligned to the 216-ROI state representation. Baselines include state-only and state-plus-context functional models. Planned structural nulls include group-average connectome, randomized connectome, distance-only network, and subject-connectome swap.

## 3. Results

### 3.1 Modality Audit

{table_markdown(RESULTS / "e1_modality_audit.csv")}

### 3.2 Structural Connectome Inventory

{table_markdown(RESULTS / "e2_structural_connectome_inventory.csv")}

### 3.3 Functional Transition Inventory

{table_markdown(RESULTS / "e3_functional_transition_inventory.csv")}

### 3.4 Functional Baselines

{table_markdown(RESULTS / "e4_state_only_baselines.csv")}

### 3.5 Structural Model Gate

The individual structural-connectome model was not run. Required subject-level structural connectomes are not available in the current workspace, and OpenNeuro metadata for the current datasets did not identify dMRI or connectome candidates.

## 4. Discussion

This is a gate result, not a structural discovery result. The current datasets contain or advertise T1w anatomy, but no dMRI-derived or otherwise valid subject-level structural connectomes. Therefore Paper 5 cannot support the claim that structure constrains the reproducible transitions. It does, however, define the exact missing input needed for a valid structural-constraint test.

Critical limitation: {audit["critical_limitation"]}

### 4.1 HCP-YA 2025 Continuation

The valid continuation is an HCP-YA 2025 analysis using 3T task-fMRI and subject-level diffusion/connectivity data. HCP-YA 2025 must be analyzed as a single release and not mixed with the earlier S1200 processing. The Phase 1 hypothesis remains:

```text
P(S_next | S_t, CognitiveState, G_i) > P(S_next | S_t, CognitiveState)
```

This hypothesis has not yet been tested in HCP.

## 5. Conclusion

Current claim-audit status: `{audit["status"]}`.

Paper 5 pipeline engineering is complete for Phase 0. The Paper 5 structural hypothesis is not complete.

## Data Availability

OpenNeuro-derived local state tables from Papers 1-4 were used. OpenNeuro metadata was queried for structural/anatomical/dMRI/connectome availability.

## Code Availability

[TO BE FILLED]

## Ethics Statement

This analysis uses public de-identified datasets. Dataset-specific ethics approvals are reported by the original dataset providers.

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
        style = styles["Heading1"] if stripped.startswith("# ") else styles["Heading2"] if stripped.startswith("## ") else styles["BodyText"]
        clean = stripped.lstrip("#").strip()
        safe = clean.replace("`", "")
        safe = safe.replace("\\_", "_").replace("\\", "")
        safe = safe.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        story.append(Paragraph(safe, style))
    doc.build(story)


def write_submission(audit: dict[str, Any]) -> None:
    text = manuscript_text(audit)
    (MANUSCRIPT / "PAPER5_MANUSCRIPT_CURRENT.md").write_text(text, encoding="utf-8")
    build_pdf(text)
    (SUBMISSION / "SUBMISSION_READINESS.md").write_text(
        f"""# Paper 5 Submission Readiness

Current status: Phase 0 is complete; not ready for bioRxiv as a positive structural-constraint paper.

Generated:

```text
paper5/manuscript/PAPER5_MANUSCRIPT_CURRENT.md
paper5/submission/PAPER5_BIORXIV_DRAFT_CURRENT.pdf
paper5/attachments/
paper5/manuscript/figures/
```

Remaining before a real structural-constraint preprint:

```text
Obtain authorized HCP-YA 2025 access and download the needed packages.
Extract HCP Working Memory stage/event-aligned brain states.
Obtain or construct subject-level dMRI-derived structural connectomes.
Align connectomes to the functional state ROI representation.
Run individual G_i model and structural nulls on HCP-YA 2025 only.
Add formal literature review, citations, authors, affiliations, funding, COI, and code URL.
```

Claim audit status:

```text
{audit["status"]}
```
""",
        encoding="utf-8",
    )
    (SUBMISSION / "HCP_PHASE1_NEXT_ACTIONS.md").write_text(
        f"""# HCP Phase 1 Next Actions

Status:

```text
PENDING_HCP_YA_2025_DATA_ACCESS_AND_DOWNLOAD
```

Use HCP-Young Adult 2025 only:

```text
{HCP_RELEASE_URL}
```

Required local inputs before the structural hypothesis can be tested:

```text
HCP-YA 2025 Working Memory task-fMRI package
HCP-YA 2025 event/E-Prime variables
HCP-YA 2025 dMRI-derived connectomes or raw dMRI packages plus a reproducible connectome-construction pipeline
Subject list intersecting fMRI and structural-connectome availability
ROI atlas mapping shared by fMRI states and G_i matrices
```

Do not tune on mixed S1200/2025 data. Do not treat T1w anatomy as `G_i`.
""",
        encoding="utf-8",
    )
    (SUBMISSION / "FIGURE_CAPTIONS.md").write_text(
        """# Figure Captions

Figure 1. Structural modality availability from local and OpenNeuro metadata audit.

Figure 2. Functional state-only/context baselines available before structural-connectome modeling.
""",
        encoding="utf-8",
    )


def main() -> None:
    ensure_dirs()
    write_protocol()
    e1 = e1_modality_audit()
    e2 = e2_structural_connectome_audit()
    rows = load_transition_rows()
    e3_transition_inventory(rows)
    e4_state_only_baselines(rows)
    blocked_experiment("P5-E5", "No subject-level structural connectomes aligned to the 216-ROI functional state representation were found.", RESULTS / "e5_individual_gi_model.json")
    blocked_experiment("P5-E6", "Structural nulls require a real subject-level structural connectome before group-average/random/distance comparisons are meaningful.", RESULTS / "e6_structural_nulls.json")
    blocked_experiment("P5-E7", "Subject-holdout structural statistics require E5 individual G_i model outputs.", RESULTS / "e7_subject_holdout_statistics.json")
    audit = e8_claim_audit(e1, e2)
    hcp_phase1_requirements()
    write_json(RESULTS / "e1_e8_run_summary.json", {"experiment": "P5-E1-E8", "status": audit["status"], "claim_audit": audit})
    (RESULTS / "CURRENT_RESULTS.md").write_text(current_results_md(audit), encoding="utf-8")
    make_figures()
    write_attachments(audit)
    write_submission(audit)
    print(json.dumps(audit, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
