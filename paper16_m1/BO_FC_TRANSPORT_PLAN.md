# BO-targeted heldout transport

Preserve all 55 candidates: Development has five BO and 23 FC mice; Final has 27 BO mice. The frozen roster retains mouse, session, probe, sex, genotype and historical exposure. Both pilots and all historical Allen/P12 overlaps remain Development. There is no replacement, reroll or pooling across probes, sessions, mice or other visual areas.

This is a protocol-distribution shift within one Allen source. It is neither an IID split within one protocol nor independent-laboratory replication. The target is heldout BO animals fitted from new C states under the Development-selected model and ridge policy.

B selects from ridge .01/.1/1 using B1's unpenalized predictive logscore: average equally across mice within BO and FC, then weight the two protocol means .5/.5. Ties within1e−12 select the larger ridge. Keep the winning B1 state. No B4 gain, E outcome or Final score chooses weights or ridge.

S03 registers a BO-only E sensitivity on the five original BO Development mice, requiring at least three admissions. Report it beside FC E, requiring at least ten. Report all seven model levels, six gains, exposure, rates/QC, source composition and descriptive intervals; show B1 B-score curves without selecting an alternate BO-only policy. Bootstrap10000 whole mice using BO seed16043 and FC seed16044, with numeric mouse order. With so few BO animals, this is a descriptive diagnostic, not a new subgroup significance claim or causal protocol effect.

Future Development requires at least fourteen admissions, including three BO and ten FC. Final main coverage requires twelve. Six to eleven allows a separately authorized descriptive fallback retaining the failed main coverage gate and no positive category; fewer than six stops before D. These are coverage/planning floors, not demonstrated power. Report acquisition batch, sex, genotype, anatomy/probe composition and dependence assumptions; do not count units or trials as additional animals.
