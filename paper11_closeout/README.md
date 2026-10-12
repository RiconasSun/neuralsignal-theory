# P11 Exploratory Manuscript Package

Separate mission:P11-MANUSCRIPT-CLOSEOUT-1. Completed scholarly reporting of
existing evidence, NOT originalR3, independent biological validation or a
retrospective PASS for any original failure.

## Deliverables

- `output/manuscript.pdf` and editable `output/manuscript.md`:main paper.
- `output/supplement.pdf` and Markdown:all57configurations, all patient effects,
  saved conditional intervals, coverage, optimizer summaries and failures.
- `output/figures/`:seven300DPI PNG and vectorPDF figures with hashed input/data
  sidecars. `figure_manifest.json` records exact output identities.
- `output/tables/`:full-precision CSVs, including all3887optimizer records.
- `output/attachments/A1.md` through `A10.md`:evidence and reproducibility.
- `CLAIM_AUDIT.md`, `output/claim_map.json`, `output/LIMITATIONS.md`:boundaries.
- `evidence/`:actual saved-only PowerShell execution,21tests, reference checks,
  manuscript-only gate, QC and rendered page metrics.
- `evidence_freeze.json`:all original input/prior-file hashes. Existing scientific
  files remain byte-identical. OriginalR2FAIL/DATA_INSUFFICIENT andR3NOTEXECUTED.

## One Command

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\paper11_closeout\reproduce.ps1
```

Run from a repository checkout with the frozen saved source summaries present.
The package archive is a delivery bundle, not a standalone redistribution of
the original datasets/repository. It never includes raw spikes or final outcomes.
Read REPRODUCTION.md for runtimes, comparison policy and no-network boundaries.

Verdict:MANUSCRIPT_COMPLETE;SCIENTIFIC_VALIDATION_PASS=false.
Submission readiness:false until named authors/declarations are approved.
Stop here; no new dataset search, scientific rescue or model fitting.
