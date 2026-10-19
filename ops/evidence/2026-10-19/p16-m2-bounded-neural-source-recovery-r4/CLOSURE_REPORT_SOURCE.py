"""Saved-derived current-mission trace; no acquisition/model code."""
from pathlib import Path
import json,hashlib,datetime
R=Path.cwd();P=R/'paper16_source_r4';E=R/'ops/evidence/2026-10-19/p16-m2-bounded-neural-source-recovery-r4'
def load(p):return json.loads(p.read_text(encoding='utf8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):
 with p.open('x',encoding='utf8',newline='\n') as f:json.dump(v,f,indent=2,allow_nan=False);f.write('\n')
def text(p,v):
 with p.open('x',encoding='utf8',newline='\n') as f:f.write(v)
a=load(P/'SOURCE_AND_PHYSIOLOGY_ACCOUNT.json');s=load(E/'SAVED_VERIFICATION_RESULT.json');f=load(P/'TERMINAL_FIELDS.json');b=load(E/'REQUIREMENT_BASELINE.json')
assert a['verdict']=='M2_SOURCE_AND_PHYSIOLOGY_PASS' and s['total_complete_sources']==28 and a['candidate_states_retained']==1983
assert f['FINAL_STATUS']=='CONTINUE_EXECUTION' and f['BUG_COUNT']==f['WARN_COUNT']==0
prefix=E.relative_to(R).as_posix()+'/'
pending={109,111,112,115,120};conditional=set(range(38,46))|{62,86,88,89}
items=[]
for row in b['items']:
 n=int(row['id'].split('-')[1]);status='PENDING_ARCHIVE' if n in pending else 'VERIFIED'
 if n<=13:
  refs=['paper16_source_r4/ACCESS_REGISTRATION.json','paper16_source_r4/R3_REUSE_MANIFEST.json',prefix+'BOOTSTRAP.json',prefix+'PREACCESS_REVIEW.md'];observation='Exact BASE,55 identities,28Dev5BO23FC/27Final allocation and original scientific/source hashes checked before access; all frozen preaccess payloads remain unchanged.'
 elif n<=24:
  refs=['paper16_source_r4/R3_REUSE_MANIFEST.json','paper16_source_r4/results/RECOVERED_RANGE.json',prefix+'FOURTH_SOURCE_REVIEW.md','paper16_source_r4/SOURCE_AND_PHYSIOLOGY_ACCOUNT.json'];observation='R3 history remains3complete/1failedpartial/24unattempted and228savedA;3sources reused without live opening;19fourth states retained,54new; exact507904suffix+540672prefix at original logical offset.'
 elif n<=55:
  refs=['paper16_source_r4/RECOVERY_POLICY.md','paper16_source_r4/transport.py','paper16_source_r4/RESOURCE_LEDGER.json','paper16_source_r4/results/TRANSPORT.jsonl',prefix+'SYNTHETIC_HOST_FINAL.log'];observation=f"Actual R4 {s['R4_source_requests']}HTTP/{s['R4_new_payload_bytes']}payloadbytes/{s['R4_transport_retries']}retries/{s['R4_timeout_recovery_slots']}slots; fixed caps/identity/range guards and one original48hstage; synthetic header/partial/timeout/cap rejection cases do not represent real failed requests."
 elif n<=64:
  refs=[prefix+'FOURTH_SOURCE_APPROVAL.json',prefix+'FOURTH_SOURCE_REVIEW.md','paper16_source_r4/results/WORKER_remaining.json','paper16_source_r4/results/SUPERVISION_remaining.json','paper16_source_r4/results/BUDGET_FOURTH.jsonl'];observation='Complete fourth-source independent acceptance preceded remaining24; exact original order, same deadline,28complete source dispositions; reviewed fourth ledger preserved as current append-only prefix.'
 elif n<=79:
  refs=['paper16_source_r4/core.py','paper16_source_r4/neural_reader.py','paper16_source_r4/A_ONLY_STATE_MANIFEST.json','paper16_source_r4/SOURCE_AND_PHYSIOLOGY_ACCOUNT.json',prefix+'FULL_SAVED_REPLAY.log'];observation='Independent saved replay checks all1983 native A states with original QC function/thresholds, exact original candidate order, valid-zero/invalid separation, within-presentation ISIs and numeric-lowest-eight/common support; only A exports, no B/E outcome scaling, no Final access.'
 elif n<=94:
  refs=['paper16_source_r4/results/M2_DECISION.json','paper16_source_r4/SOURCE_AND_PHYSIOLOGY_ACCOUNT.json','paper16_source_r4/A_ONLY_STATE_MANIFEST.json','paper16_source_r4/M3_M5_HANDOFF.md',prefix+'COHORT_BOUNDARY_REGRESSIONS_2.log'];observation=f"28/28complete;{s['admitted_complete_sources']}admitted({s['admitted_BO']}BO/{s['admitted_FC']}FC), original14/3/10floors. Every physiological exclusion retained; no pooling/replacement; all inputs frozen,0models/scalers. Synthetic failing-floor/missing28th/source-error branches deny invalid PASS without publishing a decision."
 elif n<=106:
  refs=[prefix+'SYNTHETIC_HOST_FINAL.log',prefix+'PREACCESS_REVIEW.md',prefix+'COHORT_BOUNDARY_REGRESSIONS_2.log','paper16_source_r4/R3_REUSE_MANIFEST.json'];observation='37 unique source/transport/reader/resume/controller/integration cases passed on the native host; independently reviewed synthetic fault/role/zero/preservation cases and actual R3 hash/QC preservation. Seven additional cohort boundary tests strengthen original gates; none replaces actual source evidence.'
 elif n==107:
  refs=[prefix+'PREACCESS_APPROVAL.json',prefix+'PREACCESS_REVIEW.md','paper16_source_r4/PREACCESS_FREEZE_MANIFEST.json'];observation='Accepted independent preaccess report bound36identities/0P0/0P1 before first actualHEAD or neuralGET.'
 elif n==108:
  refs=[prefix+'FOURTH_SOURCE_APPROVAL.json',prefix+'FOURTH_SOURCE_REVIEW.md'];observation='Accepted complete-fourth-source independent report bound271identities/0P0/0P1 before any remaining source.'
 elif n in pending:
  refs=['paper16_source_r4/TERMINAL_FIELDS.json','paper16_source_r4/archive_handoff.py'];observation='Not complete at precommit freeze. Resolve only in actual postcommit FINAL_HANDOFF_RECEIPT after accepted final review, exact normal commit/push, all remote blob readbacks and clean tree; no interim full mission PASS.'
 elif n==110:
  refs=[prefix+'FULL_SAVED_REPLAY.log','paper16_source_r4/reproduce.ps1','paper16_source_r4/verify_saved.py'];observation='Actual nativePowerShell saved-only full28/1983A/QC/ledger/recovery replayPASS with network denied; raw private inputs required. Postfreeze replay additionally verifies every final-manifest private/public payload.'
 elif n in [113,114]:
  refs=['paper16_source_r4/results/M2_DECISION.json','paper16_source_r4/A1_A10_CLAIM_AUDIT.md','paper16_source_r4/SOURCE_ONLY_LIMITATIONS.md'];observation='Exactly M2_SOURCE_AND_PHYSIOLOGY_PASS; source/physiology only. No predictive, numerical model, null or Final scientific validation claim.'
 elif n in [116,117,118]:
  refs=['paper16_source_r4/TERMINAL_FIELDS.json','paper16_source_r4/results/WORKER_remaining.json','paper16_source_r4/neural_reader.py'];observation='Actual0model/scalerfits,0B/E neural scientific access,0FinalC/D; allowlisted source trace and unchanged frozen implementation, not a model-result inference.'
 elif n==119:
  refs=['paper16_source_r4/R3_REUSE_MANIFEST.json',prefix+'SYNTHETIC_HOST_1.log',prefix+'PRE_FIX_TEST_INTEGRATION.py',prefix+'CLI_COMPATIBILITY.log',prefix+'CLOSURE_STATUS_REGISTRATION.json'];observation='All old source/stopped/failed/review bytes and new unsuccessful fixture/CLI attempts preserved; status-only helper amendment preserves prior accepted helper/tests/reviews by exact independent SHA, no scientific changes.'
 else:raise AssertionError(row)
 kind='CONDITIONAL_ENFORCEMENT_PLUS_SYNTHETIC_AND_ACTUAL_LEDGER' if n in conditional else 'PENDING_FRESH_ARCHIVE_PROOF' if n in pending else 'ACTUAL_SAVED_SOURCE_QC_OR_FROZEN_IMPLEMENTATION_AND_SPEC_REGRESSION'
 items.append({'id':row['id'],'section':row['section'],'requirement':row['requirement'],'status':status,'verification_method':kind,'observed':observation,'evidence_paths':refs})
assert len(items)==120 and sum(x['status']=='VERIFIED' for x in items)==115
refs=sorted({name for row in items for name in row['evidence_paths']});digests={name:sha(R/name) for name in refs}
write(E/'REQUIREMENT_RESULTS.json',{'mission':f['MISSION_ID'],'baseline_sha256':sha(E/'REQUIREMENT_BASELINE.json'),'baseline_requirement_count':120,'verified_baseline_count':115,'pending_archive_count':5,'pending_ids':['REQ-'+str(n).zfill(3) for n in sorted(pending)],'not_a_terminal_mission_PASS':True,'items':items,'evidence_hashes':digests,'postcommit_resolution':'paper16_source_r4/work/FINAL_HANDOFF_RECEIPT.json; only the5 pending archive rows may then resolve, no scientific threshold/requirement changed'})
text(E/'verdict.md',f'''# R4 precommit verdict and closure boundary

Mission: {f['MISSION_ID']}. Exact BASE d60e913c528feecfaaab9397ba1a6157c511526d.

Scientific source verdict: **M2_SOURCE_AND_PHYSIOLOGY_PASS**. Actual28/28complete sources, {s['admitted_complete_sources']}admitted ({s['admitted_BO']}BO/{s['admitted_FC']}FC),1983retainedA states, original14/3/10floors unchanged. This is not predictive/model scientific validation.

Internal execution state at this freeze: **CONTINUE_EXECUTION**, pending final independent review and verified archive. A full mission PASS is not asserted before those checks. The postcommit FINAL_HANDOFF_RECEIPT supplies the actual final PASS/NEED_ENV state, exact SHA, all changed-file identities, clean gate and120-item trace.

bug_count=0; warn_count=0; unresolved_shrink_risk=0. baseline_requirement_count=120; verified_at_precommit_freeze=115; pending_archive=5 (109,111,112,115,120). No pending item is credited as verified yet. required_items_omitted=0; required_behaviors_silently_reduced=0; unapproved_existing_behaviors_removed=0; required_tests_silently_removed=0; temporary_substitutes_remaining=0; coverage_reductions_without_approval=0. Original baseline remains byte-exact; results are separate. No original tracked source/data/evidence is deleted or narrowed; the only old tracked edit is an additive daily prefix retaining the original exact suffix.

Verification:37native source/transport/reader/controller/integration synthetic tests +8archive +7cohort-boundary tests =52unique, all applicable source saved QC and original-history hashes independently verified. Tests do not replace actual source evidence. Original source code/acceptance payloads remain unchanged; status-only archive reporting amendment was prospective and independently rereviewed. All earlier failed/rejected/interrupted evidence remains.

Source-only test level: focused unit/fault tests, native Windows Job/clock integration, exact actual HTTP/source/A-QC receipts and native saved-only replay. UI, browser and real-channel checks are not applicable because no UI/channel product behavior is in this source-only owner baseline; no required case is waived. Full-cohort predictive fitting and unrelated repository suites are outside authorization. No screenshots or synthetic scores are substituted for source/model evidence.

Source physiological exclusion(s) are recorded, not bugs or missing-source attrition. Known curated-support/source-use/anatomical/behavioral limitations remain in SOURCE_ONLY_LIMITATIONS and A1-A10. Zero models/scalers fitted; no B/E neural scientific assessment; no FinalC/D. M3_READY is source readiness only; separately authorized implementation/numerical gates and fitting are still required.

Next closure operations only: independently accept the frozen full-M2/ledgers/saved-state package; exact-file stage; compare every index blob; normal origin/test commit/push; remote SHA/changed-file readback and clean proof. No feature/source/science work in closure. Stop after actual verified handoff.
''')
text(E/'daily-review.md',f'''# Source-only daily review

R4 full source/QC result:28complete,{s['admitted_complete_sources']}admitted,{s['admitted_BO']}BO/{s['admitted_FC']}FC. Original R3 STOP and all history preserved; all complete physiological exclusions are retained in the exact account, never replaced.0fits/B-Escience/FinalC/D. Source M2_PASS is separate from numerical/predictive science. Final independent review and archive remain pending at this snapshot; no next mission starts. See REQUIREMENT_RESULTS for115verified/5pending of120, and the postcommit receipt for actual final closure.
''')
q=R/'ops/daily-operations.md';old=q.read_bytes();prefix_text=f"# P16 R4 source-only handoff candidate: M2_SOURCE_AND_PHYSIOLOGY_PASS;28complete/{s['admitted_complete_sources']}admitted({s['admitted_BO']}BO/{s['admitted_FC']}FC). Final independent review/archive pending;0models/B-Escience/Final. STOP after verified handoff; no auto M3. Evidence: paper16_source_r4/CURRENT_HANDOFF.md.\n\n"
q.write_bytes(prefix_text.encode('utf8')+old)
write(E/'FINAL_TEST_SCOPE.json',{'unique_tests':52,'frozen_source_tests':37,'archive_tests_final':8,'cohort_tests':7,'source_preaccess35_payloads_unchanged':True,'source_test_log':'SYNTHETIC_HOST_FINAL.log','archive_test_log':'ARCHIVE_STATUS_REGRESSIONS_2.log','cohort_test_log':'COHORT_BOUNDARY_REGRESSIONS_2.log','independent_auxiliary_reviews':['AUXILIARY_REVIEW_1.md','AUXILIARY_REVIEW_2.md'],'old41_and48_scope_receipts_are_historical_not_current_denominators':True,'no_real_source_retry_or_new_model_trial_from_synthetic_tests':True})
print('120-item trace:115verified/5explicitly pending archive; source-only verdict and daily snapshot published.')
