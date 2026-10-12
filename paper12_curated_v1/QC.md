# QC - Registration and Stopped Access Preflight

M1: exact checkpoint;all26unique animals and26sessions retained;13/13SHAallocation;
all15600unique grating row IDs retained;8conditions x75trials/mouse before exclusions;
45train/calibration and30validation/final percondition before frozen masks.
All20664CA1/DGunit IDs enumerated;82known-quarantined IDs retained in inventory.

Bin policy:first exact2seconds with20nominal100ms half-open bins. Seven provider
presentations have duration<2seconds,so are excluded rather than padded. Probe
anchor/known-invalid masks use full region-common selected candidate probe sets.
Allmask reasons retained in locks/trials.json;no replenishment or repartition.
Mask reason totals can overlap;unique exclusions are separate in summary.json.
All26mice pass metadata trial coverage,not physiological eligibility.

M2: uniform same-object schema-only preflight;ETag/Range/length checks;no unit
metric values,index endpoints,timestamps,waveforms,analogs orbehavior decoded.
Initial sandbox DNS failure is preserved in results/M2/schema/766640955.json;
same scoped path succeeded with authorized network execution in schema_network1/.
No silent source version change,failed session deletion or positive gate rescue.

Read-boundary diagnosis:ragged unit-vector boundaries locate a unit,not an arbitrary
trial's permitted spike range. Shape/chunkmetadata cannot distinguish synthetic
sequences ofsame shape havingdifferent temporal membership. A verified time-index
or separately authorized custodial derivative is missing. Whole-session SDK and
binary-search timestamp probing not used. This does not prove allpossible safe
custodial implementations are impossible;it defines the exact current boundary.

Physiological QC,spike count integrity,modelnumerics,convergence/nulls and scientific
statistics NOT_EXECUTED. Final outcomes LOCKED. No DATA_INSUFFICIENT inference.
Original five scientific warninggroups remain;new access blocker retained.
Fresh automated tests and saved-only nativePowerShell proof are evidence/.
