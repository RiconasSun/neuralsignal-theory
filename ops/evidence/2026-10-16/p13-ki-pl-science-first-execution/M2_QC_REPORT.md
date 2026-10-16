# Actual M2 A/C physiological QC result

M2 PASS under the unchanged gate:10eligible development mice and9eligible final mice, each with8selected curated-release PL units. These are now actual operational QC admissions, not merely metadata candidates. The full original25animal disposition is retained in the preceding frozen source package; no replacement or reallocation occurred.

Native one-scan exit0.211unit attempts:152pass and59fail. All are preserved in individual per-mouse JSON and durable per-unit journals. First8passing numeric PLIDs selected; remaining candidates unexamined, not labeled good/bad. Unassignable nonfinite timestamps would have stopped source extraction; none did. Unit QC uses only60A/Cepochs/180s, original spike/ISI/occupancy/rate/refractory/finite/order rules. No B/E/D count, rate, QC, scaling or score was exported or used. Permitted trusted decoder transiently read full-record selected-unit timestamp arrays to clip windows; this is explicitly not a claim that no D raw timestamp was decoded.

133bounded source requests,19pinned assets,129153663transport bytes,0recorded transport errors (exact receipt total verified below). Opaque raw byte caches are not scientific excluded-outcome summaries. Complete savedA/Cstate bundles total916097bytes; states and outputs are hash-bound in M2_STATE_MANIFEST.json. No model fit or neural score is represented by this gate.

| Mouse | Role | QC partition | Units attempted | Selected numeric unit IDs |
|---|---|---|---:|---|
| 147465 | development | A | 11 | 51, 53, 54, 55, 56, 58, 60, 61 |
| 152417 | development | A | 8 | 383, 384, 385, 386, 387, 388, 389, 390 |
| 152419 | development | A | 11 | 148, 149, 150, 153, 154, 155, 156, 158 |
| 156130 | development | A | 10 | 191, 193, 194, 195, 196, 198, 199, 201 |
| 156131 | development | A | 8 | 154, 155, 156, 157, 158, 159, 160, 161 |
| 216300 | development | A | 11 | 240, 242, 243, 244, 245, 247, 248, 250 |
| 216301 | development | A | 10 | 132, 134, 135, 136, 137, 138, 139, 140 |
| 258416 | development | A | 11 | 74, 76, 78, 79, 80, 81, 82, 84 |
| 268951 | development | A | 11 | 91, 92, 93, 94, 95, 96, 97, 101 |
| 273858 | development | A | 10 | 148, 149, 150, 151, 152, 153, 156, 157 |
| 128514 | final | C | 13 | 410, 411, 413, 414, 415, 418, 420, 422 |
| 128516 | final | C | 12 | 239, 241, 242, 243, 245, 246, 248, 250 |
| 152414 | final | C | 10 | 264, 266, 268, 269, 270, 271, 272, 273 |
| 225757 | final | C | 17 | 204, 205, 208, 211, 212, 215, 217, 218 |
| 225758 | final | C | 12 | 179, 181, 182, 183, 184, 185, 186, 189 |
| 225759 | final | C | 10 | 239, 240, 241, 243, 244, 245, 246, 247 |
| 258414 | final | C | 9 | 12, 14, 15, 16, 17, 18, 19, 20 |
| 268947 | final | C | 16 | 195, 201, 203, 206, 207, 208, 209, 210 |
| 273855 | final | C | 11 | 130, 131, 135, 136, 137, 138, 139, 140 |

Failed gate counts (a unit may fail multiple conditions): `{"minimum_ISIs": 49, "minimum_occupied_epochs": 31, "minimum_spikes": 49, "rate": 21, "refractory_fraction": 15}`. Selected laminar labels: `{"PL2/3": 8, "PL5": 42, "PL6a": 94, "PL6b": 8}`.

Limitations remain: full-record provider sorting/curation, unknown original quality-column formulas, curated units rather than certified single neurons, aversive-task pre-tone target without measured awake/movement independence, and one probe per animal from one lab. Training-only operational QC cannot remove these limitations.

Independent post-M2 saved-evidence review is pending in M2_M3_A_review_r1.md. This result does not validate M3-M7 or release D outcome analysis.
