# P9 Data and Figure Availability

Publication documentation added 2026-10-10; scientific results are unchanged.

## Original Data

Raw participant imaging/signals and tractography are not redistributed. Figures are derived results or conceptual diagrams, not substitutes for downloadable source data.

P9 introduces no raw dataset; its inputs are P1-P8 evidence artifacts and claim audits, not a new participant cohort.

Provider-link verification and historical version distinctions: [source registry](../publication/SOURCE_REGISTRY.md). The registry separates current metadata from the versions recorded by these analyses.

## Samples, Processing, and Access

The following existing records define actual selected subjects/runs, splits, exclusions, pipeline parameters and data access. Candidate inventories do not establish that every candidate was analyzed.

- [paper9/attachments/A10_One_Command_Reproduction.md](https://github.com/RiconasSun/neuralsignal-theory/tree/test/paper9/attachments/A10_One_Command_Reproduction.md)
- [paper9/attachments/A2_Dataset_Manifest.md](https://github.com/RiconasSun/neuralsignal-theory/tree/test/paper9/attachments/A2_Dataset_Manifest.md)
- [paper9/attachments/A3_Full_Pipeline.md](https://github.com/RiconasSun/neuralsignal-theory/tree/test/paper9/attachments/A3_Full_Pipeline.md)
- [paper9/attachments/A5_Holdout_Audit.md](https://github.com/RiconasSun/neuralsignal-theory/tree/test/paper9/attachments/A5_Holdout_Audit.md)
- [paper9/attachments/A8_QC_Leakage_Audit.md](https://github.com/RiconasSun/neuralsignal-theory/tree/test/paper9/attachments/A8_QC_Leakage_Audit.md)
- [paper9/protocol/PAPER9_FROZEN_PROTOCOL_v1.md](https://github.com/RiconasSun/neuralsignal-theory/tree/test/paper9/protocol/PAPER9_FROZEN_PROTOCOL_v1.md)

Exact local withheld filenames and SHA256 values are in [raw_file_inventory.csv](../publication/raw_file_inventory.csv). This inventory describes files present at publication, not a reconstructed historical cohort. Missing historical raw files and unrecorded download revisions cannot be recovered from a checksum of current derived data.

For raw reproduction, obtain the indicated dataset release under its license, place files at the paths expected by the original manifests/scripts, and follow A3/A10. HCP requires your own authorized account; credentials remain local. A derived-data rerun does not prove raw-data preprocessing was reproduced.

## Figures and Generation

| Figure | Generator Command | Analysis Inputs (Script Scope) | Mapping |
| --- | --- | --- | --- |
| [paper9/figures/figure1_ontology_flow.png](https://github.com/RiconasSun/neuralsignal-theory/tree/test/paper9/figures/figure1_ontology_flow.png) | `python paper9/scripts/finalize_paper9_submission.py` | [paper9/results/claim_audit.json](https://github.com/RiconasSun/neuralsignal-theory/tree/test/paper9/results/claim_audit.json)<br>[paper9/results/p9_pdf_generation.json](https://github.com/RiconasSun/neuralsignal-theory/tree/test/paper9/results/p9_pdf_generation.json)<br>[paper9/submission/SUBMISSION_READINESS.json](https://github.com/RiconasSun/neuralsignal-theory/tree/test/paper9/submission/SUBMISSION_READINESS.json) | Literal figure name in source; inputs are script-wide, inspect function for panel subset |
| [paper9/figures/figure2_evidence_status_map.png](https://github.com/RiconasSun/neuralsignal-theory/tree/test/paper9/figures/figure2_evidence_status_map.png) | `python paper9/scripts/finalize_paper9_submission.py` | [paper9/results/claim_audit.json](https://github.com/RiconasSun/neuralsignal-theory/tree/test/paper9/results/claim_audit.json)<br>[paper9/results/p9_pdf_generation.json](https://github.com/RiconasSun/neuralsignal-theory/tree/test/paper9/results/p9_pdf_generation.json)<br>[paper9/submission/SUBMISSION_READINESS.json](https://github.com/RiconasSun/neuralsignal-theory/tree/test/paper9/submission/SUBMISSION_READINESS.json) | Literal figure name in source; inputs are script-wide, inspect function for panel subset |
| [paper9/figures/figure3_claim_gates.png](https://github.com/RiconasSun/neuralsignal-theory/tree/test/paper9/figures/figure3_claim_gates.png) | `python paper9/scripts/finalize_paper9_submission.py` | [paper9/results/claim_audit.json](https://github.com/RiconasSun/neuralsignal-theory/tree/test/paper9/results/claim_audit.json)<br>[paper9/results/p9_pdf_generation.json](https://github.com/RiconasSun/neuralsignal-theory/tree/test/paper9/results/p9_pdf_generation.json)<br>[paper9/submission/SUBMISSION_READINESS.json](https://github.com/RiconasSun/neuralsignal-theory/tree/test/paper9/submission/SUBMISSION_READINESS.json) | Literal figure name in source; inputs are script-wide, inspect function for panel subset |
| [paper9/figures/figure4_dependency_graph.png](https://github.com/RiconasSun/neuralsignal-theory/tree/test/paper9/figures/figure4_dependency_graph.png) | `python paper9/scripts/finalize_paper9_submission.py` | [paper9/results/claim_audit.json](https://github.com/RiconasSun/neuralsignal-theory/tree/test/paper9/results/claim_audit.json)<br>[paper9/results/p9_pdf_generation.json](https://github.com/RiconasSun/neuralsignal-theory/tree/test/paper9/results/p9_pdf_generation.json)<br>[paper9/submission/SUBMISSION_READINESS.json](https://github.com/RiconasSun/neuralsignal-theory/tree/test/paper9/submission/SUBMISSION_READINESS.json) | Literal figure name in source; inputs are script-wide, inspect function for panel subset |

Generation commands may rerun analyses or contact source providers; inspect A10 and prerequisites before running. They are source mappings, not evidence of a fresh scientific rerun.

## Publication Record

Code and artifacts: [neuralsignal-theory/test](https://github.com/RiconasSun/neuralsignal-theory/tree/test).

See [publication inventory](../publication/artifact_checksums.csv) for SHA256 values. Historical submission PDFs preserve earlier text; this guide and the current Markdown manuscript carry the updated availability supplement.
