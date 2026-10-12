# P12 M0 Metadata Feasibility Report

Working title: Regional Heterogeneity of Predictive Neural Dynamics Across
Hippocampal Subfields. Species: mouse. No human hippocampal validation claim.

## Verdict

Allen admission: **INCONCLUSIVE**. The single conditional IBL admission:
**INCONCLUSIVE**. **M0 does not PASS. M1-M7 are NOT EXECUTED.**
No predictive model, anatomical heterogeneity effect, null inference, or final
validation was run. Manuscript completion and scientific validation are false.
This is an auditable metadata feasibility result, not a successful experiment.

## Prospective Registration

M0 was registered at 2026-10-12T03:31:43.598449+00:00 before acquisition.
Local repository date was 2026-10-11 (America/Los_Angeles). Registration hashes
protocol and the prechange tree at 8f720d92b210dc33bf6f07ed02ce64b3cd82b611.
P1-P11 are hash-protected. No previously locked physiological data were decoded.
Primary contrast CA1 versus DG; CA3 secondary. Minimum admission remains
8 development plus 8 independent final mice, >=5 potential units per subfield
in the same session. No final mice or trial partitions were fabricated or
locked, because the admission gate did not pass.

The Allen warehouse is a mutable public API, not an immutable release archive.
Verbatim identity/anatomy snapshots and each query URL/UTC/SHA256 are retained.
58 linked NWB file IDs, sizes, ETags and Last-Modified headers are retained;
these are not full-file cryptographic checksum verification or a formal provider
release accession. Live SDK master/latest documentation were snapshotted by
hash; no SDK default unit or session loader was used.

## Full Allen Denominator

| Metadata object | Count |
|---|---:|
| Specimens/mice (one session per mouse, official description) | 58 |
| Sessions | 58 |
| Probes | 332 |
| Channels | 123,224 |
| Unfiltered unit identities | 135,275 |
| CA1 atlas-labelled unit identities | 26,620 |
| CA3 atlas-labelled unit identities | 4,972 |
| DG atlas-labelled unit identities | 9,678 |
| Potential same-session CA1-DG coverage | 51 mice / 51 sessions |
| >=5 CA3 candidate units | 50 sessions |
| Fully admitted mice | 0 |

All sessions, including seven below the provisional anatomical paired threshold,
remain in `results/allen_sessions.csv`. All mice and probes are enumerated in
the corresponding CSV files. Full channel and unit identity tables are retained
as projected source receipts. Unit-channel-probe-session joins have no orphans.
No noise, presence, waveform, firing-rate or response-based filtering was applied.
These counts are upper-bound anatomical potentials, not viable simultaneously
active units. SDK tutorial counts use different upstream/default filtering and
must not replace the full unfiltered warehouse denominator.

Stimulus protocols: brain_observatory_1.1, 32 sessions (25 anatomical potentials);
functional_connectivity, 26 sessions (26 potentials). No mixed-protocol model
comparison or stimulus choice was made. Presentation rows, including movie
frames, are not automatically independent trials or repeats.

## Native Metadata and Support Boundaries

Every one of the 58 NWB objects honored an exact eight-byte Range request and
had an HDF5 signature. Selective HDF5 metadata reads obtained session start and
timestamp reference origins for all58, plus start/stop stimulus interval summaries.
The saved table `results/allen_stimulus_intervals.csv` reports every available
table's counts, finite timestamps and envelope. These are metadata observations,
not neural measurements. Exact repeat identities and stimulus-condition balancing
are NOT established merely by interval table names.

`invalid_times` metadata occurs in 17 sessions. Its absence in the remaining41
does not establish no missing neural data. Interval tags were not decoded into
per-probe missingness attribution. Acquisition group names in all58 contain no
native electrical recording object; running-wheel acquisition is not a witness
of uninterrupted neural observation. Native start/end support and undocumented
gaps remain UNKNOWN for every session, not proven absent.

The official Allen tutorial states that released data are pre-aligned to a common
clock. This is a provider processing declaration, not independent per-probe
clock/gap validation. All58 raw S3 session directories were inventoried: 1,379
objects, 58 sync.h5 files, bare spike/LFP bands and digital event arrays.
No .meta/.oebin/params.json/settings.xml recording-parameter sidecar was found in
that complete prefix inventory. Raw signal arrays and digital sync values were
not opened. Their availability is explicitly disclosed: this audit does NOT
claim the missing support could never be reconstructed from raw synchronization
data. A separate prospective clock-reconstruction procedure would require
definitions, a validated decoder and new evidence; it is not a passed M0 gate.

Header metadata transport used 74,046,592 bytes across58 files (each under2MiB),
plus464 signature bytes and the preserved failed initial attempts. Structural
range reads can contain opaque adjacent physiological bytes. We make no claim
of zero physiological transport: only registered timestamp/header values were
intentionally decoded. Separate same-ETag link/type audits validate every path
used in the saved metadata summaries; no values are decoded in this link audit.
No spike, waveform, rate, quality-metric or model-score arrays were requested.

Unit localization is a peak-channel-to-CCF atlas annotation. CA1/CA3/DG remain
explicitly labelled; HPF, CA2, SUB and other MTL labels are never folded into them.
Per-probe histology or independent subfield localization has not been inspected.
The official processing description includes Kilosort2, artifact removal and
retrospective quality metrics; no new unit-quality conclusion is inferred here.
Running, eye/pupil and optotagging are documented modalities; eye tracking failure
flags are inventoried, not behavior values. Per-session behavioral missingness
and causal availability remain unverified.

## Single IBL Alternative

Conditional audit registered before IBL data acquisition, after the saved Allen
INCONCLUSIVE gate. The 2025 official release description is compared to the
fixed `2023_12_bwm_release.csv` identity fixture and the documented
`2024_Q2_IBL_et_al_BWM/clusters.pqt` anatomy aggregate. Source repository commit:
118fc36cb3602934466ad2c6087c2b3b441f9f1f. No later release was substituted.

Full denominator: 139 lab/subject identities, 459 sessions, 699 insertions,
621,733 unfiltered cluster identities. Corrected offline joins verify all
fixture(eid,pid) links, 621,733 distinct (pid,cluster_id) identities, no orphan
units, and no fixture probe missing anatomy rows. Atlas potentials are
84 mice /108 sessions with >=5 CA1 and >=5 DG identities. Fully admitted mice:0.
These are not good-quality-unit counts, a final-evaluation cohort or a confirmation
of simultaneous active coverage. All459 sessions are retained in the result CSV.

Only uuids, cluster_id, atlas_id, pid and eid columns were requested. The
91,555,529-byte Parquet object was not bulk downloaded: column/footer ranges
transported22,928,385 bytes. Object ETag matches the MD5 declaration in the pinned
official loader (b89fac76289f3a3d585910711f1eef41); a full object MD5 was NOT
independently recomputed. Column-only compressed decoded metadata are saved for
offline joins. Other neural columns were not requested or scored.

Identity joins and aggregate counts agree with the public release description;
this does not verify trial clocks, raw recording support, saturation/gaps,
individual anatomy localization or every release revision. No external spikes,
behavioral choices, neural scores or final validation were inspected.
IBL is a visual decision-making task, not Allen passive visual stimulation.
Any future separately admitted comparison would be convergent, not direct
same-task replication. No replacement arm or final split was established.

## Load-Bearing Sources

- [Allen official project description](https://allensdk.readthedocs.io/en/latest/visual_coding_neuropixels.html)
- [Allen official access and clock documentation](https://allensdk.readthedocs.io/en/latest/_static/examples/nb/ecephys_data_access.html)
- [Allen metadata API](https://api.brain-map.org/api/v2/data/query.json)
- [IBL official 2025 release description](https://docs.internationalbrainlab.org/notebooks_external/2025_data_release_brainwidemap.html)
- [Pinned IBL source](https://github.com/int-brain-lab/paper-brain-wide-map/tree/118fc36cb3602934466ad2c6087c2b3b441f9f1f)

Verbatim source receipts, bounded-range hashes and initial failures are preserved.
Neither atlas potentials nor successful software tests establish a preferred
predictive representation, a physical subfield regime, NAP or CWP validation.
