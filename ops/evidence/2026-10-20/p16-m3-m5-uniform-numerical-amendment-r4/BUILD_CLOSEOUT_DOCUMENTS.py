"""Build additive closeout documents from saved metadata, never scientific calls."""
import json
from pathlib import Path
R=Path(__file__).resolve().parents[4]
P=R/'paper16_development_r4'
E=Path(__file__).resolve().parent
def read(p):return json.loads(p.read_bytes())
def write(p,obj):
    with p.open('x',encoding='utf8',newline='\n') as f:
        json.dump(obj,f,indent=2,ensure_ascii=False,allow_nan=False);f.write('\n')
def text(p,s):
    with p.open('x',encoding='utf8',newline='\n') as f:f.write(s)
baseline=read(E/'REQUIREMENT_BASELINE.json')
facts=read(P/'EXECUTION_FACTS.json')
assert facts['new_optimizer_attempts']==3041 and facts['new_numerical_passes']==3040
assert facts['incomplete_attempted_tasks']==1 and facts['unattempted_tasks']==2478
groups=[
 (range(1,16),['BOOTSTRAP.json','CLOSURE_BRANCH_PREFLIGHT.json','OWNER_REQUEST.txt'], 'Base/mission identity and conditional execution boundaries; terminal scientific completion is not claimed.'),
 (range(16,39),['INHERITED_R3_REPRODUCTION.log','INHERITED_FEASIBILITY_REPRODUCTION.log','INDEPENDENT_REUSE_CHECK_RESULT.json'], 'Historical source pins, saved-only inherited checks, immutable failures and exact historical denominators.'),
 (range(39,58),['PREFIT_REVIEW_1.md','PREFIT_APPROVAL.json'], 'Prospective uniform policy and unchanged scientific definitions bound by the production freeze.'),
 (range(58,101),['INDEPENDENT_REUSE_CHECK_RESULT.json','REUSE_REVIEW_1.md','REUSE_ADMISSION_APPROVAL.json'], 'Every 952 optimizer and 216 B0 state audited; historical ftol provenance retained; actual 5519 task derivation and exclusions reviewed before fitting.'),
 (range(101,114),['M3_CERTIFICATION_1_RESULT.json','FOCUSED_FINAL_GATES_2.log','PREFIT_REVIEW_1.md','PREFIT_APPROVAL.json'], 'Production numerical/causal/role/budget tests and independent prefit acceptance preceded new A-only fits.'),
 (range(114,129),['INDEPENDENT_INTERRUPTION_EVIDENCE.json','INDEPENDENT_COMPLETED_NUMERICAL_SUMMARY.json','EXTERNAL_INTERRUPTION_REVIEW_1.md'], 'One original stage; unchanged policy; actual 3040 completed states and one incomplete prefix preserved. No retry/reset/extension. Native final exit/time unavailable, not reconstructed.'),
 (range(129,137),['INDEPENDENT_INTERRUPTION_EVIDENCE.json','INDEPENDENT_PARTIAL_IDENTITY.json'], 'Frozen Development identities/access and exact attempt journals; no E/Final exports and no recorded numerical failure.'),
 (range(137,150),['INDEPENDENT_INTERRUPTION_EVIDENCE.json'], 'Complete M4 was not reached; no complete selection manifest or independent complete-M4 acceptance exists.'),
 (range(150,171),['INDEPENDENT_INTERRUPTION_EVIDENCE.json'], 'M4 prerequisite enforced: no E entitlement, export, scores, comparisons, sensitivity scoring or controls. Unavailable is not a negative effect.'),
 (range(171,188),['INDEPENDENT_INTERRUPTION_EVIDENCE.json','INHERITED_R3_REPRODUCTION.log'], 'Historical failures/attempts/reviews retained; no prohibited scientific claims or retrospective clearance.'),
 (range(188,209),['OWNER_REQUEST.txt','EXTERNAL_INTERRUPTION_REVIEW_1.md'], 'Additive mission archive and explicit publication boundary; exact new payload requires separate owner approval.'),
 (range(209,255),['OWNER_INTERRUPTION_CAUSE.json','INDEPENDENT_COMPLETED_NUMERICAL_SUMMARY.json'], 'Actual closeout values and unavailability reported without scientific PASS, unavailable effects or invented native receipts.'),
]
open_ids={9,114,116,148,149,196,199,*range(137,147),*range(152,166)}
pending={202:'Actual native saved-only reproduction must finish successfully.',203:'Actual independent final scientific/archive review pending.',204:'Actual local commit and transport receipts pending; exact publication approval required.',241:'Self-containing commit SHA belongs in the ignored post-commit receipt, not guessed here.',243:'Post-commit clean gate belongs in ignored PUBLICATION_LOCAL receipt.'}
human={207:'Exact public payload authorization has not been granted.',242:'New payload remote verification unavailable until exact owner publication approval; BASE only verified.'}
rows=[]
for item in baseline['items']:
    n=int(item['id'].split('-')[1]); evidence=[]; reason=''
    for numbers,paths,note in groups:
        if n in numbers:evidence=[(E/p).relative_to(R).as_posix() for p in paths];reason=note;break
    evidence+=['paper16_development_r4/SCIENTIFIC_CLOSEOUT.md','paper16_development_r4/EXECUTION_FACTS.json']
    status='VERIFIED'
    if n in open_ids:status='OPEN';reason='Required scientific output is incomplete/unavailable after external interruption; retained as unmet, not waived. '+reason
    if n in pending:status='OPEN';reason=pending[n]
    if n in human:status='BLOCKED_HUMAN_INPUT';reason=human[n]
    if n in {236,237,240}:status='IMPLEMENTED_UNVERIFIED';reason='Actual independent final review and defect counts pending; not pre-signed.'
    rows.append({**item,'status':status,'verification_method':'Saved-artifact, strict journal, identity and independent review cross-check; no new scientific calculation', 'evidence':evidence,'outcome_explanation':reason})
assert len(rows)==254 and len({r['id'] for r in rows})==254
write(E/'REQUIREMENT_OUTCOMES.json',{'mission':baseline['mission'],'baseline_requirement_count':254,'traceable_count':254,'baseline_unchanged':True,'all_scientific_requirements_verified':False,'items':rows})
text(E/'REQUIREMENT_OUTCOMES.md','# Frozen requirement outcomes\n\nAll 254 original owner statements remain individually traceable. This is a traceability denominator, not 254 independent tests or 254 scientific passes. The original baseline is unchanged. Complete M4/E outputs remain OPEN; scientific stop compliance does not replace them. Post-commit identities are recorded separately without self-reference.\n\n'+''.join(f"- {r['id']} — {r['status']}: {r['outcome_explanation']}\n" for r in rows))
result={
 'MISSION_ID':baseline['mission'],'BASE_SHA':'3a7fb87c879410155595ae6a640730c290e080a9','FINAL_STATUS':'WAIT_FOR_HUMAN_INPUT',
 'SCIENTIFIC_VERDICT':'STOP_EXECUTION_INTERRUPTED_REQUIRED_GATE','NUMERICAL_AMENDMENT_REGISTERED':True,'FTOL':0.0,
 'ORIGINAL_PG_AD_FD_GATES_PRESERVED':True,'OLD_952_STATES_AUDITED':952,'OLD_952_STATES_ADMITTED':952,'OLD_216_B0_STATES_ADMITTED':216,
 'INDEPENDENT_REUSE_REVIEW':'ACCEPTED_HISTORICAL_STATE_ADMISSION_ONLY','GLOBAL_LAMBDA':1.0,'LAMBDA_ORIGIN':'HISTORICAL_R3_B1_SELECTION',
 'NEW_OPTIMIZER_TASKS_PLANNED':5519,'NEW_OPTIMIZER_ATTEMPTS':3041,'NEW_NUMERICAL_PASSES':3040,'NEW_NUMERICAL_FAILURES':0,
 'INCOMPLETE_ATTEMPTED_TASKS':1,'UNATTEMPTED_TASKS':2478,'M4_COMPLETE':False,'M4_INDEPENDENT_REVIEW':'NOT_REACHED',
 'E_EXECUTED':False,'E_B4_MINUS_B1':'UNAVAILABLE_NOT_EVALUATED','E_SECONDARY_EFFECTS':['UNAVAILABLE_NOT_EVALUATED']*5,
 'SENSITIVITIES_COMPLETED':'NO_E_SCORING_PARTIAL_A_FITS_RETAINED','CONTROLS_COMPLETED':False,'HISTORICAL_R3_STOP_PRESERVED':True,
 'BUG_COUNT':None,'WARN_COUNT':None,'FINAL_C_ACCESS':False,'FINAL_D_ACCESS':False,'INDEPENDENT_FINAL_REVIEW':'PENDING_ACTUAL_REVIEW',
 'GIT_COMMIT':'ACTUAL_SHA_IN_POSTCOMMIT_PUBLICATION_LOCAL_RECEIPT','REMOTE_VERIFICATION':'BASE_VERIFIED_NEW_PAYLOAD_NOT_PUSHED_OWNER_AUTH_PENDING',
 'WORKTREE_CLEAN':'ACTUAL_POSTCOMMIT_GATE_IN_PUBLICATION_LOCAL_RECEIPT','M6_REQUEST_READINESS':False,
 'STOP_REASON':'OWNER_REPORTED_COMPUTER_SHUTDOWN_NATIVE_FINAL_RECEIPT_UNAVAILABLE_NO_RETRY',
 'NATIVE_RETURN_CODE':None,'EXACT_SHUTDOWN_TIME':None,'NATIVE_SAVED_REPRODUCTION':'RUNNING_NOT_YET_ACCEPTED',
 'FG_COMPLETED':facts['FG_completed'],'ACCEPTED_ITERATIONS':facts['accepted_iterations'],
 'DERIVATIVE_RESERVATIONS_ARE_NOT_COMPLETION_CERTIFICATES':True,
 'PUBLICATION_BLOCKED_REQUIREMENT':'R-207; OWNER_REQUEST section 9',
 'PROPOSED_DESTINATION':'https://github.com/RiconasSun/neuralsignal-theory.git refs/heads/test'}
write(P/'FINAL_REPORT.json',result)
text(P/'FINAL_REPORT.md','''# R4 interrupted Development closeout

Scientific verdict: **STOP_EXECUTION_INTERRUPTED_REQUIRED_GATE**. Archive closure awaits independent final review, actual saved-only PowerShell verification and exact public-payload authorization. It is not scientific PASS.

Base: `3a7fb87c879410155595ae6a640730c290e080a9`. The owner confirmed computer shutdown. Independent native checks found the original supervisor and Windows Job absent; exact shutdown time and native exit code remain unknown. No synthetic native terminal receipt was substituted.

All 952 historical optimizer states and 216 B0 analytic certificates were independently accepted for reuse before new fitting. Only the 952 optimizer states have historical `ftol=1e-12` provenance; the B0 certificates are analytic and have no optimizer ftol. The single-case feasibility endpoint and R3 failed endpoint were excluded. New attempts used the prospectively frozen uniform `ftol=0` policy, unchanged PG <=1e-5, AD <=1e-8 and fixed h=1e-5 FD error <=2e-5. Global lambda 1.0 is the previously consumed R3 B1 selection, not a new selection.

The 5,519 planned new tasks produced 3,041 actual attempts: 3,040 complete numerical passes, zero recorded numerical failures, one incomplete attempt and 2,478 unattempted tasks. The independent completed-endpoint audit found maximum PG 1.999980498137462e-6, maximum scaled AD error 5.329070518200751e-15 and maximum fixed-FD error 8.413669760898301e-11. The 3,040 complete endpoints used 707,125 FG pairs and 664,219 accepted iterations; the incomplete prefix adds 485 FG pairs and 465 accepted iterations. Total saved arithmetic is 707,610 completed FG pairs and 664,684 accepted iterations. Reserved derivative calls are reported separately and are not completion certificates. Optimizer success never replaces numerical checks.

The incomplete task `763236014:S02:S:None:11:GLOBAL` has 275 parameters, no completed endpoint/result and no numerical verdict. Original partial files are retained. No fit was restarted or retried; the one original 48-hour claim was not reset or extended.

Complete M4 and independent complete-M4 approval were not reached. E was never claimed, exported or evaluated. B4-B1, B4-B2, B4-B3, D-B4, C-B4 and D-S are all unavailable, as are E confidence intervals, full S01–S12 sensitivity scores and N1–N4 controls. Unavailable does not mean zero, nonsignificant, equivalent or biologically absent. Partial A panel fits do not complete sensitivity analyses.

No Final C/D access occurred. M6 is not ready. R1/R2/R3 stops, failed reviews, methodological exposure and prior attempts remain unchanged. This archive supports statements about numerical progress and truthful interruption only; it provides no new E evidence for neural-history predictive value, causal connectivity, physical primitives, CWP/NAP, independent laboratory replication or Final confirmation.

保存证据说明：952 个历史优化状态和 216 个 B0 状态全部通过独立复用审查；修订优化流程未完成剩余任务，M4 没有完成，E 没有产生任何神经历史预测结果。所有相关科学效果保持不可用，不能据此申请 Final M6。若未来继续，只能另行前瞻登记，对 2,479 个未解决任务制定独立有界合同；本次封存不授权继续。

The complete private inventory contains the original 33,574 files plus one append-only independent hash inventory. A public clone cannot reproduce private-array integrity without the original protected saved bundle and pinned runtime; no download/refit fallback exists. Saved-only regression and archive integrity are engineering evidence, not scientific completion.

The original requirement baseline has 254 statements. Their individual outcomes are retained in REQUIREMENT_OUTCOMES.json; missing scientific requirements stay OPEN. Failed tooling/review attempts remain preserved. Final code, review, public-manifest hashes and actual local commit/clean/readback identities are separately bound to avoid circular self-hashes.

The owner’s section 9 publication rule requires separate approval of the exact new payload. The previous 127-file authorization does not cover these new A-derived numerical logs/certificates. No new payload will be pushed before that approval. Protected neural arrays, private caches, keys and credentials are excluded. Destination, if approved: `https://github.com/RiconasSun/neuralsignal-theory.git`, branch `test`.
''')
text(E/'CLOSEOUT_GOLDENSTANDARDS.md','''# Additive interruption closure contract

Current mission remains P16-M3-M5-UNIFORM-NUMERICAL-AMENDMENT-R4. Original prospective goldenstandards.md, all 254 baseline statements, production freeze, source pins and scientific standards are immutable. This is the saved-only closure step, not a new scientific execution stage.

The closure registration preceded tooling changes. Owner-reported computer shutdown is distinct from unavailable native final exit/time. Preserve all original attempts, partial files and failed tooling/reviews. Never invent a native supervision result, rerun a model, evaluate a derivative/score, read new neural sources or access E/Final. Build truthful STOP evidence, verify every saved file/certificate, run native saved-only PowerShell, independently review the final archive, prepare an exact public manifest and local commit. Ask for section 9 exact-payload publication approval only after all safe local work is exhausted.

Verification oracle: 3041 attempts = 3040 complete passes + 1 incomplete; 5519 planned = 3041 attempts + 2478 unattempted. No complete M4, E or Final. First protected seal plus one supplement must exactly equal current saved work/results files; missing/extra/tampered bytes fail. Tests: saved-only original14/new9; independent inventory7; prior prefit production33 and affected focused10 are separately reported, never summed as unique cases. Original strict journal helpers remain unchanged. No real-channel/UI gate applies.

Preservation matrix: REQUIREMENT_OUTCOMES.json/.md maps every original statement. OPEN scientific items cannot be replaced by extra engineering checks. No scientific shrink or assertion weakening is permitted. Original daily-operations/current-handoff are source-pinned historical artifacts; FINAL_HANDOFF.md provides the additive current state. All new files stay in this mission namespace. Exact-file staging only; no main/force/PR/reset/clean. Scientific STOP is permanent in this archive; technical bug/warn counters await actual independent review. Terminal WAIT_FOR_HUMAN_INPUT is only for the exact publication authorization, not permission to resume science.
''')
text(P/'FINAL_HANDOFF.md','''# Current R4 handoff — external interruption

This additive handoff supersedes the operational status of the immutable prospective CURRENT_HANDOFF.md. The scientific worker is stopped after owner-confirmed shutdown. Do not restart it, reset its deadline, refit the incomplete task, complete M4, claim E, access Final C/D or start M6/P17.

Read FINAL_REPORT.json, SCIENTIFIC_CLOSEOUT.md, EXECUTION_FACTS.json, TASK_OUTCOMES.json and the exact independent final review. The only remaining external action is a separate owner decision on the exact reviewed public payload after local sealing/review/commit. The older 127-file approval is insufficient. Publication approval would authorize only transport of the reviewed commit; it would not authorize science.

One command for protected local saved-only verification:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\paper16_development_r4\REPRODUCE_SAVED.ps1
```

Requires original protected saved bundle and pinned runtime. No refit/network fallback. Actual self-containing commit SHA and clean/remote receipts reside in ignored mission evidence PUBLICATION_LOCAL/, outside scientific inventory and public payload.
''')
print('Created additive draft closeout documents; review/reproduction fields remain pending.')
