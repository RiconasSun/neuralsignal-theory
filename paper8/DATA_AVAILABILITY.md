# P8 Data and Figure Availability

Publication documentation added 2026-10-10; scientific results are unchanged.

## Original Data

Raw participant imaging/signals and tractography are not redistributed. Figures are derived results or conceptual diagrams, not substitutes for downloadable source data.

- [HCP-YA](https://www.humanconnectome.org/study/hcp-young-adult/document/hcp-young-adult-2025-release): 2025 release named in local protocols; inspect download manifests for actual package keys. Access/license: HCP/BALSA authorized access and data-use terms.
- [ds005795](https://openneuro.org/datasets/ds005795): 1.0.0. Access/license: See provider dataset license.
  Dataset DOI recorded locally: [doi:10.18112/openneuro.ds005795.v1.0.0](https://doi.org/10.18112/openneuro.ds005795.v1.0.0).
NEMAR mirror: [on005795](https://www.nemar.org/dataset/on005795), version v1.0.0; [manifest](https://data.nemar.org/on005795/v1.0.0/manifest.json).

Provider-link verification and historical version distinctions: [source registry](../publication/SOURCE_REGISTRY.md). The registry separates current metadata from the versions recorded by these analyses.

## Samples, Processing, and Access

The following existing records define actual selected subjects/runs, splits, exclusions, pipeline parameters and data access. Candidate inventories do not establish that every candidate was analyzed.

- [paper8/attachments/A10_One_Command_Reproduction.md](https://github.com/RiconasSun/neuralsignal-theory/tree/test/paper8/attachments/A10_One_Command_Reproduction.md)
- [paper8/attachments/A2_Dataset_Manifest.md](https://github.com/RiconasSun/neuralsignal-theory/tree/test/paper8/attachments/A2_Dataset_Manifest.md)
- [paper8/attachments/A3_Full_Pipeline.md](https://github.com/RiconasSun/neuralsignal-theory/tree/test/paper8/attachments/A3_Full_Pipeline.md)
- [paper8/attachments/A5_Holdout_Audit.md](https://github.com/RiconasSun/neuralsignal-theory/tree/test/paper8/attachments/A5_Holdout_Audit.md)
- [paper8/attachments/A8_QC_Leakage_Audit.md](https://github.com/RiconasSun/neuralsignal-theory/tree/test/paper8/attachments/A8_QC_Leakage_Audit.md)
- [paper8/protocol/PAPER8_FROZEN_PROTOCOL_v0_1.md](https://github.com/RiconasSun/neuralsignal-theory/tree/test/paper8/protocol/PAPER8_FROZEN_PROTOCOL_v0_1.md)
- [paper8/results/p8_e1_hcp_wm_physio_download.json](https://github.com/RiconasSun/neuralsignal-theory/tree/test/paper8/results/p8_e1_hcp_wm_physio_download.json)
- [paper8/results/p8_final_extension_ds005795_manifest_audit.json](https://github.com/RiconasSun/neuralsignal-theory/tree/test/paper8/results/p8_final_extension_ds005795_manifest_audit.json)
- [paper8/results/p8_final_extension_ds005795_smoke_download.json](https://github.com/RiconasSun/neuralsignal-theory/tree/test/paper8/results/p8_final_extension_ds005795_smoke_download.json)

Exact local withheld filenames and SHA256 values are in [raw_file_inventory.csv](../publication/raw_file_inventory.csv). This inventory describes files present at publication, not a reconstructed historical cohort. Missing historical raw files and unrecorded download revisions cannot be recovered from a checksum of current derived data.

For raw reproduction, obtain the indicated dataset release under its license, place files at the paths expected by the original manifests/scripts, and follow A3/A10. HCP requires your own authorized account; credentials remain local. A derived-data rerun does not prove raw-data preprocessing was reproduced.

## Figures and Generation

| Figure | Generator Command | Analysis Inputs (Script Scope) | Mapping |
| --- | --- | --- | --- |
| [paper8/figures/figure1_p8_nuisance_ladder_transition_contrast.png](https://github.com/RiconasSun/neuralsignal-theory/tree/test/paper8/figures/figure1_p8_nuisance_ladder_transition_contrast.png) | `python paper8/scripts/make_paper8_figures.py`<br>`python paper8/scripts/paper8_make_manuscript_pdf.py` | [paper8/results/p8_e1_e6_hcp_physio_ladder_smoke.json](https://github.com/RiconasSun/neuralsignal-theory/tree/test/paper8/results/p8_e1_e6_hcp_physio_ladder_smoke.json)<br>[paper8/results/p8_manuscript_pdf.json](https://github.com/RiconasSun/neuralsignal-theory/tree/test/paper8/results/p8_manuscript_pdf.json) | Literal figure name in source; inputs are script-wide, inspect function for panel subset |
| [paper8/figures/figure2_p8_nuisance_ladder_classification.png](https://github.com/RiconasSun/neuralsignal-theory/tree/test/paper8/figures/figure2_p8_nuisance_ladder_classification.png) | `python paper8/scripts/make_paper8_figures.py`<br>`python paper8/scripts/paper8_make_manuscript_pdf.py` | [paper8/results/p8_e1_e6_hcp_physio_ladder_smoke.json](https://github.com/RiconasSun/neuralsignal-theory/tree/test/paper8/results/p8_e1_e6_hcp_physio_ladder_smoke.json)<br>[paper8/results/p8_manuscript_pdf.json](https://github.com/RiconasSun/neuralsignal-theory/tree/test/paper8/results/p8_manuscript_pdf.json) | Literal figure name in source; inputs are script-wide, inspect function for panel subset |
| [paper8/figures/figure3_p8_v2_transition_nulls.png](https://github.com/RiconasSun/neuralsignal-theory/tree/test/paper8/figures/figure3_p8_v2_transition_nulls.png) | `python paper8/scripts/make_paper8_v2_figures.py`<br>`python paper8/scripts/paper8_make_manuscript_pdf.py` | [paper8/results/p8_manuscript_pdf.json](https://github.com/RiconasSun/neuralsignal-theory/tree/test/paper8/results/p8_manuscript_pdf.json)<br>[paper8/results/p8_v2_signal_separation_audit.json](https://github.com/RiconasSun/neuralsignal-theory/tree/test/paper8/results/p8_v2_signal_separation_audit.json) | Literal figure name in source; inputs are script-wide, inspect function for panel subset |
| [paper8/figures/figure4_p8_v2_classification_nulls.png](https://github.com/RiconasSun/neuralsignal-theory/tree/test/paper8/figures/figure4_p8_v2_classification_nulls.png) | `python paper8/scripts/make_paper8_v2_figures.py`<br>`python paper8/scripts/paper8_make_manuscript_pdf.py` | [paper8/results/p8_manuscript_pdf.json](https://github.com/RiconasSun/neuralsignal-theory/tree/test/paper8/results/p8_manuscript_pdf.json)<br>[paper8/results/p8_v2_signal_separation_audit.json](https://github.com/RiconasSun/neuralsignal-theory/tree/test/paper8/results/p8_v2_signal_separation_audit.json) | Literal figure name in source; inputs are script-wide, inspect function for panel subset |
| [paper8/figures/figure5_p8_ds005795_streaming_nuisance_ladder.png](https://github.com/RiconasSun/neuralsignal-theory/tree/test/paper8/figures/figure5_p8_ds005795_streaming_nuisance_ladder.png) | `python paper8/scripts/make_paper8_ds005795_streaming_figure.py`<br>`python paper8/scripts/paper8_make_manuscript_pdf.py` | [paper8/results/p8_ds005795_streaming_figure.json](https://github.com/RiconasSun/neuralsignal-theory/tree/test/paper8/results/p8_ds005795_streaming_figure.json)<br>[paper8/results/p8_final_extension_ds005795_streaming_nuisance_ladder.json](https://github.com/RiconasSun/neuralsignal-theory/tree/test/paper8/results/p8_final_extension_ds005795_streaming_nuisance_ladder.json)<br>[paper8/results/p8_manuscript_pdf.json](https://github.com/RiconasSun/neuralsignal-theory/tree/test/paper8/results/p8_manuscript_pdf.json) | Literal figure name in source; inputs are script-wide, inspect function for panel subset |

Generation commands may rerun analyses or contact source providers; inspect A10 and prerequisites before running. They are source mappings, not evidence of a fresh scientific rerun.

## Publication Record

Code and artifacts: [neuralsignal-theory/test](https://github.com/RiconasSun/neuralsignal-theory/tree/test).

See [publication inventory](../publication/artifact_checksums.csv) for SHA256 values. Historical submission PDFs preserve earlier text; this guide and the current Markdown manuscript carry the updated availability supplement.
