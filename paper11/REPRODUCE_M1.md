# P11 M1 Reproduction

Prerequisite: M0 gate PASS and every M0 frozen file/environment unchanged.
M1 uses the same standard-library Python environment. Papers 1-10 and the M0
protocol, metadata, tests and results are never edited by this command.

First real progressive acquisition (Internet required, resumable verified cache):

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File paper11/scripts/reproduce-m1.ps1 -Acquire
```

Replay from verified local data, with no network access:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File paper11/scripts/reproduce-m1.ps1
```

Only fixed nm000363 v1.0.0 and ds004752 v1.0.1 commit content is downloaded.
Each file must equal its pinned Git blob; local SHA256 and acquisition receipts
are recorded. The pilot metadata session precedes complete metadata acquisition;
the actual trial manifest is frozen before sequential session spike downloads
and training-only QC. No waveform, original NIX, iEEG signal or external NWB
downloads are needed for this M1 anatomy/alignment gate.

Raw tables remain under ignored paper11/raw/M1, not on GitHub. A clean clone
requires -Acquire first. Do not replace missing experimental bytes with fixtures.
Corrupt caches and changed split manifests fail closed; never overwrite locks.

Metadata defines valid trials: no artifact; legal task labels; finite response
time; confirmed preprobe phase timing/coverage. Incorrect trials remain eligible.
Companion alignment checks all trial identities, set sizes, probe letters,
IN/OUT match, correctness, artifact flags and response times. Macro-electrode
name, coordinates, region and hemisphere are crosschecked when paired. Unpaired
sessions remain explicitly labeled; they can support spikes but not paired iEEG.

Explicit hippocampal labels only; other MTL and unresolved labels stay outside
the primary. Unit identity is scoped to subject/session. Training epoch counts
are QC counts, not 100-ms features or fitted firing-rate results. >=20 training
preprobe spikes and full source array coverage are required by the frozen QC
contract. Validation/test timestamp and unit fields are never decoded for QC;
only row trial IDs are inspected to skip heldout content. Downloading/hash-checking
raw bytes is distinguished from analytical inspection of heldout spikes.

Source aggregate spike counts are not used to select units. Published sorting
was session-wide; SU versus MU is not supplied. These limitations are retained.
Confirmatory coverage threshold is >=6 subjects each with >=1 session having
>=40 valid trials and >=5 eligible hippocampal sorted units. Fewer subjects yields
DATA_INSUFFICIENT and prevents M2; no model comparison is forced.

Outputs: per-unit/session/subject QC, trial alignment report, immutable split
JSON/lock, per-file receipts, automated tests, gate_result.json, claim audit,
execution.log and updated MILESTONE_STATUS.md. All scientific regime preferences
remain NOT_TESTED. Stop at M1; no M2-M7 execution is performed.

Derived QC/coverage tables and trial splits derive from nm000363 and are shared
under CC-BY-SA-4.0; source license is reproduced in
results/M1/DERIVED_DATA_LICENSE.txt. Cite the original nm000363 dataset and the
Boran source studies listed in the unchanged M0 README snapshot. Source metadata
retains original licenses. This statement does not invent a blanket code license.
