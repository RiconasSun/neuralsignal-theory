[![DOI](https://img.shields.io/badge/DOI-10.82901%2Fnemar.nm000363-blue)](https://doi.org/10.82901/nemar.nm000363)

# Human medial temporal lobe single units during verbal working memory: spike data aligned to OpenNeuro ds004752

## Companion to NEMAR on004752 (OpenNeuro ds004752): the single-unit data of the same 9 patients
This dataset holds the **single-unit (microwire) data** for the **same 9 patients** whose scalp EEG and
intracranial EEG are published as **NEMAR on004752**, a mirror of **OpenNeuro ds004752**. It does not
repeat that EEG/iEEG.

- NEMAR on004752: https://data.nemar.org/on004752/ (DOI https://doi.org/10.82901/nemar.on004752)
- OpenNeuro ds004752, version 1.0.1: https://doi.org/10.18112/openneuro.ds004752.v1.0.1

**Subject labels are identical.** `sub-01` to `sub-09` here are `sub-01` to `sub-09` of on004752 and
ds004752, the same patients under the same labels. ds004752's `sciAdv_identifier` column (1–9) links them to
"Subject 1"–"Subject 9" of the original NIX release and of Boran et al. 2019/2020. Patients `sub-10` to
`sub-15` of ds004752 had no unit recordings in this release.

**Session labels are identical.** `ses-01` to `ses-07` match the ds004752 sessions of the same subject trial
by trial: the set size, probe letter and response time agree for every trial. The one exception is
`sub-08/ses-05`: that NIX session exists only in the original release and has no ds004752 counterpart.

**Trial numbers are identical.** `trial` here equals `nTrial` in the ds004752 `events.tsv`. A spike at
`spike_time` falls at `onset(nTrial) + spike_time + 6 s` on the ds004752 recording.

## What this dataset is
This is a **BIDS derivative** dataset with the **single-unit content** of the dataset by Boran et al.
(G-Node GIN, doi:10.12751/g-node.d76994; Scientific Data 7:30, 2020, doi:10.1038/s41597-020-0364-3), re-keyed to the
subject and session labels of **OpenNeuro ds004752** (mirrored on NEMAR as **on004752**,
doi:10.82901/nemar.on004752). ds004752 publishes the scalp EEG and intracranial EEG (iEEG) of the same nine
patients, plus six more, but none of their microwire unit data. This dataset adds the missing unit data:

- 1526 sorted units (single- and multi-unit activity; the source does not label which) recorded on
  microwires in the hippocampus, entorhinal cortex and amygdala, from 30 of 37 sessions of nine subjects;
- 1,526,770 spike times, given per trial;
- the mean and standard deviation of each unit's waveform;
- the mapping of each unit to its microwire, depth electrode, macro contact, MNI coordinates and anatomical label;
- per-trial task properties and trial event tags;
- participant metadata from the NIX files that ds004752 lacks: handedness, implanted depth electrodes and
  seizure-onset-zone electrodes.

The scalp EEG and iEEG time series inside the NIX files are **not** included, because they are already archived
as ds004752. Combine the two datasets by matching `participant_id`, `session_id` and the trial number.

## Subjects and sessions
Nine patients with drug-resistant focal epilepsy were implanted with depth electrodes in the medial temporal lobe
for clinical evaluation (Schweizerisches Epilepsie-Zentrum, Zürich). Subjects `sub-01` to `sub-09` are the
ds004752 labels. The `sciAdv_identifier` column of `participants.tsv` gives the subject number used in the NIX
release and the papers; ds004752's own participants.tsv provides that crosswalk.

**How sessions were matched.** Each NIX session was compared with every ds004752 session of the same subject,
trial by trial (set size, probe letter and response time).
- 36 of the 37 NIX sessions match exactly one ds004752 session with the same number, identical on all trials
  (see `sub-*/sub-*_sessions.tsv` and `code/source_provenance.json`).
- NIX `Data_Subject_08_Session_05` (49 trials, 87 units) matches no ds004752 session. It is included as
  `sub-08/ses-05`, and its EEG/iEEG is not present in ds004752.
- Seven sessions have no microwire units in the source: sub-01 ses-03 and ses-04, sub-06 ses-04 to ses-07, and
  sub-07 ses-01. For these sessions only the trial tables are provided.

## Task
This is a modified Sternberg task. Each 8-s trial has four phases, timed relative to probe onset:
- fixation, −6 to −5 s;
- encoding, −5 to −3 s: eight consonants are shown, and the middle 4, 6 or 8 are the memory items (the set size);
- maintenance, −3 to 0 s;
- probe, from 0 s: a probe letter appears, and the subject answers by button press whether it was in the set
  (IN/OUT).

Each session had about 50 trials. The task was run in Presentation® (Neurobehavioral Systems,
www.neurobs.com/ex_files/expt_view?id=266). The task is `verbalWM`, as in ds004752.

Further task details from Boran et al. 2020 (Sci Data 7:30, Methods):
- "The subjects were instructed to respond as rapidly as possible without making errors."
- After the response the probe was turned off and the subjects received acoustic feedback on whether the response was
  correct; "a trial with an incorrect response was always followed by a trial with a set size of four".
- "The subjects performed 50 trials in one session, which lasted approximately 10 min"; several subjects performed
  more than one session, up to seven, during the recording period of several days.
- Presentation® version 18.0, run on a notebook computer in front of the subject; event TTL pulses were sent to the
  ATLAS acquisition system via a parallel port.

## Recording and spike sorting
These details are taken from Boran et al. 2020.
- **Electrodes:** AdTech depth electrodes (1.3 mm diameter, 8 contacts of 1.6 mm, 5 mm spacing). Each electrode
  has nine microwires protruding about 4 mm from its tip.
- **Acquisition:** Neuralynx ATLAS, recorded against a common intracranial reference. Microwires were sampled at
  32 kHz and macro contacts at 4 kHz (resampled to 2 kHz in the release), with a 0.5–5000 Hz passband.
- **Spike sorting:** Combinato (https://github.com/jniediek/combinato). Steps:
  - peak detection in the >500 Hz high-passed signal;
  - wavelet features;
  - superparamagnetic clustering.
- **Curation:** clusters were inspected visually. Clusters with firing rate below 0.1 Hz, noisy waveforms or
  non-uniform shape were removed, and highly similar clusters on the same microwire were merged.
- **Anatomy:** electrode positions come from post-implantation CT and MRI, normalized to MNI space and labelled
  with the Brainnetome atlas, with manual labels where needed (`macro_label_manual_entry`).
- **Implantation:** "Implantation sites were selected solely based on the clinical indication." All subjects "had
  normal or corrected-to-normal vision and were right-handed as confirmed by neuropsychological testing".
- **Scalp EEG (in ds004752, not here):** 10-20 system with minor adaptations, NicoletOne system at 256 Hz
  (0.3-100 Hz passband, Natus).
- **Sorting quality reported by the authors:** sorting yielded single-unit (SUA) and multi-unit activity (MUA);
  percentage of inter-spike intervals below 3 ms 1.58 ± 4.18%; waveform peak signal-to-noise ratio 3.28 ± 1.56.
- **Spike-sorting method reference:** Niediek J, Bostrom J, Elger CE, Mormann F (2016) Reliable Analysis of
  Single-Unit Recordings from the Human Brain under Noisy Conditions: Tracking Neurons over Hours. PLoS One
  11:e0166598, doi:10.1371/journal.pone.0166598.

## Files
Each `sub-XX/ses-YY/ieeg/` folder holds the following files, all named `sub-XX_ses-YY_task-verbalWM_<kind>.tsv`.
Their column definitions are in the top-level `task-verbalWM_<kind>.json` sidecars.

| file | content |
|---|---|
| `_units.tsv` | one row per unit: microwire, macro contact, anatomical label, MNI coordinates, spike count |
| `_spikes.tsv` | one row per spike: `unit_id`, `trial`, `spike_time` (s, relative to probe onset) |
| `_waveforms.tsv` | per unit, a mean row and a std row, each with 64 samples (µV) at 32 kHz starting −0.59375 ms before the peak |
| `_trials.tsv` | set size, probe letter, match, correctness, response code, response time, artifact flag |
| `_trialevents.tsv` | NIX trial event tags (fixation, stimulus, maintenance, probe, response), trial-relative times |

**Aligning to ds004752.** To place spikes on the ds004752 iEEG/EEG timeline (EDF), take the onset of the
ds004752 `events.tsv` row whose `nTrial` equals `trial` and add `spike_time` + 6 s.

## How to load
```python
import pandas as pd
d = "sub-01/ses-01/ieeg/sub-01_ses-01_task-verbalWM_"
units = pd.read_csv(d + "units.tsv", sep="\t")
spikes = pd.read_csv(d + "spikes.tsv", sep="\t")      # unit_id, trial, spike_time (s from probe onset)
trials = pd.read_csv(d + "trials.tsv", sep="\t")
# spikes of unit 1 in correct set-size-8 trials
ok = trials.query("correct == 1 and set_size == 8").trial
st = spikes[(spikes.unit_id == 1) & spikes.trial.isin(ok)]
```
The matching iEEG/EEG time series are in on004752/ds004752 (same `sub-`/`ses-` labels; `trial` == `nTrial`).

## Known caveats
- Units are not labelled as single- or multi-unit in the source; the paper reports both SUA and MUA.
- Spike times exist only inside the 8-s trial windows ([-6, 2] s around probe onset); inter-trial spikes are not in
  the source.
- Unit numbers are defined per session file; the same `unit_id` in two sessions does not imply the same neuron.
- Seven sessions have no units (listed under Subjects and sessions); `sub-08/ses-05` has no EEG/iEEG in ds004752.
- `response` holds raw button codes (values 1, 2, 51, 52 occur); the source does not document their mapping.
  Use `match` and `correct` for the response outcome.

**Validator.** Microelectrode spike data have no BIDS suffix yet, so these files are listed in `.bidsignore`. The
BIDS validator therefore checks the dataset-level files, `participants.tsv` and `sessions.tsv`.

## Source and changes
- **Source:** the 37 NIX files of the GIN release (17.3 GB). They were downloaded over the repository's public
  HTTP endpoint and verified against its git-annex MD5 keys.
- **Re-checking:** SHA-256 checksums are listed in each `sessions.tsv`. The code that produced this dataset is in
  `code/`.
- **Values:** all values are copied as stored, with no re-sorting, filtering or rescaling.
- **Session label:** the only relabeling is the session label of sub-08's fifth NIX session, which ds004752
  lacks.
- **Not copied:** the NIX files themselves, and the `usz_identifier` column of ds004752 (a hospital database
  number).

## License and citation
The source data are licensed CC BY-SA 4.0 (`LICENSE`, copied verbatim from the GIN repository). This derivative
is distributed under the same license, as share-alike requires.

Please cite:
- Boran et al. 2020, Scientific Data 7:30, doi:10.1038/s41597-020-0364-3;
- Boran et al. 2019, Science Advances 5:eaav3687, doi:10.1126/sciadv.aav3687;
- the GIN dataset, doi:10.12751/g-node.d76994.

For the EEG/iEEG, also cite ds004752: Dimakopoulos et al. 2022, eLife 11:e78677,
doi:10.18112/openneuro.ds004752.v1.0.1.

## Ethics
All subjects gave written informed consent. The study was approved by the Kantonale Ethikkommission Zürich
(PB-2016-02055) (Boran et al. 2020).

## Funding
Boran et al. 2020, Acknowledgements: "We acknowledge grants awarded by the Swiss National Science Foundation (SNSF
320030_176222 to J.S.), Mach-Gaensslen Stiftung (to J.S.), Stiftung für wissenschaftliche Forschung an der
Universität Zürich (to J.S.) and by Forschungskredit der Universität Zürich (to T.F.)." The same funders are listed in
the GIN DataCite record of doi:10.12751/g-node.d76994.
