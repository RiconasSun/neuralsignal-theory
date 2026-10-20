# P16 prospective S07/N4 precision contract

MISSION: P16-S07-N4-PROSPECTIVE-PRECISION-CONTRACT-1
Registration BASE: `1870ec5f6ee0ca87afc87aae5f5bf89c5ee20431`.
Owner decisions: OWNER_DECISIONS.md. Machine definition: PRECISION_CONTRACT.json.

This is an additive future operator definition. The original M1 and the R1
STOP_IMPLEMENTATION_REQUIRED_GATE record remain unchanged, including their two
historical warnings. Registration does not retrospectively clear that gate or
provide present authority to implement, fit, select or score models.

For S07, rank only the original eight selected main units within each mouse by
their A-only rate on the main model's common-valid presentations and identical
observation mask in [100,220) ms. Rate is total scored-window spikes divided by
actual valid scored exposure seconds. Sort rate ascending, then numeric Unit ID
ascending; select zero-based positions 2,3,4,5. This selects a sensitivity subset
and never changes the original eight main units. No B/E/D outcome participates.
The corresponding future Final definition uses C only, subject to separate
authorization; the mention of C grants no access in this mission.

For N4, use the set (color_flip, time_rotation) in {0,1} × {0,1,2,3,4,5}, excluding
(0,0). On the original ±1 current-color coding, a flip changes c to −c for both
the 12 color×time PSTH assignments and the color*r raw interaction. A rotation
maps only the six PSTH time indices cyclically; it does not change actual source
time or any other nuisance. The canonical representation is k'=(k+s) mod 6.
Because every nonidentity cyclic shift is included, this representation does not
select a favorable subset or an alternative stress-test family.

Previous color, historical repetition counts, raw running r and all other
nuisances remain their original observed values. Keep fitted B1 coefficients,
the original training-only scaler/active-column map, targets and masks fixed.
Construct the specified wrong raw columns and use the same frozen preprocessing;
do not refit or recenter it, or negate a centered/scaled interaction in place of
changing the raw color*r value. The 11 fixed operators have no RNG or p-value and
remain deterministic nuisance stress tests under the original claim limitations.

No scientific or numerical threshold, model, ridge, seed, source, allocation or
historical failure is altered. No neural arrays or real features are loaded and
no scientific stage clock starts for this registration. Both previously missing
definitions are prospectively supplied; production implementation and independent
prefit certification remain absent and must be assessed in a separate mission.
