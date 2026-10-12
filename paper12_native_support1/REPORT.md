# Native Recording Support Recovery Audit

Mission:P12-M0-NATIVE-SUPPORT-AUDIT-1. Independent prospective metadata audit.
Checkpoint91c92abcda3549196cce1d6253ef0fa76c8d0886. Mouse study, not human validation.

## Decision

**CURATED_RELEASE_SUPPORT_ONLY_PROPOSE_SEPARATE_EXPLORATORY_PROTOCOL.**
Original M0 remains INCONCLUSIVE, not PASS. Native uninterrupted observation and
true per-bin exposure are not certified. No M1-M7, neural features, model fitting,
scores, behavior outcomes or final validation were executed or decoded.

A common-protocol exploratory study of curated-release counts and provider
annotated subfields is computationally feasible in principle:26 functional-
connectivity mouse identities have anatomical paired potentials and581-600
clock-bracketed, known-exclusion-screened repeated grating presentations each.
This establishes potential for8 development plus8 separate final mice, not
physiological eligibility, a locked cohort, adequate power or biological success.

## Full Denominator And New Evidence

All58sessions/mice,332probes,123224channels and135275unfiltered unit identities
were retained. No difficult session/probe was deleted. Every session underwent
digital timing, frozen-object NWB metadata, anatomy-coordinate and trial audits.
All58value-path schema checks pass using unchanged ETags without decoding values.
Three source/decoder protection issues and initial smoke failures are preserved
in EXECUTION_LOG.md and original output directories, with separate corrections.

| Evidence | Result | Interpretation |
|---|---:|---|
| Whole-probe all-segment clock diagnostic |313/332pass | Not continuity certification |
| Underidentified probe/gap segment records |19probes | All retained, not favorable pruning |
| Known invalid intervals decoded |88 | Probe/global tags, not complete packet audit |
| Physical visual-frame timing, both registered tables |56/58pass | Two maximum-error failures retained |
| Functional-connectivity protocol |26mice/sessions | Metadata-selected before neural scores |
| Repeated grating presentations |600/session |8conditions,75repetitions per condition |
| Clock-bracketed paired grating presentations |581-600/session |26potential mice; not spike adequacy |
| Complete movie repetitions where definition passes |60/session in25FCsessions |54000frames are not54000trials |
| Original fully admitted mice |0 | Original support standard not demonstrated |

Full session/probe matrices, known exclusions, genuine trial conditions and all
functional-connectivity trial windows are machine-readable under results/.
Presentation repetitions are disjoint candidate scoring units, not independent
animals or guaranteed statistically independent trials. The mouse remains the
independent biological unit. No inferential statistics or effects were estimated.

## Clock Findings

Source definitions were pinned and the barcode policy registered before digital
decoding. Source-defined signed TTL channel IDs were corrected prospectively
before full-cohort decoding:only+/-1barcode and0split are interpreted; auxiliary
line identifiers are not assigned behavioral meanings. The official parser's
first-code omission is disclosed; time/code length mismatches now fail closed.
Every uniquely identified shared code is included in its source-defined segment.
Independent all-code affine regression checks1ms p95/5ms maximum residual;
no seeds, replicas or favorable codes were selected. Underidentified segments
with<3codes fail rather than receive an invented transform. No extrapolated
trial receives a clock-bracketed support flag.

The master digital clock is100kHz; probes have nominal30kHz sampling with
independently estimated scales. A100ms bin corresponds nominally to3000samples,
but physical bin boundaries must be in continuous master seconds, not assumed
integer corrected-clock sample counts. Good clock residuals are smaller than
the bin, but alone cannot certify raw data continuity or true observation exposure.

A separately registered non-neural visual TTL/thresholded photodiode check used
the pinned SDK reconstruction policy without parameter search. Reconstructed
frame times were compared with every saved presentation onset in the selected
repeat tables; known global invalid windows were counted separately. All26FC
grating tables satisfy the frozen1ms p95/5ms max diagnostic. Session793224716's
grating max difference is0.000237314948s; its movie table contains2unmasked
starts exceeding5ms, max0.016445560879s. Session737581020 (other protocol) has
one unmasked start with0.016667952952s difference. Both all-table failures remain
FAIL. Their residuals were not administratively cleared or tolerance-relaxed.
Movie intervals fail the positive-duration definition in793224716(one interval)
and754312389(two intervals, other protocol), not the material-overlap check. All
their movie candidate cycles remain unadmitted. Primary grating feasibility is
reported separately from those failed secondary timing/trial checks.

Nearest-frame agreement on a dense periodic pulse train is not a uniquely
identified physical stimulus/condition match:integer-frame ambiguities cannot
be excluded by nearest distance alone. Provider stimulus-condition annotations
remain the target. The exploratory design is not an independently verified
stimulus-causality or absolute physical timing study.

The endpoint oracle was executed for371identifiable segments;103underidentified
segments remain unexecuted, rather than invented. The largest official-endpoint
versus all-code transform discrepancy is0.000877836369s. Both procedures use
the same barcodes, so agreement is not independent absolute accuracy proof.
Session839557629probeC(846401834) has exported sampling_rate=0 despite identifiable
earlier digital segments and no published probe invalid interval. This negative
provenance finding is retained. Other probes in that session provide429CA1 and
131DG anatomical potentials; the zero-rate probe must not be presented as
fully supported or silently patched by a derived rate.

Calendar date metadata disagree between native sync and NWB in54/58sessions.
These calendar origins are NOT reconciled or assumed interchangeable. Agreement
of dense non-neural frame times, unique barcode identities and matching probe
metadata supports the elapsed-time relationship, not absolute calendar truth.
An exploratory design must use relative master time and retain this provenance
limitation; any analysis needing accurate acquisition dates remains blocked.

## Why Original Native Continuity Still Fails

The public extractor writes int16,384-channel sample vectors and increments a
serialized sample counter. The pinned PXI code does not enforce its commented
hardware timestamp consistency check. Thus byte length/768 and exported zero
markers can establish serialized sample counts and declared chunks, not prove
that no hardware packets were lost or that every nominal100ms contains intact
physical observation. Barcode irregularities identify some macro-discontinuities,
not every micro-dropout. Sparse digital events do not supply all neural packet
timestamps. No analog samples were read to invent a continuity certificate.

The matrix explicitly keeps native_observation_certified=false and
continuity_certified=false. Conditional serialized durations are labelled
conditional; absence of gap flags is never converted to uninterrupted support.
Future lossless native-observation claims require additional authoritative packet
integrity/acquisition provenance, not a lower accuracy threshold or model result.

## Anatomy And Quantified Uncertainty

Every original channel/label/probe identity agrees with the new bounded coordinate
projection. All41270CA1/DG/CA3-labelled unit identities have finite stored CCF
coordinates. There are26620CA1,9678DG and4972CA3identities; these are not confirmed
single neurons or physiologically eligible units. Other MTL regions are not pooled.

The whitepaper describes dye-track optical imaging and atlas registration, but
also manual boundary adjustment using physiological features. Therefore provider
atlas labels are histology-assisted and physiology-assisted annotations, not
independent blinded per-unit subfield ground truth. No original tissue images or
independent histological annotations were reviewed. The projected public
ImageSeries route failed and is retained; it is not evidence that images cannot
exist elsewhere. No empirical localization-error distribution can be estimated.

| Label | Unit identities |Within20umof another channel label |Within40um |
|---|---:|---:|---:|
|CA1|26620|861|1760|
|DG|9678|902|1613|
|CA3|4972|350|661|

These distances are vertical within-probe channel-label proxies, not CCF border
distances, actual localization errors, drift bounds or confidence intervals.
All26FCsessions retain grating paired potentials in the declared40umproxy
sensitivity. This does not validate labels or remove physiology-assisted
registration bias. Absolute anatomy claims remain unsupported.

## Resolved Versus Unresolved

Resolved as metadata/timing evidence:complete denominator; native digital format
and relative barcode clocks; physical stimulus synchronization; real grating
conditions/repeats; frame-cycle versus trial distinction; known-invalid tag
attribution; unit/channel/probe/CCF joins; declared geometric sensitivity.

Critical for original admission:lossless native observation/continuity and true
per-bin exposure remain uncertified. A true native-clock regime study cannot
silently replace these with nominal curated-release bins.

Sensitivity/explicit limits for a distinct exploratory question:provider-assisted
anatomy, unknown registration error, unreported packet gaps, underidentified
segments, unresolved calendar dates, failed movie/frame diagnostics and upstream
whole-session sorting. Counts remain anatomical upper-bound potentials only.

Optional:behavior covariates were not decoded and do not block a prospectively
stimulus-controlled primary design. Omitting them changes neither the paired
stimulus question nor recorded exposures, but behavioral causal explanations
would remain unavailable. Original M0's warning files are not changed by this
new prospective classification.

## Bounded IBL Decision And Next Step

No new IBL acquisition was performed. Allen already has adequate common-protocol
timing-supported potentials. The old IBL inventory does not demonstrate that
missing lossless packet provenance or independent histology could be resolved
there. A new cohort search would not be justified by current evidence.

Recommend a separately authorized, prospectively registered curated-release
exploratory protocol as described in RECOMMENDED_PROTOCOL.md. Do not call this
original M0PASS or automatically start M1. No representation/regime, NAP, CWP,
neural primitive or cross-species validation is established.

## Sources And Access

- [Allen whitepaper Version1.0,2019](https://cdn.prod.website-files.com/689cfbd308fa7373b604d290/6a30107b2f53d6743336311d_neuropixels_visual_coding_-_white_paper_v10-compressed.pdf)
- [Pinned SDK processing definitions](https://github.com/AllenInstitute/AllenSDK/tree/a56bd8ea7613a812334602b64746cdd30c325a96/allensdk/brain_observatory/ecephys)
- [Pinned extractor](https://github.com/AllenInstitute/ecephys_spike_sorting/tree/919992748a5324724ba87169ecdcf9eb6e3b9973/ecephys_spike_sorting/modules/extract_from_npx)
- [Official data access documentation](https://allensdk.readthedocs.io/en/latest/_static/examples/nb/ecephys_data_access.html)

Only registered non-neural digital bits/edges, stimulus/invalid interval metadata,
anatomical coordinates, identities and structural attributes were decoded.
Uninterpreted digital bits and opaque NWB structural bytes were transported;
there is no zero-transport claim. No spike, waveform, analog neural/behavioral
data, unit firing/quality values, model scores or final holdout was inspected.
Raw digital caches remain locally hash-verified; compact metadata preserve exact
decompressed bytes. Frozen originalP1-P11/P12 artifacts remain unchanged.
