# P11-v2 Milestone Status

Separate study registered at commit base
8c2cdf92ce2567f68c49ede77d929f03c0c7424d. P11-v1 M4/NUM1/NUM2/NUM3 failures
are final and unchanged. This file never replaces paper11/MILESTONE_STATUS.md.

| Milestone | Scientific Gate | Evidence | Next Step |
| --- | --- | --- | --- |
| R0 original >=40 usable-trial admission | FAIL: DATA_INSUFFICIENT; immutable | results/R0_final/gate_result.json | Never reclassify |
| R0 authorized R0-TRIAL-1 >=32/train24/dev8 | PASS admission:9patients,23sessions; repair review cleared | results/R0_amendment1_code1/gate_result.json | R1 authorized |
| R1 original implementation | FAIL; preserved | results/R1/gate_result.json | Never reclassify |
| R1-CODE-1 implementation repair | PASS; independent review cleared | results/R1_code1/gate_result.json | R2 not executed in this scope |
| R2 development/nulls/external assessment | NOT EXECUTED | none | final holdouts LOCKED |
| R3 manuscript/A1-A10 | NOT EXECUTED | none | no scientific manuscript-completion claim |

Original R0 parser failure is preserved in results/R0. Append-only
R0-SCHEMA-1 recognizes actual recog/learn phase labels and site-qualified
Toronto identifiers. Its external METADATA SUBGATE passes:87/87 NWB files,
36 candidate patients,52 sessions,712 hippocampal labeled session-local units,
100 recognition trials/session. No spike arrays or prediction scores decoded.
This external subgate is not the combined R0 gate and does not authorize R1.

The combined gate applies minimum40 usable train+validation trials/session and
minimum8 development patients. Old test is forbidden and cannot supply usable
trial coverage. Only sub-03/ses-03 and sub-06/ses-02 reach40 usable trials;
therefore even before unit/rate QC the patient upper bound is2, not8.

Important denominator limitation: the initial protocol said minimum valid
trials/session without spelling out recorded versus usable. The conservative
usable interpretation is explicit in the final-gate registration, not secretly
changed to make the data pass. Any lower usable-trial criterion must be a
separate human-approved prospective amendment before new neural/model access.

Historical original execution status:WAIT_FOR_HUMAN_INPUT. Original safe R0 metadata, integrity, tests and
negative-result reproduction work completed. Keep source
provenance independence separate from private cross-cohort reidentification,
and metadata candidacy separate from physiological coverage/train-rate QC.

## Authorized Controlled Amendment

The user authorized32usable trials/train>=24/development validation>=8 based
on metadata coverage. Registration preceded real train/development-array QC.
No lower subject, unit or training-spike threshold is authorized. The original
>=40 failure and all v1 failures remain final. Final external60/40 and primary
oldtest locks remain unchanged; neither final partition was decoded.

Actual eligible cohort:9patients,23sessions,592session-local units,
622training trials,201development-validation trials. Unit totals are not
unique neurons across sessions. All selected units have >=20training spikes.
Training-only ordering QC excluded21units;4others failed training-spike count.
Ordering exclusions are conservative data criteria, not physiological findings.
Source observation-array coverage does not certify per-bin dropout masks.

Sensitivity with minimum5units:32trials admits9patients/23sessions;
36admits8/15;40admits2/2. At32trials and minimum10units:8/20;
minimum20units:6/13. See subject_table.csv/session_table.csv and cohort.json.

Independent review identified incomplete rejected-unit access logs and an
unsafe missing-cache replay path. Original evidence/source preserved;
R0-TRIAL-1-CODE-1 was registered before repaired real QC. All23count-feature
objects remain exactly identical. The repair records every decode attempt and
fails closed before missing/corrupt saved artifacts can trigger raw reads.
33R0 tests PASS and actual code1 PowerShell reproduction exits0.
R0 is admission/engineering evidence, not a predictive scientific result.
Independent repair review cleared both P1s:21,546allowlisted decode entries,
including22reads across all21ordering exclusions; no excluded-unit development
reads.37registered inputs,52locked artifacts,408prior artifacts and2,514archive
files match. All23feature files are byte-identical. R1 activated only after this
clearance. R2/R3 remain unexecuted and final holds remain locked.

## R1 Controlled Verification

Initial R1 FAIL remains immutable:1bitwise trial-reset failure and14temporary
fixture permission errors. R1-CODE-1 registered an append-only per-trial
recurrence/readout implementation and workspace-local fixture directory.
All17original test methods/assertions are unchanged; one determinism regression
was added. No likelihood threshold, seeds, ridge grid, budget or model family
changed. No preset grid fits occurred in the initial failed attempt.

Fresh CODE-1:18tests PASS; combined R0/R1 unique51tests PASS.220numerical
cases and54causal checks pass. Maximum score errors in nats/unit-bin:
Poisson9.094947017729282e-13, state1.1102230246251565e-15,
recurrent4.440892098500626e-16; threshold remains1e-10.
Maximum analytical-gradient central-difference error3.555037817945528e-11
under separately registered1e-6gradient criterion.

All169controlled fits retained:1stationary,60regularized baselines,
24discrete,36continuous and48hybrid. All converged; maximum273iterations,
zero coefficient-bound hits. Fitting time sum6.453251700208057seconds excludes
tests/registration. Fixture software verification only, no winning family.
Actual PowerShell code1 reproduction exits0, saved-only and no holdout reads.
Independent mathematical/evidence review cleared P0/P1:13source,
473preceding,2,514archive and8artifact hashes matched. All169required run
identities present; independently reconstructed objectives agree to4.441e-16.
Real development fitting, null tests, subject effects and external physiological
coverage/final validation remain NOT EXECUTED; R2/R3 are not implied PASS.
