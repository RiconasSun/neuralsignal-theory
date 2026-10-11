# Reproduce P11 M0 Only

From the repository root, using the frozen Python environment:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File paper11/scripts/reproduce-m0.ps1
```

The command verifies frozen protocol/source/environment SHA256, checks P1-P10
preservation, runs unittest, writes real QC/test/gate/claim reports, and stops.
It neither downloads raw spikes/iEEG/NWB files nor executes M1-M7.

Environment is recorded in environment/environment.json, not inherited from P1's
different Python requirements. M0 requires Python 3.11+ and standard library
only. Later modeling packages and numerical backends require their own frozen
milestone environment; M0 does not certify them.

Initial freeze creation, once only (network is needed for metadata):

```powershell
python paper11/scripts/run_m0.py --acquire-metadata
python paper11/scripts/run_m0.py --freeze --verify
```

Existing freeze is never overwritten; do not rerun acquisition after freezing.
Offline reproduction uses committed metadata receipts and snapshots. A changed
environment or protocol fails closed. A protocol amendment requires a new
version and preserved old lock, with explicit disclosure before holdout access.
The environment lock includes installed package versions; reproduce those on a
matching machine or document a separately audited environment rather than
editing the original lock to suppress a failure.

Metadata participant counts are not eligible hippocampal subjects. Trial split
fixtures test code only; no real trial assignments are fabricated in M0. M1
must freeze actual eligible trial manifests before any signal preprocessing.
The locked split algorithm is chronological whole-trial 60/20/20 per session.

The primary metric is causal one-step predictive count log-likelihood, equal
weight per subject. P10 global continuity does not exclude local hippocampal
discrete or hybrid regimes. No NAP or CWP claim is permitted.

nm000363 is CC-BY-SA-4.0; cite its original dataset and comply with share-alike
terms for derivative data. Metadata snapshots preserve original notices. ds004752
is a separate companion modality; DANDI is an independent convergent candidate
whose anatomy/task eligibility remains unaudited until later milestones.
