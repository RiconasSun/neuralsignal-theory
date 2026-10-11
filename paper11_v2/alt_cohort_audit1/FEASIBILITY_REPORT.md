# P11-ALT-COHORT-AUDIT-1

Scientific feasibility gate: **INCONCLUSIVE**. No new validation arm admitted.
Original P11-v1 numerical failures, P11-v2 R2 FAIL/DATA_INSUFFICIENT, DANDI
boundary INCONCLUSIVE, and every previous split/holdout lock remain unchanged.

## Observed Evidence

Protocol registration preceded all candidate metadata acquisition. Initial
HEAD182ddb86e2e6898d9db920720b948b42aae40c44; clean test branch, freshly fetched
origin/test identical. Registration records UTC/source hashes and all prior
tracked hashes. Scientific protocol and access scope never relaxed.

OSF project VH5KQ is public and mutable, not a frozen project registration.
Provider project metadata says modified2025-01-29. Complete uniform recursive
inventory:2,585files,14folders,46event-session filename stems,15patient filename
labels. All2,585files expose current versions and SHA256. The saved inventory
pins per-file versions/hashes, NOT an immutable project release. Provider data
hashes were inventoried, not independently checked against forbidden data bytes.
Three standalone README RTF files were downloaded under an exact access plan;
all three local SHA256 values match their provider SHA256. Provider project
license is CC0 1.0 Universal; published article license is separate. Do not
assume the project license clears third-party ImageNet/COCO stimulus rights.

The first default10-item pagination attempt stopped at its250request budget
(exit1). This incomplete attempt and all receipts are preserved. A prospective
acquisition-only registration used100items/page with an additional250request
ceiling. It completed the same all-folder inventory in43requests,5,993,973bytes,
including the descriptor and two official tables. No patient/session was
omitted to meet a gate. Metadata pagination changed, not scientific criteria.

## Patient And Session QC

The descriptor describes16patients across WVU/WUSTL/Utah. Its Table1 and the
complete event filename inventory each expose15patient labels and46session
rows/stems. The16-versus15 discrepancy requires author reconciliation; missing
identity is not inferred or quietly dropped. Source institutions differ from
the primary Zurich cohort, supporting site/source independence only. Private
cross-border nonoverlap cannot be established from unrelated pseudonyms.
[Descriptor](https://www.nature.com/articles/s41597-024-04265-1),
[Patient table](https://www.nature.com/articles/s41597-024-04265-1/tables/1).

| Filename Patient | Sessions | Published Hippo Counts By Table Row | Full Eligibility |
| --- | ---: | --- | --- |
| p14WV / WVU14 | 2 | 9,8 | UNKNOWN |
| p16WV / WVU16 | 3 | 37,47,41 | UNKNOWN |
| p18WV / WVU18 | 4 | 1,8,6,8 | UNKNOWN |
| p19WV / WVU19 | 2 | 18,25 | UNKNOWN |
| p20WV / WVU20 | 5 | 52,25,27,25,32 | UNKNOWN |
| p21WV / WVU21 | 3 | 0,0,0 | UNKNOWN |
| UIC202214 | 1 | 7 | UNKNOWN |
| BJH024 | 2 | 8,17 | UNKNOWN |
| BJH025 | 2 | 0,0 | UNKNOWN |
| BJH026 | 4 | 13,11,14,9 | UNKNOWN |
| BJH027 | 4 | 18,14,21,18 | UNKNOWN |
| BJH028 | 2 | 0,0 | UNKNOWN |
| BJH029 | 4 | 8,5,8,6 | UNKNOWN |
| BJH032 | 4 | 6,4,8,4 | UNKNOWN |
| BJH033 | 4 | 1,0,0,0 | UNKNOWN |

WVU filename/table pairing is a spelling-based correspondence, not independently
verified alias/session-row linkage. Table counts are published summary metadata,
not neural values read by this audit. Eleven published patients have some row
with>=5hippocampal units. This is promising potential, not eleven admitted
patients:table rows lack exact linkage to event files and session-local unit
dictionaries. All15patients and46sessions remain in QC, including low-count
and unknown cases. No selected-neuron identity persists across sessions.

Existing external thresholds remain8independent patients,5hippocampal units
and40valid trials/session. The32trial amendment applies to primary development,
not this external candidate. README describes550/555nominal trials and manual
removals after interruptions. Actual valid exposure/trial counts are UNKNOWN.
Training>=20spikes/unit is deliberately unexamined, never inferred from counts.
QC's0documented fully eligible patients means0CERTIFIED, not0actually eligible.

## Recording Boundaries And Clocks

The public descriptor reports continuous32kHz Neuralynx/Blackrock recording,
and microsecond event/spike exports. The event README defines pre/post stimulus
windows, not acquisition support. The unit README documents matched session,
channel, cluster and area arrays inside mixed spike MAT files. These arrays
and all event-value files were not opened. Published whole-task rate filtering
must be disclosed in any future arm; it cannot replace train-only unit QC.

No identifiable standalone NCS/NEV/NSx raw recording file, native header/gap
manifest or independent common-clock mapping appears in the complete public
inventory. Two archives remain unopened. This does NOT prove raw data never
exist or are not inside an archive; it means authoritative header/continuity
evidence could not be obtained under this registered metadata-only access.
No start/end timestamp, gap duration, hardware offset or drift estimate was
invented. Common units, epoch size, stimulus endpoints and zero spike counts
cannot substitute for independently measured recording support/synchronization.

## Next Candidate: Figshare14905317

Following the primary INCONCLUSIVE gate, public article/version metadata and
the descriptor were assessed. Version1 DOI10.6084/m9.figshare.14905317.v1,
published2023-07-06, CC BY4.0. One public file:ESN_code_data_19052023.zip,
12,256,930,819bytes; computed/supplied MD5 both
508b77e3a31f87d9a4547a3f7b27f157. The archive was NOT downloaded or opened;
the checksum is provider metadata, not locally verified neural-data integrity.
[Versioned record](https://doi.org/10.6084/m9.figshare.14905317.v1).

The published study describes30participants across Birmingham/Erlangen and
human hippocampal recordings. Its associative task differs from P11's primary
working-memory task; possible convergence, never direct replication. Public
archive-level metadata cannot establish unique patient mappings,>=8admissible
simultaneous populations, valid trial/support masks, raw gaps or clock linkage.
Next-candidate feasibility is also INCONCLUSIVE, not a failed biological theory.
[Study](https://www.nature.com/articles/s41562-023-01706-6).

## Required Evidence Before Any New Arm

Obtain an author/repository standalone metadata bundle:all canonical patient
aliases and task/session mapping, unit/channel hemisphere and hippocampus-only
labels, valid trial-count/coverage summaries without responses, native acquisition
header timestamps, block validity/gap masks, and documented event-neural clock
transforms with synchronization uncertainty. Reconcile VH5KQ16/15denominator.
For Figshare, first obtain archive directory/schema metadata without extracting
spikes, outcomes or waveshapes. Author contact or broader archive access requires
separate authorization and a prospective access plan. No current binary download
or full-cohort fitting is authorized by this result.

All independently executable authorized metadata/source/QC/test work is complete.
Do not lower thresholds, rename missing evidence as PASS, reassign DANDI60/40,
revive R2 or run R3. Stop here pending genuinely new metadata and authorization.
