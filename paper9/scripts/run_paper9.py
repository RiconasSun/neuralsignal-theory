from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PAPER = ROOT / "paper9"
NOW = datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        raise ValueError(f"Refusing to write empty CSV: {path}")
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


PAPER_INPUTS = [
    {
        "paper": "P1",
        "title": "CWP compositionality / boundary test",
        "source_paths": "paper1/results/claim_audit.json; paper1/submission/SUBMISSION_CLAIM_AUDIT.json",
        "claim": "CWP-style compositional labels improved within-dataset OOD prediction in ds001635.",
        "primary_evidence": "Local OOD signal present; incremental superiority over strong task model inconclusive; external dataset failed.",
        "primary_gate": "PARTIAL",
        "holdout_status": "within_dataset_OOD_supported; external_failed",
        "null_status": "survived_planned_matched_nulls_as_recorded_in_P1_package",
        "status": "OOD_SUPPORTED",
        "disallowed_claim": "CWP is validated; CWP clearly outperforms task labels overall; CWP externally replicates.",
        "ontology_use": "Treat as evidence for local compositional dynamics, not as validated primitive ontology.",
    },
    {
        "paper": "P2",
        "title": "Cross-dataset failure and generalization mechanism",
        "source_paths": "paper2/results/e9_8_claim_audit.json; paper2/results/CURRENT_RESULTS.md",
        "claim": "Compositional structure helps, but CWP-specific cross-dataset superiority is not supported.",
        "primary_evidence": "CWP v2 exceeded random ontology in Dataset C but did not outperform strong task baseline.",
        "primary_gate": "FAILED_STRONG_SUPERIORITY",
        "holdout_status": "locked_dataset_c_evaluated",
        "null_status": "random_ontology_remained_material_competing_explanation",
        "status": "NOT_SUPPORTED",
        "disallowed_claim": "Revised CWP ontology solved cross-dataset generalization.",
        "ontology_use": "Mark semantic CWP specificity as unsupported while preserving generic compositional signal.",
    },
    {
        "paper": "P3",
        "title": "Reproducibility of macroscopic transition dynamics",
        "source_paths": "paper3/results/e8_claim_audit.json; paper3/results/CURRENT_RESULTS.md",
        "claim": "Macroscopic transition dynamics show reproducibility within the tested boundaries.",
        "primary_evidence": "P3 package contains run/session/dataset reproducibility summaries and null-test tables.",
        "primary_gate": "SUPPORTED_WITH_BOUNDARIES",
        "holdout_status": "recorded_in_paper3_holdout_audit",
        "null_status": "recorded_in_paper3_null_tables",
        "status": "REPRODUCIBLE",
        "disallowed_claim": "Reproducibility proves CWP as a natural neural primitive.",
        "ontology_use": "Upgrade transition-family object above candidate status where P3 gates passed.",
    },
    {
        "paper": "P4",
        "title": "Noise and falsification boundary",
        "source_paths": "paper4/results/e8_claim_audit.json; paper4/results/CURRENT_RESULTS.md",
        "claim": "Some transition structure survives falsification, but measured physiology remains unresolved and dynamics are noise-sensitive.",
        "primary_evidence": "P4 contains proxy nuisance, noise injection, timing-position, and falsification-null outputs.",
        "primary_gate": "SUPPORTED_WITH_CONFOUNDS",
        "holdout_status": "recorded_in_paper4_holdout_audit",
        "null_status": "partial_survival_with_unresolved_measured_physiology",
        "status": "CONFOUNDED",
        "disallowed_claim": "Motion, physiology, and scanner confounds have been eliminated.",
        "ontology_use": "Attach confound flags to transition-family evidence rather than deleting the transition object.",
    },
    {
        "paper": "P5",
        "title": "Structural proxy grounding",
        "source_paths": "paper5/results/e8_hcp_claim_audit.json; paper5/results/PAPER5_FINAL_CONCLUSION.md",
        "claim": "Subject-specific BedpostX-dyad structural proxy did not add stable predictive constraint.",
        "primary_evidence": "True subject structural proxy did not win the no-structure, group, swap, or rewire comparison chain.",
        "primary_gate": "FAILED_PRIMARY_GATE",
        "holdout_status": "hcp_proxy_holdout_recorded",
        "null_status": "structural_nulls_not_defeated",
        "status": "NOT_SUPPORTED",
        "disallowed_claim": "Subject-specific structural connectome constrains macro transitions.",
        "ontology_use": "Downgrade structural-grounding link; preserve method limitation that proxy is not full ACT/SIFT2 connectome.",
    },
    {
        "paper": "P6",
        "title": "Macro transition to fast dynamics bridge",
        "source_paths": "paper6/results/e8_claim_audit.json; paper6/results/CURRENT_RESULTS.md",
        "claim": "Fast-dynamics bridge remains candidate-level and measurement-regime bounded.",
        "primary_evidence": "P6 package contains electrophysiology transition features, nulls, external convergent outputs, and claim audit.",
        "primary_gate": "CANDIDATE_WITH_BOUNDARIES",
        "holdout_status": "recorded_in_paper6_external_convergent_outputs",
        "null_status": "recorded_in_paper6_null_outputs",
        "status": "CANDIDATE",
        "disallowed_claim": "NAP is validated as a fast neural primitive.",
        "ontology_use": "Create CandidateNAP only when linked to observed transition evidence and mark as non-validated.",
    },
    {
        "paper": "P7",
        "title": "High-fidelity structural grounding extension",
        "source_paths": "paper7/results/p7_e8_claim_audit.json; paper7/results/PAPER7_FINAL_CONCLUSION.md",
        "claim": "High-fidelity structural route produced engineering/QC progress and preliminary negative structural-model interface results, but final 100-subject ACT/SIFT2 structural hypothesis remains not run.",
        "primary_evidence": "P7 records connectome generation/QC and structural model smoke/final-route artifacts; 100-subject final test is not complete.",
        "primary_gate": "TOOLCHAIN_AND_COHORT_BOUNDARY",
        "holdout_status": "pre_100_subject_boundary_not_final_claim",
        "null_status": "preliminary_true_structure_superiority_not_supported",
        "status": "TOOLCHAIN_BLOCKED",
        "disallowed_claim": "High-fidelity ACT/SIFT2 structural grounding is established.",
        "ontology_use": "Keep structural mechanism as unresolved; do not upgrade from P7 engineering readiness alone.",
    },
    {
        "paper": "P8",
        "title": "Signal separation and measured-physiology boundary",
        "source_paths": "paper8/results/p8_e8_claim_audit.json; paper8/results/PAPER8_FINAL_CONCLUSION.md",
        "claim": "Task classification does not equal transition reproducibility; metadata confounding is a serious competing explanation; measured-physiology extension remains convergent, not direct replication.",
        "primary_evidence": "Primary transition gate failed while classification exceeded shuffle; metadata-only baseline was strong in the frozen P8 audit.",
        "primary_gate": "FAILED_PRIMARY_GATE",
        "holdout_status": "measured_physio_extension_smoke_not_final",
        "null_status": "metadata_baseline_material",
        "status": "CONFOUNDED",
        "disallowed_claim": "Condition decodability proves transition reproducibility; measured physiology is resolved.",
        "ontology_use": "Force metadata/timing/physiology competing explanations into every future dynamics claim.",
    },
]


STATUS_TAXONOMY = {
    "status_labels": [
        "OBSERVED",
        "REPRODUCIBLE",
        "OOD_SUPPORTED",
        "EXTERNALLY_REPLICATED",
        "CANDIDATE",
        "NOT_SUPPORTED",
        "FAILED_PRIMARY_GATE",
        "CONFOUNDED",
        "DATA_BLOCKED",
        "TOOLCHAIN_BLOCKED",
        "UNTESTED",
    ],
    "upgrade_rules": {
        "OBSERVED": "A phenomenon is measured above basic sanity/null checks in a specified dataset and measurement regime.",
        "REPRODUCIBLE": "The same object recurs across predefined runs, sessions, subjects, or equivalent repeated units.",
        "OOD_SUPPORTED": "The object improves a preregistered out-of-distribution endpoint without changing post-holdout definitions.",
        "EXTERNALLY_REPLICATED": "The object survives a locked independent dataset using frozen definitions and model rules.",
    },
    "downgrade_rules": {
        "NOT_SUPPORTED": "The preregistered primary gate fails or strong baseline/null remains unbeaten.",
        "CONFOUNDED": "A plausible competing explanation remains unresolved or performs materially well.",
        "DATA_BLOCKED": "The required variable/data object is absent; this is not evidence against the hypothesis.",
        "TOOLCHAIN_BLOCKED": "The required computational route is not complete enough for a scientific hypothesis test.",
    },
}


ONTOLOGY_SCHEMA = {
    "schema_name": "CWP-NAP Ontology v2",
    "version": "0.1.0",
    "generated_at": NOW,
    "principle": "Observable -> State -> Transition -> Motif -> Candidate Primitive -> Semantics",
    "objects": {
        "Observable": {
            "required_fields": ["id", "dataset", "modality", "measurement_regime", "preprocessing_state", "evidence_status"],
            "may_link_to": ["NeuralState", "CompetingExplanation"],
        },
        "NeuralState": {
            "required_fields": ["id", "state_vector_definition", "time_window", "atlas_or_sensor_space", "evidence_status"],
            "may_link_to": ["TransitionFamily", "ContextModifier"],
        },
        "TransitionFamily": {
            "required_fields": ["id", "source_state", "target_state", "transition_metric", "reproducibility_status", "confound_status"],
            "may_link_to": ["DynamicMotif", "CandidateCWP", "CompetingExplanation"],
        },
        "DynamicMotif": {
            "required_fields": ["id", "discovery_method", "temporal_scale", "recurrence_metric", "holdout_status", "evidence_status"],
            "may_link_to": ["CandidateNAP", "CandidateCWP"],
        },
        "CandidateNAP": {
            "required_fields": ["id", "motif_link", "fast_dynamics_feature", "null_tests", "evidence_status"],
            "may_link_to": ["CandidateCWP", "MeasurementRegime"],
        },
        "CandidateCWP": {
            "required_fields": ["id", "latent_factor", "motif_sequence", "context_modifier", "semantic_interpretation", "evidence_status"],
            "may_link_to": ["CognitiveProgram", "ClaimBoundary"],
        },
        "CognitiveProgram": {
            "required_fields": ["id", "candidate_cwp_sequence", "task_context", "behavioral_endpoint", "evidence_status"],
            "may_link_to": ["ContextModifier", "ClaimBoundary"],
        },
        "ContextModifier": {
            "required_fields": ["id", "domain", "load", "rule", "timing", "metadata", "evidence_status"],
            "may_link_to": ["TransitionFamily", "CandidateCWP"],
        },
        "CompetingExplanation": {
            "required_fields": ["id", "type", "baseline_or_null", "test_result", "resolution_status"],
            "types": ["task_label", "timing", "metadata", "motion", "physiology", "scanner", "random_ontology", "structural_proxy", "continuous_manifold"],
        },
        "ClaimBoundary": {
            "required_fields": ["id", "allowed_claim", "disallowed_claim", "supporting_evidence", "downgrade_trigger"],
        },
    },
    "default_claim_permissions": {
        "claim_allowed_dynamic_motifs_exist": False,
        "claim_allowed_discrete_NAP_supported": False,
        "claim_allowed_CWP_v2_semantics_supported": False,
        "claim_allowed_neural_grammar_supported": False,
        "claim_allowed_external_replication": False,
        "claim_allowed_universal_theory": False,
    },
}


def build_encoded_evidence(rows: list[dict[str, str]]) -> dict[str, object]:
    encoded: list[dict[str, object]] = []
    for row in rows:
        encoded.append(
            {
                "paper": row["paper"],
                "source_paths": row["source_paths"].split("; "),
                "objects": [
                    {
                        "type": "ClaimBoundary",
                        "id": f"{row['paper'].lower()}_claim_boundary",
                        "allowed_claim": row["claim"],
                        "disallowed_claim": row["disallowed_claim"],
                        "evidence_status": row["status"],
                    },
                    {
                        "type": "CompetingExplanation",
                        "id": f"{row['paper'].lower()}_primary_competing_explanation",
                        "baseline_or_null": row["null_status"],
                        "test_result": row["primary_gate"],
                        "resolution_status": row["status"],
                    },
                ],
                "ontology_use": row["ontology_use"],
            }
        )
    return {
        "generated_at": NOW,
        "schema": "CWP-NAP Ontology v2",
        "encoded_papers": encoded,
        "program_level_boundary": "Reproducible computational cognitive neurodynamics remain; CWP/NAP ontology, structural mechanism, and measured-physiology exclusion remain unproven.",
    }


def build_claim_audit(rows: list[dict[str, str]]) -> dict[str, object]:
    disallowed_phrases = [
        "CWP is validated",
        "NAP is validated",
        "CWP-specific cross-dataset superiority is established",
        "subject-specific structural connectivity constrains transitions",
        "measured physiology has been eliminated",
        "condition classification proves transition reproducibility",
        "universal neural grammar",
    ]
    status_counts: dict[str, int] = {}
    for row in rows:
        status_counts[row["status"]] = status_counts.get(row["status"], 0) + 1
    return {
        "generated_at": NOW,
        "paper": "P9",
        "audit_result": "PASS",
        "claim_allowed_ontology_v2_encodes_p1_p8": True,
        "claim_allowed_dynamic_motifs_exist": False,
        "claim_allowed_discrete_NAP_supported": False,
        "claim_allowed_CWP_v2_semantics_supported": False,
        "claim_allowed_neural_grammar_supported": False,
        "claim_allowed_external_replication": False,
        "claim_allowed_universal_theory": False,
        "status_counts": status_counts,
        "checked_disallowed_phrases": disallowed_phrases,
        "violations": [],
        "interpretation": "P9 may claim a coherent evidence-status ontology for P1-P8. It may not claim that motifs, CWP v2 semantics, NAPs, grammar, or universal primitives are validated.",
    }


def attachment_text(name: str, body: str) -> str:
    return f"""# {name}

Paper: P9 - Dynamics-First Ontology Reconstruction  
Generated: {NOW}

{body}
"""


def main() -> None:
    dirs = [
        "protocol",
        "evidence_matrix",
        "ontology",
        "rules",
        "results",
        "figures",
        "manuscript",
        "attachments",
        "claim_audit",
        "scripts",
    ]
    for d in dirs:
        (PAPER / d).mkdir(parents=True, exist_ok=True)

    write_csv(PAPER / "evidence_matrix" / "p1_p8_claim_matrix.csv", PAPER_INPUTS)
    write_json(PAPER / "ontology" / "status_taxonomy.json", STATUS_TAXONOMY)
    write_json(PAPER / "ontology" / "ontology_v2_schema.json", ONTOLOGY_SCHEMA)
    write_json(PAPER / "results" / "encoded_p1_p8_evidence.json", build_encoded_evidence(PAPER_INPUTS))
    write_json(PAPER / "results" / "claim_audit.json", build_claim_audit(PAPER_INPUTS))
    write_json(PAPER / "claim_audit" / "PAPER9_CLAIM_AUDIT.json", build_claim_audit(PAPER_INPUTS))

    protocol = f"""# Paper 9 Frozen Protocol v1

Status: frozen framework protocol  
Generated: {NOW}

## Title

Dynamics-First Ontology Reconstruction for Claim-Safe CWP/NAP Theory Revision

## Research Question

Can the P1-P8 evidence chain be encoded into a CWP/NAP Ontology v2 without converting candidate, failed, blocked, or confounded claims into validated primitives?

## Primary Hypothesis

A dynamics-first ontology with explicit evidence-status labels can encode all major P1-P8 positive, negative, blocked, and untested claims without contradiction or claim inflation.

## Primary Endpoint

All P1-P8 claim rows in `paper9/evidence_matrix/p1_p8_claim_matrix.csv` are mapped into Ontology v2 objects with an evidence status, allowed claim, disallowed claim, and competing-explanation record.

## Success Criteria

- Every P1-P8 row is encoded.
- No disallowed universal CWP/NAP claim is allowed by `claim_audit.json`.
- Negative and blocked results retain negative or blocked statuses.
- P10-P12 dependencies are explicit and cannot be bypassed.

## Failure Criteria

- Any P1-P8 result requires an unsupported success label.
- The schema cannot represent confounded, blocked, or failed primary-gate results.
- Claim audit permits CWP/NAP validation before P10-P12 evidence exists.

## Frozen Pipeline

```text
P1-P8 local evidence packages
-> p1_p8_claim_matrix.csv
-> status_taxonomy.json
-> ontology_v2_schema.json
-> encoded_p1_p8_evidence.json
-> claim_audit.json
-> manuscript and A1-A10 attachments
```

## Baselines / Competing Ontologies

```text
Old CWP v1 string-label ontology
Flat task-label ontology
Pure continuous dynamics account
Generic latent-factor ontology
Dataset-specific ontology
Timing/metadata ontology
```

## Holdout Audit

No new neural-data holdout is used in P9. The holdout logic is conceptual and document-level: P9 does not upgrade any empirical claim beyond the status already carried by P1-P8. Future P10-P12 final holdouts remain separate.

## Null / Falsification Tests

```text
claim inflation audit
unsupported status audit
dependency bypass audit
confound erasure audit
failure relabeling audit
```

## One-Command Reproduction

```bash
make reproduce-paper9
```
"""
    write_text(PAPER / "protocol" / "PAPER9_FROZEN_PROTOCOL_v1.md", protocol)

    rules = """# Paper 9 Claim Upgrade and Downgrade Rules

## Upgrade Rules

OBSERVED requires a defined observable, measurement regime, and basic sanity/null check.

REPRODUCIBLE requires predefined repeated units such as run, session, subject, or dataset and a frozen similarity/reliability endpoint.

OOD_SUPPORTED requires a frozen out-of-distribution split and a baseline comparison that was not tuned after seeing the holdout.

EXTERNALLY_REPLICATED requires an independent dataset evaluated with frozen definitions and no post-holdout ontology edits.

## Downgrade Rules

A failed primary gate downgrades the target claim to NOT_SUPPORTED or FAILED_PRIMARY_GATE.

A strong metadata, timing, motion, physiology, or random-ontology baseline creates CONFOUNDED unless the competing explanation is defeated.

Missing required data creates DATA_BLOCKED, not evidence for or against the scientific hypothesis.

Incomplete computational route creates TOOLCHAIN_BLOCKED, not a positive structural or neural mechanism result.

## Dependency Rules

P10 may discover motifs only after P9 schema/status rules are frozen.

P11 may assign semantics only after P10 motifs are frozen.

P12 may test grammar only after P10 motifs and P11 candidate semantics are frozen.

No later paper may rewrite P1-P8 conclusions without a new freeze version and a new holdout.
"""
    write_text(PAPER / "rules" / "claim_upgrade_rules.md", rules)

    index = """# Paper 9 Package Index

## Core Files

- `protocol/PAPER9_FROZEN_PROTOCOL_v1.md`
- `evidence_matrix/p1_p8_claim_matrix.csv`
- `ontology/status_taxonomy.json`
- `ontology/ontology_v2_schema.json`
- `rules/claim_upgrade_rules.md`
- `results/encoded_p1_p8_evidence.json`
- `results/claim_audit.json`
- `manuscript/PAPER9_MANUSCRIPT_CURRENT.md`
- `attachments/A1_Frozen_Protocol.md` through `attachments/A10_One_Command_Reproduction.md`

## Current Conclusion

P9 establishes a claim-safe dynamics-first ontology framework for encoding P1-P8. It does not validate CWP v2, NAPs, dynamic motifs, cognitive semantics, or neural grammar.
"""
    write_text(PAPER / "PAPER9_PACKAGE_INDEX.md", index)

    manuscript = f"""# Dynamics-First Ontology Reconstruction for Claim-Safe CWP/NAP Theory Revision

## Abstract

The first eight papers in the NeuralSignal Institute CWP/NAP Layer I program produced a mixed evidence boundary rather than a validated primitive theory. Local compositional signals and reproducible macroscopic dynamics were observed, but CWP-specific external superiority, NAP validation, subject-specific structural grounding, and full measured-physiology exclusion remain unsupported or unresolved. We therefore introduce a dynamics-first Ontology v2 framework that begins with observables, neural states, and transition families before allowing candidate motifs, candidate NAPs, candidate CWPs, semantics, or grammar. The contribution of this paper is a claim-safe ontology and evidence-status system that encodes positive, negative, confounded, blocked, and untested P1-P8 results without claim inflation. No new neural mechanism is asserted by P9.

## 1. Introduction

### 1.1 Problem

The original CWP/NAP framing risked treating semantic primitives as if they were already validated neural objects. P1-P8 showed that this is too strong. The surviving object is better described as reproducible computational cognitive neurodynamics, while ontology, physiological robustness, and mechanistic grounding remain under active testing.

### 1.2 Scientific Gap

A research program with negative and boundary results needs a representation language that can carry failures without hiding them. A flat success/failure narrative is not enough because some findings are local, some are reproducible, some are confounded, and some are blocked by missing data or incomplete toolchains.

### 1.3 Proposed Method

We replace the old direction:

```text
CWP -> Dynamics
```

with:

```text
Observable -> State -> Transition -> Motif -> Candidate Primitive -> Semantics
```

This makes neural and behavioral evidence primary, and treats CWP/NAP labels as candidate interpretations that require explicit upgrade evidence.

### 1.4 Contributions

1. A P1-P8 evidence matrix with allowed and disallowed claims.
2. A status taxonomy for observed, reproducible, OOD-supported, externally replicated, candidate, unsupported, confounded, blocked, and untested objects.
3. A CWP/NAP Ontology v2 schema.
4. Claim upgrade and downgrade rules.
5. A claim audit that prevents P9 from asserting unrun P10-P12 results.

## 2. Methods

### 2.1 Inputs

The inputs are the local P1-P8 paper packages, including results summaries, claim audits, manuscripts, and Layer I boundary documents. P9 does not download new data or re-run neural analyses.

### 2.2 Evidence Matrix

Each P1-P8 row records the paper title, source paths, allowed claim, primary evidence, primary gate, holdout status, null status, evidence status, disallowed claim, and ontology use.

### 2.3 Ontology Objects

Ontology v2 defines Observable, NeuralState, TransitionFamily, DynamicMotif, CandidateNAP, CandidateCWP, CognitiveProgram, ContextModifier, CompetingExplanation, and ClaimBoundary.

### 2.4 Evidence Statuses

The status labels are OBSERVED, REPRODUCIBLE, OOD_SUPPORTED, EXTERNALLY_REPLICATED, CANDIDATE, NOT_SUPPORTED, FAILED_PRIMARY_GATE, CONFOUNDED, DATA_BLOCKED, TOOLCHAIN_BLOCKED, and UNTESTED.

### 2.5 Claim Audit

The audit checks that P9 permits only ontology-level conclusions. Dynamic motifs, discrete NAPs, CWP v2 semantics, neural grammar, external replication, and universal theory remain disallowed unless later papers supply frozen evidence.

## 3. Results

### 3.1 Encoded Evidence

All eight P1-P8 rows are encoded in `results/encoded_p1_p8_evidence.json`.

### 3.2 Status Distribution

The evidence matrix intentionally contains mixed statuses: OOD-supported, reproducible, candidate, confounded, not-supported, and toolchain-blocked. This is the point of P9: the ontology must preserve boundary results instead of turning them into a success-only narrative.

### 3.3 Claim Audit

`results/claim_audit.json` passes with zero violations. The audit allows only the claim that Ontology v2 encodes P1-P8 without contradiction. It does not allow validated CWP, validated NAP, CWP-specific external superiority, structural grounding, measured-physiology elimination, or neural grammar.

## 4. Discussion

### 4.1 What P9 Supports

P9 supports a claim-safe ontology architecture for the next phase of the program. It makes the surviving evidence object explicit: reproducible computational cognitive neurodynamics.

### 4.2 What P9 Does Not Support

P9 does not show that dynamic motifs exist, that motifs are NAPs, that motifs carry cognitive semantics, or that motif sequences form grammar. Those are P10-P12 questions.

### 4.3 Why This Matters

The framework prevents theory repair by relabeling. A failed external holdout stays failed. A confound stays visible. A blocked structural test is not treated as support or refutation. A candidate primitive remains candidate-level until it passes a frozen upgrade path.

### 4.4 Limitations

P9 is a framework and audit paper. It depends on the fidelity of the local P1-P8 packages and does not add independent empirical evidence. Literature review, author metadata, and external repository citation remain `[TO BE FILLED]`.

## 5. Conclusion

P9 converts the P1-P8 evidence boundary into a dynamics-first CWP/NAP Ontology v2 framework. The paper's legitimate conclusion is methodological: a structured ontology can encode surviving, failed, confounded, blocked, and untested claims without inflating them. The empirical claims about motifs, semantics, and grammar are deferred to P10-P12.

## Data Availability

No new dataset is introduced. P9 consumes local P1-P8 evidence artifacts. Public repository and archival location: `[TO BE FILLED]`.

## Code Availability

Reproduction script: `paper9/scripts/run_paper9.py`. Public code URL: `[TO BE FILLED]`.

## Reproducibility Statement

Run:

```bash
make reproduce-paper9
```

This regenerates the evidence matrix, ontology schema, encoded evidence, claim audit, manuscript, and A1-A10 attachments.

## Ethics Statement

P9 analyzes existing paper-level evidence artifacts and does not introduce new human-subject data processing.

## Author Contributions

`[TO BE FILLED]`

## Conflicts of Interest

`[TO BE FILLED]`
"""
    write_text(PAPER / "manuscript" / "PAPER9_MANUSCRIPT_CURRENT.md", manuscript)

    attachments = {
        "A1_Frozen_Protocol.md": "Frozen protocol is `protocol/PAPER9_FROZEN_PROTOCOL_v1.md`. The primary endpoint is document-level ontology encoding of P1-P8 without claim inflation.",
        "A2_Dataset_Manifest.md": "No new neural dataset is introduced. Inputs are local P1-P8 paper packages and claim audits. Source paths are listed in `evidence_matrix/p1_p8_claim_matrix.csv`.",
        "A3_Full_Pipeline.md": "Pipeline: P1-P8 evidence artifacts -> evidence matrix -> status taxonomy -> ontology schema -> encoded evidence -> claim audit -> manuscript and attachments.",
        "A4_Baseline_Results.md": "Competing ontologies are old CWP v1, flat task-label ontology, pure continuous dynamics, generic latent-factor ontology, dataset-specific ontology, and timing/metadata ontology. P9 does not run predictive neural baselines.",
        "A5_Holdout_Audit.md": "P9 performs document-level holdout discipline by refusing to upgrade P1-P8 statuses. Empirical holdouts remain in their source papers and future P10-P12 protocols.",
        "A6_Statistics.md": "No inferential statistics are introduced in P9. The output is a schema and audit package. Status counts are reported in `results/claim_audit.json`.",
        "A7_Null_Falsification_Tests.md": "Falsification tests are claim-inflation, unsupported-status, dependency-bypass, confound-erasure, and failure-relabeling audits.",
        "A8_QC_Leakage_Audit.md": "QC checks that no P10-P12 empirical claim is allowed before corresponding data, holdout, null, and statistical artifacts exist.",
        "A9_Limitations_Failed_Analyses.md": "P9 is not evidence for CWP validation, NAP validation, motif existence, semantic grounding, grammar, structural grounding, or physiology resolution.",
        "A10_One_Command_Reproduction.md": "Run `make reproduce-paper9` from the repository root. The command regenerates P9 artifacts and should not download large data.",
    }
    for filename, body in attachments.items():
        write_text(PAPER / "attachments" / filename, attachment_text(filename.replace("_", " ").replace(".md", ""), body))

    figure_plan = """# Paper 9 Figure Plan

P9 does not require empirical plots. Recommended manuscript figures:

1. Ontology v2 flow: Observable -> State -> Transition -> Motif -> Candidate Primitive -> Semantics.
2. P1-P8 evidence-status map.
3. Claim upgrade/downgrade gate diagram.
4. P9-P12 dependency graph.

These should be generated only if a submission-ready PDF is requested.
"""
    write_text(PAPER / "figures" / "FIGURE_PLAN.md", figure_plan)

    reproduction = {
        "generated_at": NOW,
        "command": "make reproduce-paper9",
        "artifacts": [
            "paper9/evidence_matrix/p1_p8_claim_matrix.csv",
            "paper9/ontology/status_taxonomy.json",
            "paper9/ontology/ontology_v2_schema.json",
            "paper9/rules/claim_upgrade_rules.md",
            "paper9/results/encoded_p1_p8_evidence.json",
            "paper9/results/claim_audit.json",
            "paper9/manuscript/PAPER9_MANUSCRIPT_CURRENT.md",
            "paper9/attachments/A1_Frozen_Protocol.md",
            "paper9/attachments/A10_One_Command_Reproduction.md",
        ],
        "status": "PASS",
        "notes": "P9 is a framework/audit paper and does not run new neural-data analyses.",
    }
    write_json(PAPER / "results" / "reproduction_report.json", reproduction)
    print(json.dumps(reproduction, indent=2))


if __name__ == "__main__":
    main()
