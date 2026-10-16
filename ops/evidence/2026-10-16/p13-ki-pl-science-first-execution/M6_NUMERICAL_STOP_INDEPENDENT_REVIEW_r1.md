# Independent M6 numerical-stop review r1

Mission: `P13-KI-PL-SCIENCE-FIRST-EXECUTION`.
Reviewed UTC: 2026-10-16T17:11:55Z.
Reviewer: separate local reviewer agent; independent internal scientific/evidence/code review, not external peer review.
Decision: **SCIENTIFIC STOP REQUIRED — M6 CONDITIONAL CONTROL NUMERICAL FAILURE**.
Open review P0: **0**. Open review P1: **0** for the observed fail-closed execution/evidence inspected here. The **required scientific/numerical gate is FAIL**, not PASS. A failed registered experiment is not by itself evidence of a coding defect.

This accepts the applicability of the scientific stop and truthful preservation/reporting path. It does not certify completed M6, final eligibility, a valid final assessment, manuscript/PDF completion, full mission PASS or future Git closure. Stop all final C/D execution and further substantive scientific experiments in this mission. Preserve unexecuted drafts as unexecuted; no D engineering review or execution is granted here.

## Frozen execution and direct failure evidence

Independently verified the approved `M6_E_IMPLEMENTATION_FREEZE_r2.json` SHA256 **c55f5dc3f04371bf367af6910c7d0a671f72048a5b5817434b9ad1bb48478e91**, all **2,316** frozen file hashes, accepted stage approval and the actual review hash it binds. The reviewed control implementation is unchanged. Read the actual gate, full progress journal, native traceback/exit receipt, original stop/control definitions and exact owner/baseline amendments.

`paper13_ki_execution1/results/M6_E_CONTROLS_GATE.json` records **FAIL**, suite **conditional_Bstar**, zero-based replicate **0**, mouse **156130**, `FloatingPointError: overflow encountered in exp`, with retry/new random draw unauthorized. Native receipt records exit **1** at 2026-10-16T17:09:38.3053465Z. Traceback locates the error at `control_core.py:45`, `means=np.exp(eta)`, inside `conditional_counts`, called by `replicate`, before the failed mouse's predictive scoring can return.

The journal has one execution start and one final execution-error event, with no execution-complete event or later attempt. No trace/gate evidence of clipping, replacement draw, seed switch, fitted-model rescue or restart was found. Existing exclusive journal creation prevents an implicit repeated experiment. No new control, RNG draw, fit or source read was performed by the reviewer.

## Independent completed/attempted accounting

Loaded the four saved score arrays only for shape/dtype/finite-mask/receipt accounting, without recomputing controls or scoring any neural data. Each array is **999x10x9 float64**, preserving nine score labels. All completion tuples are unique and occur in frozen replicate/sorted-mouse order. Completed-suite file hashes match their durable SUITE_COMPLETE receipts.

| Suite | Completed mouse-replicates | Completed full ten-mouse replicates | Finite score cells | Uncompleted NaN score cells |
|---|---:|---:|---:|---:|
| temporal | 9,990 | 999 | 89,910 | 0 |
| history | 9,990 | 999 | 89,910 | 0 |
| task_order | 9,990 | 999 | 89,910 | 0 |
| conditional_Bstar | 3 | 0 | 27 | 89,883 |
| Total | **29,973** | **2,997 across three suites** | **269,757** | **89,883** |

Conditional replicate0 has complete scores only for **147465, 152417, 152419**. The next scheduled mouse **156130** failed. Its cell and all later cells remain NaN, correctly indicating no completed score; none is a zero or invented result. All conditional replicas1–998 are unexecuted.

Exact planned denominator is **39,960 mouse-replicates**. There are **29,974 attempted =29,973 completed +1 failed**, leaving **9,986 unattempted**. Journal event counts independently match: 2,998 REPLICATE_START, 2,997 REPLICATE_COMPLETE, 29,973 MOUSE_CONTROL_COMPLETE, three SUITE_COMPLETE and one CONTROL_EXECUTION_ERROR. There are **zero complete conditional ten-mouse replicates out of999**, not a small complete-sample conditional reference.

Saved array SHA256 identities:

- temporal: `0ec411b82c432f51768852d163b4803b80a9e5c1e68ddb4811b1a6e7007aa8de`
- history: `40b7519eb819ee68774a6a392919950babfbddc3168691c36145aae9649bcf7d`
- task_order: `fa6f40249865b920c53fe6d0ee00fcbf7ccae04bca8ba72c4201eb28ae02bf44`
- conditional_Bstar partial: `a6982696eec537df59646559521c865365fda479f437ea8f17a3352056814274`

These partial/complete artifacts should all be retained in the stop archive. They cannot be called four completed suites. In particular, do not compute the registered conditional p-values from three mice, ignore the failed mouse, change999/1000, replace NaNs or infer a passing full-reference guard. Descriptive summaries of the three already completed stress arrays may be labeled as such, but cannot rescue the failed mandatory stage or authorize final execution.

## Scientific STOP applies without a new purpose ambiguity

The original owner activation directs stop on substantive scientific/numerical failures (`USER_MISSION.txt:29`), requires registered prerequisites and no numerical rescue, and calls for a truthful scientific stop report if a prerequisite fails (:183). The prospective control implementation registration explicitly says invalid generated means/scores stop execution, with no clipping/cap/refit/new random draw. The frozen code implements that rule.

The direct owner B amendment exempts **only** the known six-versus-eight recent-event coverage failure from stopping an otherwise eligible descriptive final execution. It explicitly retains all other required physiological/implementation/numerical/source gates. Baseline amendment r3 likewise retains STOP for all other substantive failures. This new overflow therefore is **not** covered by that exception. The recent-event broad-claim INCONCLUSIVE lock remains independently binding; it does not license ignoring a second required numerical failure.

Consequently the current mission's next scientific step is a **truthful scientific stop report and preservation**, not C fitting or D exposure and not another owner-purpose question to evade the unchanged STOP. Final C approval/gate/execution directory are absent in the inspected saved state. No final C fit or D outcome is evidenced. The absence of final evaluation is a respected boundary, not evidence of a negative final biological result. The valid earlier M1-M5/QC/930-fit results remain their actual historical completed scope; the failed generative control does not retroactively turn all those training fits into numerical failures.

Changing the null model, clipping generated counts/means, stabilizing history feedback, lowering requirements, skipping the failed control, choosing another seed/draw or promoting three stress suites to complete M6 would change the registered experiment. There is no demonstrated ordinary coding defect here that would authorize such a recovery under the current mission. Any future scientific redesign/recovery requires its own explicit prospective protocol/authorization; it must not be hidden inside this stop archive.

## Root-cause wording must remain bounded

Established observation: **floating-point exponential overflow during the frozen conditional-B* autoregressive Poisson simulation**, with B*=B2 for this mouse. The generator uses frozen coefficients/scalers, original nuisance and previously generated counts, with no count/mean clipping; Poisson counts and the exponential link do not supply a global hard bound on simulated means. Thus wording such as **“overflow in the uncapped autoregressive conditional simulation”** is supportable if “uncapped” describes the implementation/support, not a proven dynamical diagnosis.

The saved failure does **not** record the failing within-epoch bin/unit, generated prefix, eta values or local feedback trajectory. No new diagnostic simulation is performed here. Therefore the evidence does **not** establish a specific positive-feedback coefficient mechanism, a general instability theorem, inevitable stochastic explosion, numerical impossibility for all draws, biological runaway activity, or the invalidity of every fitted predictor. “Runaway self-excitation caused it” may at most be an untested hypothesis, not a demonstrated root cause. “Exponential overflow” is the observed failure location; a deeper instability mechanism remains unproven. Report that limitation rather than reconstructing a favorable explanation by new draws.

## Review scope and next administrative work

No P0/P1 implementation/retention violation requiring a repair before truthful stop reporting was identified in the inspected frozen path and saved artifacts. The required M6 numerical failure remains a scientific failure even with review bug_count0; synthetic engineering acceptance cannot convert it into a scientific PASS. The registered reference analysis is unavailable/incomplete, with no final claims or final validation.

Complete the saved-only failure audit, current stage/requirement matrix, honest stop report/limitations and independent archive-closure review; preserve every complete/partial outcome, immutable failure and original owner amendment. Archive/Git administrative work may proceed only through its actual later reviewed scoped closure. This review does not certify that closure or a full original study/manuscript has completed.

No network/raw source/neural count bundle/new real control/draw/model fit/final C/D outcome was accessed. Only saved E-control scores/metadata/receipts were inspected; no model outcome was recomputed. Only this new review file is written. Earlier reviews remain unchanged. No external peer review, full mission/scientific PASS or prospective commit/push/readback/clean-tree status is granted.
