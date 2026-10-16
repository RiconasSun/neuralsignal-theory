# Saved-evidence reproduction and execution boundary

This is a descriptive, post-amendment P13 assessment. The original conditional B* control remains FAILED / UNAVAILABLE; the original recent-event sensitivity retains six eligible final mice against the unchanged minimum of eight. No saved-evidence verification upgrades either failure or validates the affected broad temporal claims.

## Verified Windows environment

The actual scientific execution uses Python 3.11.15, NumPy 2.4.6, SciPy 1.17.1, h5py, Requests and Matplotlib in the existing Hermes virtual environment. Independent differentiation uses the preserved Autograd 1.8.0 installation under `paper13_ki_execution1/work/ad_vendor`. The saved reproduction checks the original source identities and numerical policies rather than substituting a newer solver or derivative policy.

From the repository root, the one-command PowerShell audit is:

```powershell
& .\paper13_descriptive_final1\reproduce_closeout.ps1
```

A separately installed compatible Python can be selected explicitly:

```powershell
& .\paper13_descriptive_final1\reproduce_closeout.ps1 -Python 'C:\path\to\python.exe'
```

This runs 96 unique synthetic regression tests, validates every original pre-D frozen file, the separate saved-audit repair freeze and any final closeout freeze, accounts for the one C execution, and verifies the original score copies/journal/hashes, exact mouse-level statistics and three complete control arrays. It prohibits network access during the tests/audits and does not call real C or D execution. Recomputing statistics from saved per-mouse scores is distinct from computing new predictive likelihoods from neural data.

The original pre-D `audit_saved.py`, `verify_saved.py` and `reproduce.ps1` remain byte-exact historical evidence. Their first actual post-D audit failed after88 tests passed because it incorrectly demanded bitwise equality between two different floating-point reduction orders. The failed receipt is preserved. The separately registered `audit_reduction.py`/`verify_closeout.py` use exact score-copy/journal/hash/statistic checks, exact D/S sums and exact B*/B2 aliases. For the63 baseline/Continuous/alias aggregates, an a priori exact-Fraction forward-error bound reports **conditional compatibility**, assuming unseen per-unit computed log terms are nonpositive. Joint-bin files alone cannot prove that premise or reconstruct individual unit-log floats losslessly. This limitation is explicit; no original score, scientific tolerance, model, null, hypothesis or inference rule changed. The eight added synthetic tests cover the saved-audit correction, exact boundaries, tampering and the missing-premise limitation. See `SAVED_AUDIT_REPAIR_REGISTRATION.json` and the independent review in the mission evidence directory.

## Restore prerequisites on another checkout

For the manual commands below, assign the two runtime paths first. These are the verified installations on the execution workstation; on another machine, replace them with compatible installations:

```powershell
$Python = Join-Path $env:USERPROFILE 'AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe'
$ArtifactPython = Join-Path $env:USERPROFILE '.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
```

The hash-bound original A/C/B/E derived states are in `paper13_ki_execution1/SAVED_DERIVED_STATES.zip`. When absent from their ignored `work` destinations, restore them using:

```powershell
& $Python -B -m paper13_ki_execution1.restore_saved_states
```

This verifies the entire existing archive before writing missing files, preserves existing identical files, and refuses mismatches. It neither requests the source nor fits a model. Obtain the declared Python dependencies and Autograd 1.8.0 before attempting the audit. No portable, dependency-free or fresh-machine verification is implied by the current-workspace reproduction receipt.

Current-mission C coefficients, numerical certificates, trajectories, preprocessing, full-state seal, authorized D derived states, per-bin log scores and reference distributions are committed in this package's `results` tree. Raw full-record range caches remain excluded from Git. Synthetic temporary fixtures are also excluded. Previously failed scientific evidence stays in its original packages.

## Reporting from completed saved results

Only after a valid complete D result exists, the frozen reporter can regenerate the paper tables and figures from saved results. Use a separate ignored output directory so the reviewed, hash-sealed deliverables are preserved:

```powershell
& $Python -B -c "from pathlib import Path; from paper13_descriptive_final1.build_report import prepare; print(prepare(Path('paper13_descriptive_final1/work/rebuilt_manuscript')))"
```

It does not export neural sources, refit models, compute D likelihoods, or generate another real null draw. The frozen PDF renderer uses ReportLab and reads the two Markdown documents:

```powershell
& $ArtifactPython -B -c "from pathlib import Path; from paper13_descriptive_final1.render_pdf import render; p=Path('paper13_descriptive_final1/work/rebuilt_manuscript'); render(p/'Manuscript.md',p/'Manuscript.pdf'); render(p/'Supplement.md',p/'Supplement.pdf',wide=True)"
```

The archived PDFs and their render-QA evidence are the reviewed deliverables. Byte-identical future PDF/SVG rendering is not asserted: renderer metadata and library versions can vary. Scientific CSV/JSON values, source identities and archived artifact hashes are the exact audit targets.

## Consumed scientific execution

The C and D entrypoints document the actual frozen executable path; they are not reproduction commands to run again. The C attempt and D once-only entitlement are consumed. Do not delete their markers, resume a partial assessment, generate fresh final controls, replace the conditional generator, retune models, or perform a second D assessment. A missing prerequisite must produce an explicit failure, never a substitute fit or evaluation.

The manuscript remains a descriptive research draft requiring owner verification of authors, affiliations, contributions, conflicts, secondary-use obligations and submission wording. Internal agent review is not external peer review.
