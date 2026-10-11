# P6 Data and Figure Availability

Publication documentation added 2026-10-10; scientific results are unchanged.

## Original Data

Raw participant imaging/signals and tractography are not redistributed. Figures are derived results or conceptual diagrams, not substitutes for downloadable source data.

- [ds004117](https://openneuro.org/datasets/ds004117): Dataset DOI version 1.0.1; BIDS format version 1.7.0 is not a release identifier; exact download commit not recorded. Access/license: CC0 per local P6 audit and provider metadata.
  Dataset DOI recorded locally: [doi:10.18112/openneuro.ds004117.v1.0.1](https://doi.org/10.18112/openneuro.ds004117.v1.0.1).
- [ds004752](https://openneuro.org/datasets/ds004752): Dataset DOI version 1.0.1; BIDS format version 1.4.0 is not a release identifier; exact download commit not recorded. Access/license: CC0 per local P6 audit and provider metadata.
  Dataset DOI recorded locally: [doi:10.18112/openneuro.ds004752.v1.0.1](https://doi.org/10.18112/openneuro.ds004752.v1.0.1).

Provider-link verification and historical version distinctions: [source registry](../publication/SOURCE_REGISTRY.md). The registry separates current metadata from the versions recorded by these analyses.

## Samples, Processing, and Access

The following existing records define actual selected subjects/runs, splits, exclusions, pipeline parameters and data access. Candidate inventories do not establish that every candidate was analyzed.

- [paper6/attachments/A10_One_Command_Reproduction.md](https://github.com/RiconasSun/neuralsignal-theory/tree/test/paper6/attachments/A10_One_Command_Reproduction.md)
- [paper6/attachments/A2_Dataset_Manifest.md](https://github.com/RiconasSun/neuralsignal-theory/tree/test/paper6/attachments/A2_Dataset_Manifest.md)
- [paper6/attachments/A3_Full_Pipeline.md](https://github.com/RiconasSun/neuralsignal-theory/tree/test/paper6/attachments/A3_Full_Pipeline.md)
- [paper6/attachments/A5_Holdout_Audit.md](https://github.com/RiconasSun/neuralsignal-theory/tree/test/paper6/attachments/A5_Holdout_Audit.md)
- [paper6/attachments/A8_QC_Leakage_Audit.md](https://github.com/RiconasSun/neuralsignal-theory/tree/test/paper6/attachments/A8_QC_Leakage_Audit.md)
- [paper6/protocol/PAPER6_FROZEN_PROTOCOL_v0_1.md](https://github.com/RiconasSun/neuralsignal-theory/tree/test/paper6/protocol/PAPER6_FROZEN_PROTOCOL_v0_1.md)

Exact local withheld filenames and SHA256 values are in [raw_file_inventory.csv](../publication/raw_file_inventory.csv). This inventory describes files present at publication, not a reconstructed historical cohort. Missing historical raw files and unrecorded download revisions cannot be recovered from a checksum of current derived data.

For raw reproduction, obtain the indicated dataset release under its license, place files at the paths expected by the original manifests/scripts, and follow A3/A10. HCP requires your own authorized account; credentials remain local. A derived-data rerun does not prove raw-data preprocessing was reproduced.

## Figures and Generation

| Figure | Generator Command | Analysis Inputs (Script Scope) | Mapping |
| --- | --- | --- | --- |
| [paper6/figures/figure1_pipeline.png](https://github.com/RiconasSun/neuralsignal-theory/tree/test/paper6/figures/figure1_pipeline.png) | `python paper6/scripts/make_p6_figures.py` | [paper6/results/e3_e6_ds004117_full_cohort_batched_results.json](https://github.com/RiconasSun/neuralsignal-theory/tree/test/paper6/results/e3_e6_ds004117_full_cohort_batched_results.json)<br>[paper6/results/e7_ds004752_external_convergent_results.json](https://github.com/RiconasSun/neuralsignal-theory/tree/test/paper6/results/e7_ds004752_external_convergent_results.json) | Literal figure name in source; inputs are script-wide, inspect function for panel subset |
| [paper6/figures/figure2_window_inventory.png](https://github.com/RiconasSun/neuralsignal-theory/tree/test/paper6/figures/figure2_window_inventory.png) | `python paper6/scripts/make_p6_figures.py` | [paper6/results/e3_e6_ds004117_full_cohort_batched_results.json](https://github.com/RiconasSun/neuralsignal-theory/tree/test/paper6/results/e3_e6_ds004117_full_cohort_batched_results.json)<br>[paper6/results/e7_ds004752_external_convergent_results.json](https://github.com/RiconasSun/neuralsignal-theory/tree/test/paper6/results/e7_ds004752_external_convergent_results.json) | Literal figure name in source; inputs are script-wide, inspect function for panel subset |
| [paper6/figures/figure3_e4_reproducibility.png](https://github.com/RiconasSun/neuralsignal-theory/tree/test/paper6/figures/figure3_e4_reproducibility.png) | `python paper6/scripts/make_p6_figures.py` | [paper6/results/e3_e6_ds004117_full_cohort_batched_results.json](https://github.com/RiconasSun/neuralsignal-theory/tree/test/paper6/results/e3_e6_ds004117_full_cohort_batched_results.json)<br>[paper6/results/e7_ds004752_external_convergent_results.json](https://github.com/RiconasSun/neuralsignal-theory/tree/test/paper6/results/e7_ds004752_external_convergent_results.json) | Literal figure name in source; inputs are script-wide, inspect function for panel subset |
| [paper6/figures/figure4_e5_e6_specificity_nulls.png](https://github.com/RiconasSun/neuralsignal-theory/tree/test/paper6/figures/figure4_e5_e6_specificity_nulls.png) | `python paper6/scripts/make_p6_figures.py` | [paper6/results/e3_e6_ds004117_full_cohort_batched_results.json](https://github.com/RiconasSun/neuralsignal-theory/tree/test/paper6/results/e3_e6_ds004117_full_cohort_batched_results.json)<br>[paper6/results/e7_ds004752_external_convergent_results.json](https://github.com/RiconasSun/neuralsignal-theory/tree/test/paper6/results/e7_ds004752_external_convergent_results.json) | Literal figure name in source; inputs are script-wide, inspect function for panel subset |
| [paper6/figures/figure5_subject_accuracy.png](https://github.com/RiconasSun/neuralsignal-theory/tree/test/paper6/figures/figure5_subject_accuracy.png) | `python paper6/scripts/make_p6_figures.py` | [paper6/results/e3_e6_ds004117_full_cohort_batched_results.json](https://github.com/RiconasSun/neuralsignal-theory/tree/test/paper6/results/e3_e6_ds004117_full_cohort_batched_results.json)<br>[paper6/results/e7_ds004752_external_convergent_results.json](https://github.com/RiconasSun/neuralsignal-theory/tree/test/paper6/results/e7_ds004752_external_convergent_results.json) | Literal figure name in source; inputs are script-wide, inspect function for panel subset |
| [paper6/figures/figure6_claim_audit.png](https://github.com/RiconasSun/neuralsignal-theory/tree/test/paper6/figures/figure6_claim_audit.png) | `python paper6/scripts/make_p6_figures.py` | [paper6/results/e3_e6_ds004117_full_cohort_batched_results.json](https://github.com/RiconasSun/neuralsignal-theory/tree/test/paper6/results/e3_e6_ds004117_full_cohort_batched_results.json)<br>[paper6/results/e7_ds004752_external_convergent_results.json](https://github.com/RiconasSun/neuralsignal-theory/tree/test/paper6/results/e7_ds004752_external_convergent_results.json) | Literal figure name in source; inputs are script-wide, inspect function for panel subset |
| [paper6/figures/figure7_e7_external_convergent.png](https://github.com/RiconasSun/neuralsignal-theory/tree/test/paper6/figures/figure7_e7_external_convergent.png) | `python paper6/scripts/make_p6_figures.py` | [paper6/results/e3_e6_ds004117_full_cohort_batched_results.json](https://github.com/RiconasSun/neuralsignal-theory/tree/test/paper6/results/e3_e6_ds004117_full_cohort_batched_results.json)<br>[paper6/results/e7_ds004752_external_convergent_results.json](https://github.com/RiconasSun/neuralsignal-theory/tree/test/paper6/results/e7_ds004752_external_convergent_results.json) | Literal figure name in source; inputs are script-wide, inspect function for panel subset |

Generation commands may rerun analyses or contact source providers; inspect A10 and prerequisites before running. They are source mappings, not evidence of a fresh scientific rerun.

## Publication Record

Code and artifacts: [neuralsignal-theory/test](https://github.com/RiconasSun/neuralsignal-theory/tree/test).

See [publication inventory](../publication/artifact_checksums.csv) for SHA256 values. Historical submission PDFs preserve earlier text; this guide and the current Markdown manuscript carry the updated availability supplement.
