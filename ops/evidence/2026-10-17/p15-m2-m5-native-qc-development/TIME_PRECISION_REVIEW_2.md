# Independent internal timing-fidelity review, revision 2

Mission: P15-M2-M5-NATIVE-QC-AND-DEVELOPMENT. Review scope: frozen source definitions, saved timing audit and an independently implemented Development A task/wheel-metadata-only predecessor-index diagnostic. This is an internal scientific/source review, not external peer review or authorization to repair/restart scientific execution.

## Decision

**One open P1; zero P0. VERIFIED_SOURCE_FEATURE_FIDELITY_DEFECT. The frozen source/causal-feature gate fails. Do not proceed to B selection, E scoring/controls, Final access, additional fitting or an unregistered repair/refit.** Preserve all completed and interrupted attempts, original inputs, production freezes and previous reviews. Numerical PASS of an objective evaluated on the saved rounded inputs cannot establish fidelity to the registered native-event objective.

The finding is supported by an exact discrete index change, not by choosing a post-hoc acceptable floating error. It is not necessary to impose a new magnitude cutoff to establish this defect.

## Registered definition and implementation

SCIENTIFIC_PROTOCOL.md, Partitions and exposure, requires serialization of the pinned native trial ordinals/values before neural QC. FEATURE_MODELS.md requires source events/samples strictly before each bin start; equality is deferred. Its columns24-36 use backward-held wheel values and strictly past intervals. SOURCE_QC.md requires native event/support definitions, half-open intervals and backward sample-and-hold without future interpolation. These are source-value and causal-boundary requirements.

metadata_qc.py serializes the native trial table using `tr.to_json(orient='records')` without specifying `double_precision`; the installed Pandas default is10 decimal places. Saved native float64 values are consequently changed before they determine feature-bin schedules. The protocol contains no separately registered10-decimal timing policy or timing-equivalence tolerance. The float64 numerical policy, AP one-sample support allowance and derivative tolerances do not authorize quantizing event boundaries.

## Direct mechanism and numerical evidence

The unchanged primary TIME_SERIALIZATION_AUDIT_1.json compares native/saved task representations on the same selected eight-unit saved A exports and the same existing A scalers. It reports unchanged counts/history and masks in that limited comparison, but nonzero wheel nuisance and standardized design changes for5/10 mice.

I executed a separate diagnostic, audit_time_indices_1.py, using only native trial metadata, saved task JSON, wheel timestamps/positions and saved scaler JSON. It opened no neural arrays/A exports and ran no fitting. Native/saved task SHA256s agree with the primary audit; wheel body SHA256s agree with the saved20-object body-readback receipt; scaler SHA256s agree with PRODUCTION_GATE. The diagnostic directly computes `searchsorted(wheel_times, query, side='left') - 1` for native versus rounded query schedules, with **exact integer index inequality** as the sole changed-index rule.

| Mouse | Changed query indices | Maximum standardized wheel-column change |
|---|---:|---:|
| KS046 |0|0|
| PL033 |8|0.03339247812482948|
| SWC_043 |4|0.02434193182883293|
| SWC_038 |12|0.05892361851165395|
| CSH_ZAD_026 |0|0|
| NYU-30 |0|0|
| KS051 |4|0.05804881832281805|
| ZFM-01937 |0|0|
| CSH_ZAD_019 |4|0.029465269956445828|
| UCLA035 |0|0|

There are32 changed query evaluations over5 mice:8 bin-start indices,8 at bin-minus.05,8 at bin-minus.1 and8 at bin-minus.25. Epoch-start and bin-minus.5 indices do not change. Thus32 is a count of queried predecessor indices, **not32 independent events or animals**; the8 bin-start events also recur in those lagged queries. Every changed held index in this diagnostic changes the held position. All changes are one predecessor forward for the rounded schedule.

A concrete witness is PL033 original trial224, scored bin index10 (indices0-9 are warm-up):

- Native stimulus/bin boundary and wheel event time:1150.1833035011502 seconds, float hex `0x1.1f8bbb3e9babbp+10`.
- Rounded boundary:1150.1833035012 seconds, hex `0x1.1f8bbb3e9bb96p+10`.
- Native strict predecessor394299 has position-369.2751950677104; rounded predecessor394300 has position-369.2767290484983 radians.
- The crossed event is equal to the native query, so `event < native_query` is false; `event < rounded_query` is true. This is a direct change in the frozen strict-past availability predicate, despite the small time difference.

Independent reconstruction of all14 wheel nuisance columns matches the primary audit's recorded per-column maxima for every mouse. Applying the existing A scaler/clipping maps yields the wheel-column changes in the table, matching the five primary-audit total-X maxima. That arithmetic cross-check used1e-12 only for comparing two floating arithmetic reports; it is not a new scientific tolerance, and the source-fidelity conclusion rests on exact integer index changes. Rate/squared-displacement features and existing scaling propagate a one-encoder-step held-value change to the reported design differences.

## Limits and preservation

The primary audit is a useful controlled diagnostic: source time representation changes while the selected units, existing A export and existing A scalers are held fixed. I inspected its code and receipt; I did **not** rerun that script, because it opens neural A arrays. Its counts/history equality applies only to that saved A-export/selected-unit comparison. It does not prove equivalence for all original raw role-boundary spikes or S07 role ordinals: existing exports were themselves made using the saved task boundaries. Its field-error loop also compares jointly finite values without a separate changed-missingness counter. Neither limitation can erase the independently demonstrated wheel-feature defect.

No conclusion about the sign/size of predictive effects or biological dynamics follows. No claim is made that every fitted coefficient would change, or that this index audit validates whole-role extraction. Five mice with no changed wheel indices still have small continuous time-feature differences in the primary audit; no new tolerance is supplied to declare those scientifically equivalent.

Previous reader, numerical, worker and evaluation-component reviews remain immutable evidence of their stated scopes. They did not independently establish bitwise/semantic equivalence to the native event times; saved-input integrity and numerical correctness are narrower than source-feature fidelity. The parent reports that its active A worker was interrupted and B/E/Final gates stayed closed; this metadata-only review does not independently certify process termination or all execution journals. Those must be bound into the stop archive separately.

The minimum next action in the current mission is an evidence-preserving scientific STOP/closeout. A future recovery, if separately authorized, must prospectively specify a lossless native-time representation, equality/boundary regressions, full impact/attempt accounting and the authorized recalculation/refitting scope. This review neither changes the source snapshot nor executes that repair.

## Reproduction and reviewed identities

Executed from repository root with exit0 and ResourceWarning treated as error:

`paper15_dev\\work\\runtime\\Scripts\\python.exe -W error::ResourceWarning -c "import runpy; runpy.run_path('ops/evidence/2026-10-17/p15-m2-m5-native-qc-development/audit_time_indices_1.py', run_name='__main__')"`

The script refuses an existing receipt. Preserve TIME_INDEX_AUDIT_1.json; do not delete it to rerun. Reproduction of the scientific attempt is not authorized by this diagnostic command.

| Reviewed file | SHA256 |
|---|---|
| audit_time_serialization.py |68138a7f818e89ac28ccbb842e7cd9a477e28ad11ebfecd8a11e9e2223e3709e|
| TIME_SERIALIZATION_AUDIT_1.json |6a682d4f54154f4c6899cda3f9a16496bf03b2e2cdafd03971a588800508a078|
| audit_time_indices_1.py |798304461ffb1eb211b7e98a95859c4997047dc65c80075b60829f020a80bd8c|
| TIME_INDEX_AUDIT_1.json |e4029407fb960e249130e3cf15b052cd2b587aa43226d35609a605423a1d6e9a|
| TIME_PRECISION_REVIEW_1.md |0429772405f8f8ecb68bb56b75c3966e526f0b985b18eb3db54fbcbc93c9bdf9|
| paper15_dev/metadata_qc.py |14068246912971fea75eacc510afd088230d1b1e174d14c175d9e17319008ecf|
| paper15_dev/features.py |30d17b3a902429537e8b83fc9ac5a483933bdb8080ff890c5f43c6fc5f4dd3fd|
| paper15_dev/training.py |1c11098672df8d24c54770375c6c0c8db351622d533badf30bc11170dba0212d|
| paper15_dev/reader.py |fc3f4df8d29a2bd26dafa083fecf66e99892ec3d9fa28926bf66796dda9be613|

The new receipt additionally records the source freeze, production gate, Python/Numpy/Pandas versions, native/saved task, wheel body and preprocessing hashes per mouse, and exact hexadecimal query/event witnesses. No core implementation/scientific definition, existing input, primary audit or previous review was modified in this review.
