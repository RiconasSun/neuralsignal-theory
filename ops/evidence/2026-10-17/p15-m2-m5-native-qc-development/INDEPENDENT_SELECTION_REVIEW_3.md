# Independent internal selection review 3: S05 behavioral reference

Mission: P15-M2-M5-NATIVE-QC-AND-DEVELOPMENT. Review date: 2026-10-18 UTC.

Decision: **ACCEPTED_NARROW_SELECTION_COMPONENT_UPDATE**. Open P0: 0. Open P1: 0. Prior reviews remain preserved. This accepts the current selector component conditionally on the actual completed A-attempt gate, without asserting that it has yet passed or that B/E has been accessed.

The extraction call now passes `stimuli-.5` to nuisance construction instead of the variable neural epoch start. Frozen S05 shortens only neural warm-up/history to .25s; behavioral warm-up remains unchanged. The new call therefore preserves the 37 scored nuisance columns' original behavioral displacement/previous-completed-trial reference under S05. For primary warmup=.5, the old neural epoch and the new expression are identical. Registered main B selection, causal feature definitions, bins, models and fit policies are unchanged.

Fresh reviewer execution: all9 selection tests and `SensitivityTests.test_S05_neural_reset_shortens_but_scored_nuisance_references_unchanged` PASS with ResourceWarning as error. The S05 fixture compares all37 scored columns, shows exact equality with the primary nuisance references, and confirms using the shorter neural epoch would differ. Only this one sensitivity regression was reviewed here; other sensitivity integration is outside scope.

Exact SHA256 identities:

- selection.py: `f7b36f12875138dd395740a4ea1412d8bfb837ae9e67b94bc0f82b061421c7ad`
- test_selection.py (unchanged): `278fec67b8d055ea71b40d615dfbb6839c354397e4e3fab299dd720ed20ee9ab`
- test_sensitivities.py (specific S05 test reviewed): `bcc83d996cafab5bfa696ae93f82abf05851b070bc721e70cc0d2de839f9a24c`

The accepted r2 candidate/global-selection/access behavior is otherwise unchanged. Freeze the updated selector identity before B production use. This review does not issue an E gate, certify the complete sensitivity/control/statistics pipeline, change running A-fit source identities, or approve Final access.

No real data, effects, B/E neural arrays, raw cache, network/source request or fit was read or run. Only this new review artifact was added.
