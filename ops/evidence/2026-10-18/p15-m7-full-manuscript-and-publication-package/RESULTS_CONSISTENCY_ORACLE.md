# Reviewer-owned results consistency oracle

Mission: P15-M7-FULL-MANUSCRIPT-AND-PUBLICATION-PACKAGE. Reviewer: `/root/gradient_review`. Base: `bdec0e19621cc8018abe11c5633ce76aff611443`.

JSON oracle SHA256: `168fc02a5a9552672d5ef92fb7ac043f53f0745e67af1bab48503298d67007a9`. Exactly 48 used old sources match the frozen 3099-file SOURCE_HASHES map (lock SHA `529a361ab349eb85bf76284265b76241e09d8b6a21ecb12d7194c69c0f5efc04`). This oracle transcribes saved results and cross-checks the12 existing main JSON/CSV rows; it imports no scientific module and performs no new scientific calculation,CI/test,model evaluation,fit or D assessment. It is an editorial consistency oracle,not a manuscript or scientific PASS.

## Cohort and interpretation

Original20 identities =12 Development +8 Final-reserved. Analyzed:10 Development mice/8 labs and6 Final mice/4 labs. Four immutable exclusions: NYU-37 (B31<40 epoch floor),CSHL059 (identity sync[0,1],zero covered epochs),NYU-21 (native wheel strict-order failure;16,485 ties),UCLA033 (six C-qualified units<eight). No replacement or pooled16-animal inference. Development is exploratory; every available Final comparison is DESCRIPTIVE ONLY.

The registered comparison order is primary B4-B1, own B4-B3, other B4-B2, D-B4, C-B4, D-S. File/alphabetical order is not the registered comparison order. Here C/D model names are distinct from calibration-C/assessment-D partitions.

## Exact archived main results

|Cohort|Contrast|Mean nats/unit-bin|95% mouse interval|Raw p|Holm5 p|Positive mice|
|---|---|---:|---|---:|---:|---:|
|Development|B4-B1|0.1125291851306621|[0.06745810552609997, 0.16368155129436163]|0.0009765625|primary|10/10|
|Development|B4-B3|0.03930120524139896|[0.01734158461894405, 0.06278710159999801]|0.01171875|0.05859375|9/10|
|Development|B4-B2|0.026306579812766885|[0.0050302065057874785, 0.05501082886164163]|0.044921875|0.1796875|8/10|
|Development|D-B4|-0.01477973215700219|[-0.03601613299004298, 0.0021497034444591255]|0.19921875|0.59765625|4/10|
|Development|C-B4|0.00010824211289161302|[-0.000400099229921444, 0.000568692298035778]|0.685546875|0.859375|5/10|
|Development|D-S|-0.0019684110379102277|[-0.0059149205271999674, 0.00047306207126944814]|0.4296875|0.859375|5/10|
|Final|B4-B1|0.08658239652342035|[0.04944033234175033, 0.14110164811873427]|0.015625|primary|6/6|
|Final|B4-B3|0.05208972400526927|[0.03441612054329819, 0.07346442266178636]|0.03125|0.15625|6/6|
|Final|B4-B2|0.006353386392021677|[-0.008903428833930957, 0.022405637931404047]|0.53125|1.0|5/6|
|Final|D-B4|0.00235862122254638|[-0.003948272203674794, 0.009196280435455508]|0.53125|1.0|3/6|
|Final|C-B4|0.00013410738971923112|[-5.783408566630739e-05, 0.00034291798308512485]|0.28125|1.0|5/6|
|Final|D-S|0.0016697806796088692|[-0.00030445108225563776, 0.0051111034674382804]|0.5625|1.0|2/6|

All five secondary Holm tests are nonsignificant in each cohort. Development D-B4 is negative and Final D-B4 has a positive descriptive mean; no new pooled/difference test or biological transition follows. Final primary width0.09166131577698394 exceeds0.01; Development primary width0.09622344576826166 also exceeds0.01. The n6 confirmation floor and sign-exchangeability/independence limitations cannot be overridden by a positive mean or small raw p. At n6,64 signs give raw minima1/64 (primary),2/64 (secondary),and fixed Holm5 minimum0.15625: resolution,not power/equivalence.

## All eleven baseline-only sensitivity cases

Each row below prints saved B4-B1 / B4-B3 / B4-B2 means in that order. Exact CIs,mouse effects,subjects,statuses and positive counts for all66 cohort×case×contrast panels are copied in the JSON. No case tests are added. B0–B4 refits do not supply D/C/S robustness. S04 uses100ms; its raw nats/bin magnitude is not interchangeable with50ms.

|Case|Definition|Development n|Development three means|Final n|Final three means|
|---|---|---:|---|---:|---|
|S01|first5 units|10|0.12195632940390566 / 0.0559101314103788 / 0.02484832849760004|6|0.09321962253669325 / 0.07628146213427923 / 0.004594268277979672|
|S02|first12 units;capacity conditional|9|0.11871085900925296 / 0.037484085426126 / 0.0272702438413701|6|0.0684971295279402 / 0.041036095410575825 / 0.004037491309321617|
|S03|first20 units;capacity conditional|6|0.13378185928608757 / 0.03422748006976996 / 0.038781023088903986|4|0.07883288204171675 / 0.03374647287407973 / 0.006350271803740629|
|S04|100ms bins|10|0.23351777143002206 / 0.049188179949442176 / 0.057045412236386|6|0.16734705426807273 / 0.08393125755495662 / 0.009889416147438457|
|S05|250ms neural history/warmup;behavior reference unchanged|10|0.09855366226807691 / 0.03540659250366672 / 0.026534894103679714|6|0.11767008319481387 / 0.03688724124867901 / 0.03219263001899473|
|S06|strict C/A-only physiology QC|10|0.11258296227990279 / 0.03913059240182632 / 0.026367954181606916|6|0.08511287780897638 / 0.05342777909331508 / 0.0062747118622079|
|S07|role-local rate thinning;expected2Hz cap|10|0.02525243900120209 / 0.010126573302771894 / 0.008902389347151957|6|0.013317138764047222 / 0.00782309615208021 / 0.003968478150622837|
|S08|known saturation dilation10ms|10|0.11251173343986576 / 0.03929189672956811 / 0.02622141219502842|6|0.08653775633545079 / 0.05202684640367078 / 0.00625492701839075|
|S09|known saturation dilation50ms|10|0.1130150886670033 / 0.039287748249899924 / 0.02679895671682388|6|0.08701024020812814 / 0.051676630788648946 / 0.006643071325496499|
|S10|rich drift41 nuisance columns|10|0.1106683881754158 / 0.03799685745440893 / 0.02835224324858488|6|0.08541642599700137 / 0.048770872972138 / 0.006568525961427578|
|S11|first5 units meetingfive-contact MOp boundary proxy|10|0.12195632940390566 / 0.0559101314103788 / 0.02484832849760004|6|0.09321962253669325 / 0.07628146213427923 / 0.004594268277979672|

Mandatory cases are S01 and S04–S11; S02/S03 remain capacity-conditional. Development has105 available/5 capacity-missing subject×case records; Final has64/2. Final S03 has4 mice,below the6-mouse aggregate inference minimum,with saved descriptive means/CIs retained. Missing cases never become a successful robustness condition.

## All four references and failed panels

Cells show above-reference-median mice/n,disruption gate,raw reference p/Holm4 p. N3 is the copied B4-LL wheel reliance diagnostic,not a D/C wheel-null test; its “true” diagnostic conjunction does not supply general movement independence. N4 unavailable cells retain their fixed p1 slots. Full per-mouse pre-D coverage and exact control-source paths are in the JSON.

|Cohort|Contrast|N1|N2|N3 diagnostic|N4|
|---|---|---|---|---|---|
|Development|B4-B1|7/10;False;0.001/0.004|10/10;True;0.001/0.004|10/10;True;0.001/0.004|unavailable/5;unavailable;1.0/1.0|
|Development|B4-B3|7/10;False;0.001/0.004|10/10;True;0.001/0.004|10/10;True;0.001/0.004|unavailable/5;unavailable;1.0/1.0|
|Development|B4-B2|9/10;True;0.001/0.004|9/10;True;0.001/0.004|10/10;True;0.001/0.004|unavailable/5;unavailable;1.0/1.0|
|Development|D-B4|3/10;False;0.901/1.0|7/10;False;0.001/0.004|10/10;True;0.001/0.004|unavailable/5;unavailable;1.0/1.0|
|Development|C-B4|7/10;False;0.001/0.004|10/10;True;0.001/0.004|10/10;True;0.001/0.004|unavailable/5;unavailable;1.0/1.0|
|Development|D-S|7/10;False;0.001/0.004|5/10;False;0.059/0.118|10/10;True;0.001/0.004|unavailable/5;unavailable;1.0/1.0|
|Final|B4-B1|6/6;True;0.001/0.004|6/6;True;0.001/0.004|6/6;True;0.001/0.004|unavailable/3;unavailable;1.0/1.0|
|Final|B4-B3|6/6;True;0.001/0.004|6/6;True;0.001/0.004|6/6;True;0.001/0.004|unavailable/3;unavailable;1.0/1.0|
|Final|B4-B2|5/6;True;0.001/0.004|5/6;True;0.001/0.004|6/6;True;0.001/0.004|unavailable/3;unavailable;1.0/1.0|
|Final|D-B4|5/6;True;0.001/0.004|4/6;False;0.871/1.0|6/6;True;0.001/0.004|unavailable/3;unavailable;1.0/1.0|
|Final|C-B4|5/6;True;0.001/0.004|5/6;True;0.001/0.004|6/6;True;0.001/0.004|unavailable/3;unavailable;1.0/1.0|
|Final|D-S|4/6;False;0.001/0.004|2/6;False;0.622/1.0|6/6;True;0.001/0.004|unavailable/3;unavailable;1.0/1.0|

Development primary N1 fails7/10<8; N2passes10/10. Final primary N1/N2 pass6/6 but do not alter DESCRIPTIVE ONLY. Development D-B4 N1/N2 and D-S N1/N2 disruption conditions fail. Final D-B4 N2 fails; D-S N1/N2 fail. A small reference p can coexist with a failed above-median/mean-degradation conjunction. Development N4 has5/10 eligible mice;Final3/6;both aggregate panels are unavailable. No drift-independent/persistent-state claim is rescued.

Available suite/bundle counts: Development35 complete999 suites=34,965 bundles and5 unavailable;Final21 complete999 suites=20,979 bundles and3 unavailable. These are shared replicate bundles,not independent animals or extra fits. Large saved RNG journals are not replayed in M7.

## Animal and laboratory heterogeneity

Every saved animal effect/LL numerator/actual denominator,lab mean,equal-lab mean,LOMO/LOLO vector and lab-block CI is copied in the JSON; Final distribution-table source is also hash-bound. The summaries below are copied,not recomputed.

|Cohort|Contrast|Median|IQR|SD|Equal-lab mean|
|---|---|---:|---|---:|---:|
|Development|B4-B1|0.08324565051996781|[0.06142446314728878, 0.15002671981509014]|0.08269072477270156|0.09500981392772744|
|Development|B4-B3|0.03639460416104086|[0.01435672695808756, 0.056659161903756916]|0.03902105249313305|0.04149529227811527|
|Development|B4-B2|0.010818799595939243|[0.007961193255939652, 0.03622868778993424]|0.04388361439368737|0.019451705456105233|
|Development|D-B4|-0.0011471558202988416|[-0.029096362589730168, 0.0037078330190024192]|0.03359251533102332|-0.014486643859240568|
|Development|C-B4|4.725349278562589e-05|[-0.00022999585915996806, 0.0006539163302646293]|0.0008320894674913346|5.406645445039235e-06|
|Development|D-S|-0.00013202359685418337|[-0.0014488878666101218, 0.00021467808525360435]|0.005994957750373264|-0.0011554536160871592|
|Final|B4-B1|0.06492807666789979|[0.050056839563451146, 0.08704534501175716]|0.0660187525705048|0.08070399800907131|
|Final|B4-B3|0.04428098856144826|[0.034040666045358006, 0.061491218866293766]|0.027386045772987033|0.047328323860319085|
|Final|B4-B2|0.0060015522381872575|[0.002773901596793466, 0.009091550870939711]|0.020354399942708927|0.007024192140212944|
|Final|D-B4|0.0016049015407685646|[-0.005395802039334498, 0.009608897648776]|0.009464136390754344|0.0021391596629944864|
|Final|C-B4|8.994379890441557e-05|[4.201812562917707e-05, 0.0002600359090606793]|0.0002724259948826849|7.963120362031576e-05|
|Final|D-S|-7.965064035633351e-05|[-0.0003165266159978577, 0.0007734301654490653]|0.004147138591573757|0.0024899289428856088|

## Numerical/historical ledger and interpretation guardrails

Historical359 attempts =358 completed numerical PASS on rounded inputs +1 interrupted STARTED;251 original planned attempts never started. This source/implementation STOP is immutable and its coefficients are not reused. Separately authorized exact-native R1:610main+525sensitivity=1135newPASS;historical-inclusive1494. Final C:72main+320sensitivity=392PASS;historical-inclusive1886. Exactly one D assessment addedzero fits. No retrospective claim that separately authorized recovery erased historical ceilings/failures. All old starts and unavailable records remain.

Original numerical bounds/float64/architecture/grid/seeds and L-BFGS-B settings remain fixed. Actual endpoint PG<=0.001 and independent AD/every fixed FD<=1e-5;synthetic AD code validation<=1e-8. All FD steps1e-4/1e-5/1e-6 are required. Saved policy and source paths are in the JSON; M7 does not rerun these scientific checks.

- Every Development result remains exploratory; every available Final comparison remains DESCRIPTIVE ONLY.
- Original20 animals:12Development/8Final;10Development8labs and6Final4labs admitted;four exclusions are retained and never replaced.
- No independent-laboratory replication; equal-lab and lab-block summaries are dependence diagnostics.
- Mouse is the unit of inference; actual scored nominal curated-release unit-bin denominators; no pooled unit/trial inference.
- Final primary CI width0.09166131577698394 exceeds frozen0.01 precision gate; n6 fails n8 positive-claim floor; symmetry/independence unestablished.
- Development primary N1 gate failed7/10<8/10; N2passed10/10. Final primary N1/N2passed6/6; this cannot override the descriptive verdict.
- All five secondary Holm5 tests are nonsignificant in both cohorts. Final raw minimum two-sided p2/64 and Holm5 minimum0.15625 are discrete resolution facts,not power or equivalence.
- Development D-B4 mean is negative; Final descriptive mean is positive. No pooled/new contrast,mechanistic transition or superiority follows.
- All11 sensitivity cases/33panels per cohort are baseline-only. Development S02n9/S03n6;Final S02n6/S03n4. Final S03 aggregate unavailable; no D/C/S sensitivity robustness.
- N4 aggregate unavailable in both cohorts:5Development/3Final mice below6; corresponding drift-independent/persistent-state restrictions retained.
- N3 formal statistic is B4LL/Q wheel reliance diagnostic copied across contrast slots; separate B4-B1 gain descriptive. No independent D/C wheel null or all-movement independence.
- Finite references are destructive diagnostics,not assumption-free exact mechanistic/causal/population nulls. False disruption conjunctions remain false despite a small reference p.
- No causal connectivity/motor-command mechanism,biological discrete-state finding,CWP/NAP proof,human/BCI validation,independent-lab replication or all-movement independence.
- C model name versus Final calibration partition C and D model name versus assessment partition D must be disambiguated in every text/legend.
- Source restrictions include curated provider whole-session labels,known selected-probe saturation masks,strict-past native precision,observational wheel confounding,and contact/atlas proxies; no histological-depth claim.
- No new scientific analysis,selection,model evaluation,fit,hypothesis test or second Final D assessment is permitted in M7.

## Source map

The JSON source_hashes map provides every exact path/SHA used. Core saved result paths:

- paper15_r1/results/E_STATISTICS.json; E_SENSITIVITY_SUMMARY.json; E_CONTROL_SUMMARY.json; DEVELOPMENT_STATUS.json; CLAIM_TO_EVIDENCE_AUDIT.json.
- paper15_final1/results/D_STATISTICS.json; D_SENSITIVITY_SUMMARY.json; D_CONTROL_SUMMARY.json; D_SCIENTIFIC_VERDICTS.json; FINAL_DELIVERY.json; FINAL_CLAIM_TO_EVIDENCE_AUDIT.json.
- Frozen M1 cohort/protocol/policy and original R1 B selection;both source/QC cohort tables;both metadata-only reference freezes;original saved result CSVs and reports.

No old package or new paper15_manuscript file was changed by the reviewer. Later manuscript/figure/PDF consistency remains a separate requested review against this oracle.
