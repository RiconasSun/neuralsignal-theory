# R0 Scientific Limitation

The current v2 analysis cannot proceed under its registered usable-trial
criterion. Excluding old protected test partitions leaves32-40 development
trials/session for the recorded primary cohort. Only two patients have a
session at40. The minimum is8 independent patients. This is an upper bound:
hippocampal labels, training-rate and recording-QC filters cannot increase it.
No model fit, null test, effect size, uncertainty interval or regime ranking
has been produced. Do not call the metadata and engineering checks success of
the scientific research question.

Independent external metadata candidates are available:36 patients/52sessions
out of87files. Each selected session has>=5 explicitly hippocampal unit IDs and
100 recognition trials; split60train/40final. Site-qualified repeated sessions
are grouped under the same patient, not independent samples. Other MTL units
are not mixed into hippocampal candidates. Units are session-local, not tracked
identities. Different-task convergence is not direct replication.

No new physiological arrays were decoded. All range reads are bounded and
logged; adjacent undecoded bytes can be buffered. Published whole-file SHA256
values are pinned provenance, not falsely claimed local whole-file checksums.
Old test and the new external final partitions remain locked. There are no
per-unit observation intervals in the inspected NWB schema. The source paper
documents continuous acquisition and stable units; this is not independent
verification of individual recording gaps. Observation support must be
resolved without inferring absence from first/last spikes before R2 counts.

Potential next steps require a human scientific decision, not routine milestone
approval: retain40usable trials and stop, or separately approve a prospective
v2 eligibility amendment before any new neural/model result access. A32usable
trial minimum with>=24train/>=8validation would have9metadata candidate
patients before unit/QC filtering. This is not already authorized, not a power
guarantee, and not a scientific result. Alternatively a new truly unexposed
development dataset requires a separately registered source/split audit.

Primary and external task differences, small development patient count,
retrospective upstream full-session sorting, unknown private cross-cohort
identity and absent local dropout masks remain explicit limitations. Preserve
every original failure. Never repurpose a registered external final subject
subset for tuning or count old final trials as usable development data.

Sources: [primary external dataset descriptor](https://www.nature.com/articles/s41597-020-0415-9),
[pinned DANDI release](https://dandiarchive.org/dandiset/000004/0.220126.1852).
