# R2 Scientific Stop And Limitations

R2 gate FAIL; scientific verdict DATA_INSUFFICIENT; dynamical-regime verdict
INCONCLUSIVE. Engineering tests and development model execution do not override
the failed external-support gate. R3 was not executed.

## Completed Development Evidence

Nine independent patients,23sessions,592session-local hippocampal units,
622training/201development trials. All3,887required candidate/seed fits
converged; no failed seed was excluded. All108controlled numerical cases pass:
maximum score error1.1102230246251565e-15nats/unit-bin and gradient error
3.1667389197020945e-11. These tests are not a global optimizer certificate.

Equal-session-within-patient, then equal-patient development means:

| Representation selected under frozen rules | nats/unit-bin |
| --- | ---: |
| Strongest Poisson baseline, combined ridge0.001 | -0.5349213147416831 |
| Discrete K2 ridge0.01 | -0.5471759733084931 |
| Continuous d1 ridge1 | -0.5680885963548558 |
| Hybrid K2 lag1 ridge0.01 | -0.5462372511131538 |

All three selected families have negative patient-averaged differences versus
the strongest baseline. Discrete/hybrid are above baseline for sub-05 and below
for the other eight; continuous is below in all nine. Existing10,000patient
bootstrap intervals and512exact sign flips,
with Holm6 correction, are preserved. Development data were already exposed;
these post-selection statistics are exploratory, not confirmatory. Strongest
baseline uses maximum development score while family choices use frozen one-SE
complexity selection. This is not a claim about every possible family model.
The one-SE discrete selection is not a physical hippocampal-regime conclusion.

The raw development maximum across all57configurations is hybrid K4/lag5,
ridge0.001,score-0.514053175318272; the raw discrete K4/ridge0.001 score is
-0.5153939231286009. These exceed the baseline raw score, but the frozen
one-SE rule selects lower-complexity, more-regularized configurations. All57
scores are retained; the negative selected-model comparisons must not be
generalized to every grid configuration or used to revise selection after
seeing results. Independent validation remains absent for every configuration.

Some L-BFGS-B successes stop on relative objective tolerance, including
one-iteration stops with gradients above gtol. Frozen criteria are unchanged;
global optimality and identifiability are not established. Original design_rank
is first-unit rank, not joint rank; complexity uses nominal total coefficients.

## Mandatory External Gate Failure

Frozen DANDI000004release0.220126.1852:52candidate sessions/36metadata patients.
The registered metadata-only boundary procedure requires independent recording
start/end support, not first/last spikes. Forty-seven sessions passed this
support procedure, five remain UNKNOWN_SUPPORT. Their first TTL values:

| Asset ID | First TTL |
| --- | --- |
| 37347191-3430-47bb-a3b5-81bc1d81239e | 1.0 |
| 383557c1-167f-42f4-be1e-6bb7d6948774 | 1.0 |
| 5f8737c1-8cc2-4ea2-8c00-085722c15db0 | 1.0 |
| bed1fc5b-e8d1-40b1-9780-532df3f35804 | 1.0 |
| dab65d89-d309-4a67-bccb-d8f840961cfa | 99.0 |

None matches required recording-start55. Rejection precedes end-time decoding
for these five. This cannot certify full registered coverage; it does NOT prove
the recordings are incomplete or that the cohort has fewer than eight eligible
patients. Publication-level continuous-recording statements do not establish
per-unit dropout masks. No alternative post-hoc boundary mapping was accepted.

Only bounded metadata byte ranges/scalars were decoded. Opaque adjacent bytes
can be transported by HDF5 range buffering; no external spike values, spike
indices, rates, waveforms, calibration physiology or final scores were decoded.
External training-only unit QC and true eligible-patient counts remain unknown.
The recognition task differs from primary verbal working memory; a future
external result would be convergent validation, not direct replication.

## Null Execution And Preservation

The critical gate stopped the parent process by CTRL_C(exit1). Eight complete
count-permutation cohort replicates and2,896converged saved null fits remain;
a ninth replicate was interrupted. No corrupted saved JSON files were found.
Registered200replicates per type were not completed. Circular shifts and task
timing controls were not executed. No partial-null p-values are reported.

Oldtest was never read. External60/40split SHA256 remains
27fad80c753cfdef00977d056b379da5210f1e0247efba803a4e098e593e93e3.
No external spike acquisition/fitting/final evaluation occurred. Archived
P11-v1 and R0/R1 failures remain immutable. No NAP/CWP validation claim is made.

## Blocker Audit And Permissible Recovery

Blocked requirements:complete external recording support/physiological
eligibility and final evaluation; mandatory null completion is stopped by this
critical gate. Metadata acquisition, source-site/task audit, exact frozen asset
inspection and independent boundary checks were exhausted. Initial registration
defect and transport failure remain separately preserved; a prospectively
registered transport retry obtained all52metadata records, exposing the actual
scientific limitation rather than masking it.

Do not resume this failed attempt, drop five sessions, infer support from spikes,
relax gates or inspect a holdout to design a fix. A human-authorized separately
registered study/amendment needs independent recording-support/clock evidence,
or a demonstrably independent suitable cohort and new prospective safeguards.
Such authorization must specify the evidence and rule before physiological
evaluation. Current R2 remains failed regardless of any future recovery.
