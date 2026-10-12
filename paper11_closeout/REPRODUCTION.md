# Saved-results-only Reproduction

Run this single PowerShell command from the repository root:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\paper11_closeout\reproduce.ps1
```

The execution-policy flag applies only to that child process, not user/machine
policy. It accommodates the previously observed Windows PowerShell5.1 script
restriction without changing permanent settings. An existing permissive host
can also execute `& .\paper11_closeout\reproduce.ps1`.

The script validates frozen summary hashes, regenerates the seven figures,
tables, manuscript, supplement, equations and A1-A10 into the separate ignored
`paper11_closeout/reproduction/` directory, generates the two paginated PDFs,
runs document/data/claim tests and compares the resulting artifact hashes with
the sealed publication outputs. It writes an execution and reproducibility
receipt under that directory. No scientific model runner is imported.

The command does NOT download datasets or metadata, preprocess spikes, fit
models, select new candidates, recompute confidence intervals/sign-flip tests,
run null controls or unlock/evaluate a final holdout. It faithfully formats
recorded exploratory results. A successful replay does not execute experiments
that were incomplete and does not change any scientific gate.

Default runtimes on this workstation:
- Primary plotting/consistency runtime: Hermes Python3.11 venv, Matplotlib,
  NumPy and Pillow. `-Python` overrides its executable.
- Paged-document runtime: Codex bundled Python, ReportLab/Pillow/pypdf.
  `-PdfPython` overrides its executable.
- Recorded local source versions are emitted by the reproduction driver.
  No dependency installation or network fallback occurs during reproduction.

`visual_qa.py` separately renders every final PDF page using bundled Poppler,
checks nonblank pixels and glyph bounds, and makes contact sheets. It is a
formatting QA operation, not an experimental analysis. Published output hashes,
figure sidecars, claim_map and reference receipts bind the paper to saved input
SHA256 values. Prior tracked evidence is verified at closeout freeze/final
closure; runtime replay verifies its allowlisted source summaries and code.

Administrative author/funding/conflict/submission approval remains unprovided.
Those disclosures are explicit in the manuscript; no submission-ready status
or scientific validation is inferred from documentation completion.
