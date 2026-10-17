# Real-spike pilot feasibility report

Exactly two metadata-selected development sessions were accessed once for technical feasibility. Identities were frozen before file access; complete UUID/revision/size/ETag inventory was frozen before payload download. Every native file passed size and MD5/ETag verification. No final-reserved mouse entered the pilot, and neither model fitting nor predictive scoring occurred.

| Check | CSH_ZAD_026 / probe01 | NYU-30 / probe00 |
|---|---:|---:|
| Actual provider-reader spikes | 34,166,347 | 25,836,824 |
| Nonfinite / unordered timestamps | 0 / 0 | 0 / 0 |
| Native clusters / MOp labeled / good MOp | 1,306 / 696 / 84 | 616 / 120 / 22 |
| UUID and provider quality bridge to old table | equal | equal |
| Native anatomy differences overall | 0 | 102 |
| Good MOp cluster identity bridge | identical | identical |
| AP duration from header | 5,822.074833 s | 5,155.744500 s |
| Probe sample rate | 30,000 Hz | 30,000 Hz |
| Original sync points / extrapolated tail | 293 / 0 s | 259 / 0 s |
| Native structural trial windows | 1,103 | 784 |
| Known saturation intervals | 716 | 48 |
| Overlapping stimulus windows excluded | 163 | 23 |
| Retained native windows / exposure | 940 / 470 s | 761 / 380.5 s |
| Retained windows in original trial halves | 492 / 448 | 383 / 378 |
| Finite ordered wheel observations | 1,470,068 | 1,140,545 |
| Usable windows with wheel coverage | 940 | 761 |
| Ten-trial count demo / zero unit-bins | 8,400 / 7,500 | 2,200 / 1,745 |

The source clock is provider-synchronized session time. Recorded support is derived from the AP acquisition header and monotone probe sync, independently of observed spike extent. Known saturation sample boundaries are mapped to that clock. Native current task tables are used; no historical bwm/saturation mask is copied. The retrospective source movement-onset values differ from old aggregate values, so future M1 must use one pinned native policy. The two good MOp sets remain comparable, but laminar/non-MOp mappings are not assumed equal.

`PILOT_RESULTS.json`, `MAPPING_AUDIT.json`, per-mouse UNIT_MAP/ANATOMY_DIFFERENCES tables, FILE_RECEIPTS and COUNT_DEMO files contain coordinate-level identities and numeric evidence. The saved-only command recomputes the counts from small saved timestamp fragments and synthetic invalid-support canaries without rereading full neural caches. It does not claim independent full-array rescanning or a new provider execution.

This is **conventional curated-observation feasibility**, not all-mouse physiological admission, absolute packet completeness, artifact-free certification, model comparison or biological validation. See OBSERVATION_LIMITATIONS.md for the measurement contract and unknown other artifact burden. Both entire pilot mice remain development permanently. No more pilot sessions or fitting are authorized by M0.
