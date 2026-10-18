# Independent internal complete native-input review 1

Mission P15-DEV-EXACT-NATIVE-REPAIR-R1; owner BASE b0b692bd9b7e42f767117a51d0119644327a97f0. Review occurs after corrected A reconstruction and before real corrective fitting. Historical paper15_dev and prior unsuccessful native-repair reviews remain immutable.

**Decision: ACCEPTED_CORRECTED_DEVELOPMENT_INPUT_GATE; open P0=0, open P1=0.** Corrected admission is10 Development mice from8 laboratories, under the unchanged12-candidate roster and original thresholds. This is input/source/QC acceptance, not production numerical certification, any fit result, B/E scientific release, Final access or full mission PASS. The independently reviewed production numerical/integration gate is still required before real fits.

## Independent verification performed

I reviewed revalidate_inputs.py, input_oracle.py, verify_wheel_indices.py, the current reader/cache/serialization path and their actual saved results. I also executed two new review-only verification scripts with ResourceWarning treated as error; both exited0. They wrote only new review receipts, not production data or fitted states.

- **All12 Development source metadata:** verified current frozen-reader descendant hashes; original receipt-bound cache bodies before decoding; native trial field order/dtypes, rows and numeric compatibility values; exact finite float bits and hex; retained missing/nonfinite handling; source AP header duration/sample accounting; finite monotone sync and no-extrapolation support; known saturation interval mapping; native cluster-channel-atlas identities, provider labels and UUID order; original A/B/E masks and guards against the independent scalar mask oracle. All12 agree with the corrected states.96642 is the count of **finite binary64 numeric table cells across all fields**, not96642 distinct timestamps.
- **All ten corrected A streams:** opened only authorized saved A exports. Independently recomputed target counts/history and all37 nuisance columns with the scalar source-level oracle. Computed all69 non-intercept scaler columns directly as sum/N and sqrt(sum of squared deviations/N), using A scored rows only, without production design/fit_scale. Every mean, population SD, SD>=1e-8 active flag and entire +/-3 clipped/intercept design matrix matches the sealed states/tensors exactly. Across ten mice this covers690 scaler columns,37870 scored population-bin rows and302960 nominal scored unit-bins. All four C configurations' source-count micro-rate means/SD/active maps also agree for every mouse; other C transform/scaler states are hash-bound and retain the unchanged registered mathematical implementation, pending the separate complete production numerical gate.
- **All382487 strict-past queries:** recomputed bin-start, bin-minus.05/.1/.25/.5 and epoch-start predecessor indices using scalar bisect and compared exact integer indices and strict inequalities. No timestamp tolerance was used. The original actual PL033 trial224 event is precisely1150.1833035011502 seconds (`0x1.1f8bbb3e9babbp+10`); its predecessor is394299 and the next sample equals the boundary, so the equal sample is excluded. The historical rounded boundary1150.1833035012 would select394300. This is the actual native/wheel source witness, not only a synthetic constant.
- **All446 physiological candidate units:** independently recomputed counts, within-epoch ISI pairs/refractory numerator and fraction, exposure/rates, original chronological-quartile exposure/count/rate, primary eligibility, strict-QC flags and exclusion reasons, ranking and selected UUIDs from the ten saved A streams. Derived the complete candidate unit lists anew from native MOp mapping and provider label==1, preventing an unnoticed reduced QC denominator. All records agree;314 qualify and80 are selected (eight per mouse). Source and A-role ordinal artifacts were hash-checked and independently checked for full-stream length, increasing original source-row ordinals and consecutive A-role ordinals on all ten mice.

The first review receipt performed the full mean/SD/design recomputation for all ten mice and initially recomputed detailed QC only for PL033's21 units. The second supplemental receipt independently extends QC to **all446** and ordinal consistency to all ten mice. The original first receipt remains unchanged; its initial QC scope limit is resolved by this explicitly separate supplement.

## Source reconstruction and scope interpretation

The original raw-source projection itself was performed by the prospectively gated, reviewed trusted reader/cache path. Its source bodies are matched by original object key, size and SHA; its A projection includes every source event in the native chronological A interval, including events outside eligible epochs. The separately reviewed scalar audit scans the original Development source in bounded chunks, reproduces the full A stream and records original source-row ordinals. I inspected that implementation and its saved per-mouse evidence. I did not independently reopen whole-recording neural files: my numerical reexecution uses the complete saved A streams, while exact original-raw-to-A correspondence additionally rests on the reviewed reader/auditor execution and bound source receipts. No B/E neural outputs or Final neural values were accessed by these review scripts.

This distinction preserves the approved review boundary and avoids claiming an unperformed independent raw B/E decode. Actual A streams, target/history/feature matrices, full QC and scaler calculations were independently reexecuted. The accepted source audit's full-role correspondence plus retained source order supports S07's later unit-local source-event ordinals; the review does not substitute this for the later role-specific thinning/control gate.

Typed canonical storage retains source classifications and bits. The numeric compatibility view is the bit-verified downstream view, with legitimate NaN/pd.NA missing semantics and preserved infinity handling through the tagged loader. No rounded historical trial values were used as source truth. The producer verifies original index and native class encoding; this review additionally compares current native field/dtype/row layout and numeric values. Hashes bind both the exact sidecar and the actual numeric consumer view.

## Admission, historical differences and original failure

NYU-37 remains excluded because B has31 valid epochs below the unchanged minimum40 (A83/E41). CSHL059 retains its original finite identity sync table with registered domain[0,1]; no-extrapolation support yields A/B/E0/0/0. These are original per-mouse coverage exclusions, not a malformed-sync allegation or a new source-wide rule. Neither animal is substituted and no Final mouse is reassigned. The independent metadata-mask audit agrees for every original row, including these exclusions.

The corrected ten-mouse/eight-lab roster, selected UUIDs and A raw streams agree with history on the saved source audit; target-cell differences versus historical A tensors are0. This is a measured agreement, not a forced repair target. Corrected full design matrices do change, as expected when exact native events and newly computed A scalers replace invalid rounded inputs:

| Mouse | Maximum corrected-versus-historical X difference |
|---|---:|
| KS046 |7.146863101326062e-10|
| PL033 |0.033367945730257476|
| SWC_043 |0.024326208825078854|
| SWC_038 |0.05898135548476802|
| CSH_ZAD_026 |1.7283180442362323e-10|
| NYU-30 |6.112816919312536e-10|
| KS051 |0.05802005674779154|
| ZFM-01937 |1.7191464918298038e-10|
| CSH_ZAD_019 |0.02946601689315803|
| UCLA035 |6.616445169527196e-10|

These table values are the bound full-source audit's historical comparison; this review did not reopen historical feature tensors or any historical fitted endpoint. No newly chosen magnitude tolerance converts the five smaller differences into unchanged scientific inputs. All ten fresh designs were validated against their native definitions. Historical358 numerical PASS/one interrupted/251 unstarted records remain historical rounded-input evidence; this input acceptance never retroactively validates them or supplies their coefficients to fresh initialization.

## Commands, receipts and identities

Executed from the repository root using the existing project runtime, no fitting:

`paper15_dev\\work\\runtime\\Scripts\\python.exe -W error::ResourceWarning -c "import runpy; runpy.run_path('ops/evidence/2026-10-17/p15-dev-exact-native-repair-r1/verify_full_native_review_1.py', run_name='__main__')"`

`paper15_dev\\work\\runtime\\Scripts\\python.exe -W error::ResourceWarning -c "import runpy; runpy.run_path('ops/evidence/2026-10-17/p15-dev-exact-native-repair-r1/verify_all_qc_review_1.py', run_name='__main__')"`

Both scripts refuse to overwrite their existing receipt. Preserve them; their existence is not permission to rerun/reconstruct scientific inputs. The receipt inputs additionally bind every reviewed source metadata object, corrected task, A export, preprocessing/QC and ordinal state.

| Artifact | SHA256 |
|---|---|
| paper15_r1/revalidate_inputs.py |1e24be7d0b800474ed2f12ba545a82a3dc39de731c6f0ee1baa98975f716ffc1|
| paper15_r1/input_oracle.py |80c36268db3cf40b6453b511b41404d1411467826352665ff22473c90fae7382|
| paper15_r1/verify_wheel_indices.py |d40e453dc1be038ee48deab77d7c46e32490a1258f2ec2d5dd168b463c6050db|
| paper15_r1/results/FULL_A_SOURCE_REVALIDATION.json |77746c3cc4711884918bef7694f7521387d4e2bc8746ff934853babdb59bd45d|
| paper15_r1/results/EXACT_WHEEL_INDEX_VERIFICATION.json |3c0f1265b4a25a7821e05c8df24acb30582435ec9a5221040865abe375f9dd29|
| paper15_r1/results/M2_PHYSIOLOGY_GATE.json |7de5edf523a04f1e945ff8cf65ca2b080ca390154cf8ba07104abbea5833304e|
| paper15_r1/READER_GATE.json |d9d6dd7ea737216d44faa57d682d32a92a7a2356a72088bdc7f7813788a7749b|
| verify_full_native_review_1.py |b26779550b5abe0539af241b1093b76f2cdbbaa93c5ed421ef39ae617c18c992|
| FULL_NATIVE_INPUT_REVIEW_RECEIPT_1.json |9cc332a2167fce18c93f30422db61d34c0b71f4632f81f173d20c82d3c6d0a79|
| verify_all_qc_review_1.py |7043c34bcfd719537aa53de52241cc7dc9dc042f8d491279bfc014a238fc7ef8|
| FULL_NATIVE_QC_REVIEW_RECEIPT_1.json |1cf05e4b0d0cac03537ff26b5065b2f49262bc7c2b0f08bd398bedc0e07161e1|

The last four paths are in this mission's evidence directory. Serialization/reader/cache/math identities remain those independently accepted in NATIVE_REPAIR_REVIEW_2.md and the verified current READER_GATE. No versioned production file, source snapshot, original scientific definition, original result or previous review was modified by this review. The new versioned fit directory contained no fit JSON at final check. Production/numerical certification and all later scientific gates remain pending; Final C/D access remains forbidden.
