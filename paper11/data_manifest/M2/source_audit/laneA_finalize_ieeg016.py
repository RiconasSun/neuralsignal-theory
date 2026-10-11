#!/usr/bin/env python3
"""IEEG016: finalize the units derivative tree (metadata, sidecars, README, provenance). Text-only, idempotent.
Usage: laneA_finalize_ieeg016.py <tree> <gin_repo_dir> <acquisition_receipt.json> <convert_report.json> <converter.py>"""
import csv, json, os, shutil, sys, glob

TREE, GIN, RECEIPT, REPORT, CONV = sys.argv[1:6]
T = 'task-verbalWM'


def wjson(p, o):
    with open(p, 'w') as f:
        json.dump(o, f, indent=2, ensure_ascii=False); f.write('\n')


# 1) sub-08 extra NIX session: label ses-05 (NIX Session_05; absent from ds004752)
old = f'{TREE}/sub-08/ses-nix05'
if os.path.isdir(old):
    new = f'{TREE}/sub-08/ses-05'
    os.rename(old, new)
    for p in glob.glob(f'{new}/ieeg/*'):
        os.rename(p, p.replace('ses-nix05', 'ses-05'))
sp = f'{TREE}/sub-08/sub-08_sessions.tsv'
txt = open(sp).read().replace('ses-nix05', 'ses-05'); open(sp, 'w').write(txt)

# 2) sessions without microwire units: drop header-only unit files, keep trial tables
removed = []
for p in glob.glob(f'{TREE}/sub-*/ses-*/ieeg/*_units.tsv') + glob.glob(f'{TREE}/sub-*/ses-*/ieeg/*_spikes.tsv') + glob.glob(f'{TREE}/sub-*/ses-*/ieeg/*_waveforms.tsv'):
    with open(p) as f:
        n = sum(1 for _ in f)
    if n <= 1:
        os.remove(p); removed.append(os.path.relpath(p, TREE))

rep = json.load(open(REPORT))
tot = rep['totals']
n_ses_units = sum(1 for f in rep['files'] if f['n_units'])

# 3) dataset_description.json
wjson(f'{TREE}/dataset_description.json', {
    "Name": "Human medial temporal lobe single units during a verbal working memory task (Boran et al.): spike times and waveforms aligned to OpenNeuro ds004752",
    "BIDSVersion": "1.10.0",
    "DatasetType": "derivative",
    "License": "CC-BY-SA-4.0",
    "Authors": ["Ece Boran", "Tommaso Fedele", "Adrian Steiner", "Peter Hilfiker", "Lennart Stieglitz",
                "Thomas Grunwald", "Johannes Sarnthein"],
    "Acknowledgements": "Data recorded and spike-sorted by the authors (Klinik für Neurochirurgie, UniversitätsSpital Zürich; Schweizerisches Epilepsie-Zentrum, Zürich) and released in NIX format on G-Node GIN (doi:10.12751/g-node.d76994). Re-packaged as a BIDS derivative keyed to OpenNeuro ds004752 subject/session labels by Bruno Aristimunha for NEMAR; no values were changed.",
    "HowToAcknowledge": "Please cite Boran E, Fedele T, Steiner A, Hilfiker P, Stieglitz L, Grunwald T, Sarnthein J (2020) Dataset of human medial temporal lobe neurons, scalp and intracranial EEG during a verbal working memory task. Scientific Data 7:30, doi:10.1038/s41597-020-0364-3; Boran E et al. (2019) Persistent hippocampal neural firing and hippocampal-cortical coupling predict verbal working memory load. Science Advances 5(3):eaav3687, doi:10.1126/sciadv.aav3687; and the original data release doi:10.12751/g-node.d76994.",
    "Funding": ["Swiss National Science Foundation, SNSF 320030_176222", "Mach-Gaensslen Stiftung",
                "Stiftung für wissenschaftliche Forschung an der Universität Zürich", "Forschungskredit der Universität Zürich"],
    "EthicsApprovals": ["All subjects provided written informed consent for the study, which was approved by the institutional ethics review board (Kantonale Ethikkommission Zürich, PB-2016-02055). (Boran et al. 2020, Scientific Data 7:30, Methods: Subjects)"],
    "ReferencesAndLinks": [
        "https://doi.org/10.1038/s41597-020-0364-3",
        "https://doi.org/10.1126/sciadv.aav3687",
        "https://doi.org/10.12751/g-node.d76994",
        "https://doi.org/10.18112/openneuro.ds004752.v1.0.1",
        "https://doi.org/10.82901/nemar.on004752",
        "https://github.com/jniediek/combinato"],
    "GeneratedBy": [{
        "Name": "laneA_convert_ieeg016.py + laneA_finalize_ieeg016.py",
        "Description": "Extraction of spike times, mean/std spike waveforms, unit-to-electrode mapping, trial properties and trial event tags from the 37 NIX (HDF5) files of the GIN release, written as TSV keyed to ds004752 participant/session labels. Values copied as stored; no re-sorting, filtering or rescaling. Scalp EEG and iEEG time series were not exported (published in ds004752). Code in code/.",
        "CodeURL": "code/"}, {
        "Name": "Combinato",
        "Description": "Spike detection and sorting performed by the original authors (Boran et al. 2020), followed by visual curation and merging of similar clusters on the same microwire.",
        "CodeURL": "https://github.com/jniediek/combinato"}],
    "SourceDatasets": [
        {"DOI": "doi:10.12751/g-node.d76994", "URL": "https://gin.g-node.org/doi/Human_MTL_units_scalp_EEG_and_iEEG_verbal_WM",
         "Version": "GIN DOI release (published 2019-12-04); repository master commit 0b27b34ecd0da217e4403bdd080b4a0d78f155fd"},
        {"DOI": "doi:10.18112/openneuro.ds004752.v1.0.1", "URL": "https://openneuro.org/datasets/ds004752/versions/1.0.1", "Version": "1.0.1"},
        {"DOI": "doi:10.82901/nemar.on004752", "URL": "https://nemar.org/dataexplorer/detail?dataset_id=on004752", "Version": "v1.0.0"}],
    "Keywords": ["single units", "spike times", "microwire", "human", "medial temporal lobe", "hippocampus",
                 "entorhinal cortex", "amygdala", "verbal working memory", "Sternberg task", "epilepsy", "iEEG"]
})

# 4) LICENSE (verbatim from GIN repo), CHANGES, .bidsignore
shutil.copyfile(f'{GIN}/LICENSE', f'{TREE}/LICENSE')
open(f'{TREE}/CHANGES', 'w').write('1.0.0 2026-10-06\n  - Initial BIDS-derivative packaging of the single-unit content of GIN doi:10.12751/g-node.d76994, keyed to OpenNeuro ds004752 v1.0.1 labels.\n')
open(f'{TREE}/.bidsignore', 'w').write('# Unit-level files have no BIDS suffix yet (microelectrode spike data are not in BIDS 1.10); documented in README.\n'
                                       '*_units.tsv\n*_units.json\n*_spikes.tsv\n*_spikes.json\n*_waveforms.tsv\n*_waveforms.json\n'
                                       '*_trials.tsv\n*_trials.json\n*_trialevents.tsv\n*_trialevents.json\n')

# 5) top-level sidecars (inherited by every session file)
wjson(f'{TREE}/{T}_units.json', {
    "unit_id": {"Description": "Unit number as used in the NIX source file names (Spike_Waveform_Unit_<unit_id>_...). Unit numbers are defined per session file; the same number in two sessions does not imply the same neuron."},
    "microwire": {"Description": "Behnke-Fried style microwire on which the unit was recorded, as named in the NIX source (u<electrode><index>, e.g. uAHL2 = microwire 2 of depth electrode AHL)."},
    "macro_contact": {"Description": "Deepest macro contact of the same depth electrode (m<electrode>1), the NIX source linked to the unit; label as in ds004752 electrodes.tsv."},
    "anatomical_location": {"Description": "Anatomical label of the macro contact from the NIX source (Brainnetome atlas, manually entered when the atlas gave no MTL label, see macro_label_manual_entry)."},
    "macro_contact_mni_x": {"Description": "MNI x coordinate of macro_contact from the NIX source (iEEG_Electrode_MNI_Coordinates)", "Units": "mm"},
    "macro_contact_mni_y": {"Description": "MNI y coordinate of macro_contact from the NIX source", "Units": "mm"},
    "macro_contact_mni_z": {"Description": "MNI z coordinate of macro_contact from the NIX source", "Units": "mm"},
    "macro_label_manual_entry": {"Description": "NIX iEEG_Electrode_Manual_Entry flag: True if the anatomical label was entered manually by the authors."},
    "n_spikes": {"Description": "Number of spike times of this unit across all trials of the session (count of rows in _spikes.tsv)."},
    "n_trials_with_spike_array": {"Description": "Number of trials for which the NIX file holds a spike-time array for this unit (arrays may be empty)."},
    "nix_waveform_array": {"Description": "Name of the NIX data array holding the waveform (provenance)."}})
wjson(f'{TREE}/{T}_spikes.json', {
    "Description": "Spike times of each sorted unit, one row per spike, copied from the NIX arrays Spike_Times_Unit_<unit>_<microwire>_Trial_<trial>. Only the 8-s trial windows are available in the source (no inter-trial spikes).",
    "unit_id": {"Description": "Unit number; see _units.tsv."},
    "trial": {"Description": "Trial number (1-based), equal to nTrial in the ds004752 events.tsv of the same subject/session and to 'trial' in _trials.tsv."},
    "spike_time": {"Description": "Spike time relative to probe (retrieval) onset of the trial; the trial window is [-6, 2] s: fixation [-6,-5], stimulus/encoding [-5,-3], maintenance [-3,0], probe from 0. To place a spike on the ds004752 recording timeline use onset(ds004752 events row with nTrial == trial) + spike_time + 6.", "Units": "s"}})
wjson(f'{TREE}/{T}_waveforms.json', {
    "Description": "Mean and standard deviation of the extracellular spike waveform of each unit, copied from NIX arrays Spike_Waveform_Unit_<unit>_<microwire>.",
    "unit_id": {"Description": "Unit number; see _units.tsv."},
    "statistic": {"Description": "Summary statistic across all spikes of the unit", "Levels": {"mean": "mean waveform", "std": "standard deviation"}},
    "s00": {"Description": "First of 64 waveform samples (columns s00..s63). Sample k is at time -0.00059375 s + k * 3.125e-05 s relative to the detected spike peak (32 kHz microwire sampling).", "Units": "uV"},
    "SamplingFrequency": 32000, "WaveformOffset": -0.00059375, "Units": "uV"})
wjson(f'{TREE}/{T}_trials.json', {
    "Description": "Per-trial task properties from the NIX metadata section Session/Trial properties.",
    "trial": {"Description": "Trial number (1-based); equals nTrial in ds004752 events.tsv."},
    "set_size": {"Description": "Number of letters to memorize (4, 6 or 8)."},
    "probe_letter": {"Description": "Probe letter shown at retrieval."},
    "match": {"Description": "Probe membership as coded in the NIX source", "Levels": {"1": "IN (probe was in the memory set)", "2": "OUT (probe was not in the memory set)"}},
    "correct": {"Description": "Response correctness as coded in the NIX source", "Levels": {"1": "correct", "0": "incorrect"}},
    "response": {"Description": "Button code of the response as stored in the NIX source (raw value, not interpreted)."},
    "response_time": {"Description": "Response time from probe onset", "Units": "s"},
    "artifact": {"Description": "NIX Artifact flag for the trial", "Levels": {"1": "trial marked as artifact by the authors", "0": "no artifact flag"}}})
wjson(f'{TREE}/{T}_trialevents.json', {
    "Description": "Trial event tags from the NIX group 'Trial events single tags spike times' (or, for sessions without units, 'Trial events single tags iEEG'). Times are in the same trial-relative clock as spike_time.",
    "trial": {"Description": "Trial number (1-based)."},
    "onset": {"Description": "Event onset relative to probe onset", "Units": "s"},
    "duration": {"Description": "Event extent as stored in the NIX tag; n/a where the source tag carries no valid extent", "Units": "s"},
    "nix_event": {"Description": "Event name from the NIX tag with the '_Trial_<n>_<clock>' suffix removed, e.g. Fixation_ss<set size>_c<correct>_m<match>, Stimulus_ss<set size>_<letters>, Maintenance, Probe_m<match>_<letter>, Response_c<correct>."}})
wjson(f'{TREE}/participants.json', {
    "Description": "Participants of the Boran et al. NIX release (nine subjects), labelled as in OpenNeuro ds004752; values from the NIX Subject metadata.",
    "participant_id": {"Description": "Subject label, identical to OpenNeuro ds004752 / NEMAR on004752."},
    "sciAdv_identifier": {"Description": "Subject number in the NIX release and in Boran et al. 2019 (Sci Adv) / 2020 (Sci Data); crosswalk taken from ds004752 participants.tsv."},
    "age": {"Description": "Age as stored in the NIX Subject metadata", "Units": "year"},
    "sex": {"Description": "Sex as stored in the NIX Subject metadata"},
    "handedness": {"Description": "Handedness as stored in the NIX Subject metadata (confirmed by neuropsychological testing, Boran et al. 2020)."},
    "pathology": {"Description": "Pathology as stored in the NIX Subject metadata"},
    "depth_electrodes": {"Description": "Depth electrodes implanted (NIX 'Depth electrodes'); A=amygdala, AH=anterior hippocampus, PH=posterior hippocampus, EC=entorhinal cortex, LR/DR=other, suffix L/R=hemisphere."},
    "soz_electrodes": {"Description": "Depth electrodes in the seizure onset zone (NIX 'Electrodes in seizure onset zone (SOZ)')."}})
wjson(f'{TREE}/sessions.json', {
    "Description": "One row per NIX session file of the subject, with its checksum, trial/unit/spike counts and the matching ds004752 session.",
    "session_id": {"Description": "Session label; ses-01..ses-07 equal the ds004752 labels. sub-08 ses-05 is NIX Session_05, which has no counterpart in ds004752."},
    "nix_source_file": {"Description": "Source NIX file in the GIN release (data_nix/)."},
    "nix_source_sha256": {"Description": "SHA-256 of the source NIX file as downloaded and verified against the GIN git-annex MD5 key."},
    "n_trials": {"Description": "Number of trials in the NIX session."},
    "n_units": {"Description": "Number of sorted units in the session (0 = no microwire units in the source file)."},
    "n_spikes": {"Description": "Total number of spike times in the session."},
    "ds004752_session": {"Description": "ds004752 session whose events.tsv matches this NIX session trial-by-trial (set size, probe letter, response time identical for every trial); n/a if none."}})

# 6) provenance of source files (checksums only; NIX bytes are NOT redistributed here)
rec = json.load(open(RECEIPT))
os.makedirs(f'{TREE}/code', exist_ok=True)
wjson(f'{TREE}/code/source_provenance.json', {
    "source": "G-Node GIN doi:10.12751/g-node.d76994 (USZ_NCH/Human_MTL_units_scalp_EEG_and_iEEG_verbal_WM, master 0b27b34ecd0da217e4403bdd080b4a0d78f155fd)",
    "note": "The NIX files also contain the scalp EEG and iEEG time series, which are published as OpenNeuro ds004752; to avoid duplicating that archive they are not included here. Obtain the NIX files from the DOI above.",
    "acquisition_receipt": rec,
    "crosswalk": rep['crosswalk']})
os.makedirs(f'{TREE}/code', exist_ok=True)
shutil.copyfile(CONV, f'{TREE}/code/laneA_convert_ieeg016.py')
shutil.copyfile(__file__, f'{TREE}/code/laneA_finalize_ieeg016.py')

# 7) README
nf = len(rep['files'])
readme = f"""# Human medial temporal lobe single units during verbal working memory: spike data aligned to OpenNeuro ds004752

## What this dataset is
This is a **BIDS derivative** dataset with the **single-unit content** of the dataset by Boran et al.
(G-Node GIN, doi:10.12751/g-node.d76994; Scientific Data 7:30, 2020, doi:10.1038/s41597-020-0364-3), re-keyed to the
subject and session labels of **OpenNeuro ds004752** (mirrored on NEMAR as **on004752**,
doi:10.82901/nemar.on004752). ds004752 publishes the scalp EEG and intracranial EEG (iEEG) of the same nine
patients, plus six more, but none of their microwire unit data. This dataset adds the missing unit data:

- {tot['units']} sorted units (single- and multi-unit activity; the source does not label which) recorded on
  microwires in the hippocampus, entorhinal cortex and amygdala, from {n_ses_units} of {nf} sessions of nine subjects;
- {tot['spikes']:,} spike times, given per trial;
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
"""
open(f'{TREE}/README.md', 'w').write(readme)
print('removed header-only files:', len(removed))
print('done')
