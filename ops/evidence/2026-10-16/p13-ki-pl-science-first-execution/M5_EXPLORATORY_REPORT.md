# M5 exploratory development results

Ten original development mice; E=30epochs/mouse, 6,000 nominal curated-release unit-bins/mouse. Eight frozen predictor roles; Bstar aliases B2. No E QC, scaler fitting, model selection, refit or final validation.

| Contrast | Equal-mouse mean nats/unit-bin | 95% mouse percentile CI | Exact conditional sign p | Holm3 p | Positive mice |
|---|---:|---|---:|---:|---:|
| D_minus_B4 | 0.0135268458 | [0.00587035403, 0.024250325] | 0.001953125 | 0.005859375 | 10/10 |
| C_minus_B4 | 0.000690374378 | [-0.000206359505, 0.00153800561] | 0.17578125 | 0.17578125 | 7/10 |
| D_minus_C | 0.0128364714 | [0.0049188008, 0.0240103431] | 0.00390625 | 0.0078125 | 9/10 |
| D_minus_Bstar | 0.0186712401 | [-0.0286640646, 0.0900528048] | 0.853515625 | 1 | 5/10 |
| C_minus_Bstar | 0.00583476869 | [-0.0355225469, 0.066725865] | 0.978515625 | 1 | 3/10 |
| D_minus_S | 0.00287914554 | [-0.00102894389, 0.00720316111] | 0.236328125 | 0.708984375 | 8/10 |

Primary and guard Holm families are separate groups of three. Sign p-values are exact only under independent conditional fair-sign / suitable sign symmetry assumptions; model labels were not randomized. Bootstrap intervals assume representative independent mouse sampling and regularity, not distribution-free guarantees. E is exploratory because A/B from the same mice informed fitting/selection.

D−B4 and D−C meet their exploratory statistical components. C−B4 does not. Neither D−Bstar nor C−Bstar meets its guard, so a beyond-strong-baselines superiority claim is withheld. D−S also fails its guard; there is no validated temporal-dynamics advantage over a static joint mixture. Required controls/sensitivities and final C/D stages remain unexecuted; these are not complete scientific acceptance results.

| Mouse | B0 | B1 | B2=Bstar | B3 | B4 | D | C | S |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 147465 | -0.673704608 | -0.673902829 | -0.638540477 | -0.656758546 | -0.645964959 | -0.630355986 | -0.644092291 | -0.630992148 |
| 152417 | -0.829848578 | -0.82343251 | -0.780789391 | -0.830304343 | -0.806364915 | -0.797726154 | -0.804657877 | -0.79495805 |
| 152419 | -0.964837226 | -0.948847584 | -0.860395025 | -0.900157376 | -0.840271548 | -0.816121782 | -0.841765454 | -0.807549255 |
| 156130 | -0.465995817 | -0.466712435 | -0.411515361 | -0.46456547 | -0.460302868 | -0.458794341 | -0.459845594 | -0.460310114 |
| 156131 | -0.884353764 | -0.881052358 | -0.814273935 | -0.875053411 | -0.819299036 | -0.807510209 | -0.817022502 | -0.809716744 |
| 216300 | -0.620328832 | -0.622738094 | -0.590815046 | -0.614614513 | -0.618881242 | -0.615832859 | -0.618076934 | -0.61887809 |
| 216301 | -0.683444107 | -0.682229634 | -0.654633037 | -0.673195155 | -0.653667399 | -0.652812132 | -0.652311531 | -0.653666281 |
| 258416 | -1.06210192 | -1.0723682 | -1.03501819 | -1.06498653 | -1.12192189 | -1.11145607 | -1.1195937 | -1.12161273 |
| 268951 | -0.909233883 | -0.930873335 | -1.22803689 | -0.886818135 | -0.97882595 | -0.924725958 | -0.979816053 | -0.942102498 |
| 273858 | -0.553487991 | -0.533542539 | -0.511263722 | -0.562608927 | -0.528337323 | -0.523233186 | -0.529751451 | -0.527574217 |

All scores are predictive log likelihood divided by actual nominal curated-release unit-bins; negative log-score values are not probabilities or causal mechanisms. Models reset per epoch and retain all zero bins. Full exact values, bootstrap draws, bin scores, model identities, original thresholds, numerical trajectories and failed internal reviews are retained.

The fixed study concerns provider-labeled PL activity in aversive-task pre-tone epochs, not confirmed awake-only, choice mechanisms, independent laboratory replication, physical neural atoms or NAP/CWP proof. Operational QC and whole-record provider sorting do not certify isolated neurons. Movement/arousal and carry-over stimuli remain unmeasured limitations.
