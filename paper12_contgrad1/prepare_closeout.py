"""Prepare auditable closure docs; no model or derivative execution."""
import re
import study as r

EVIDENCE=r.ROOT/'ops/evidence/2026-10-13/p12-m4-continuous-gradient-diag-1'

def text(p,value):
    with p.open('x',encoding='utf-8') as f:f.write(value)

def main():
    daily=r.ROOT/'ops/daily-operations.md';original=daily.read_bytes()
    if r.sha(daily)!=r.load(r.HERE/'prior_manifest.json')['sha256']['ops/daily-operations.md']:raise RuntimeError('BASE_DAILY_CHANGED')
    (r.HERE/'original_daily_operations.md').write_bytes(original)
    prefix=(f'# Current mission: P12-M4-CONTINUOUS-GRADIENT-DIAG-1\n\nStage A closeout PASS, independently reviewed and remote verified origin/test BASE {r.BASE}. Stage B numerical diagnosis complete: FINITE_DIFFERENCE_INSTABILITY. Original checker FAIL (2.067630627e-4 > 1e-5), optimizer FAIL (PG 0.692604771 > 0.001, maxiter2000) preserved. One real Training-A fit, 8064 coordinate rows, independent AD validated at initial/intermediate/endpoint. No new source repair or optimizer amendment. Original controller receipt serialization error retained; original native exit/cleanup UNPUBLISHED. Fresh independent native saved-only certificate PASS with zero new fits/derivatives. Engineering closure requires final review, saved reproduction, scoped origin/test push/readback/clean gate. STOP after diagnosis; no automatic scientific continuation. Evidence: paper12_contgrad1/NUMERICAL_AUDIT.md and ops/evidence/2026-10-13/p12-m4-continuous-gradient-diag-1. All historical bytes follow unchanged.\n\n---\n').encode()
    daily.write_bytes(prefix+original)
    evidence=[
        'stage_a_gate.json; Stage A closeout review and exact remote readback',
        'registration.json; baseline_registered.md; protocol.json; execution_registration.json',
        'prior_manifest.json; preservation_audit.json; original_daily_operations.md',
        'execution_registration.json A hashes; primary and certificate native/role_proof.json',
        'native/reproduction.json target and all_exact',
        'protocol.json options; unchanged model source bindings; reproduction endpoint',
        'execution_registration.json; reproduction data/context/offset hashes and layout',
        'independent_ad.py; native/*_audit.json; test_diagnostics.py ridge/normalization',
        'execution_registration.json original and cached oracle SHA; replay exact checks',
        'native/reproduction.json original checker + PG + histories exact',
        'protocol.json; gradient_scan.csv all seven scales',
        'gradient_scan.csv fourth_order and raw probes; native/*_audit.json',
        'gradient_scan.csv richardson, roundoff and stability; audit_statistics.py',
        'independent_ad.py; native/*_audit.json; synthetic regression tests',
        'test_diagnostics.py dimensions1/2/4 and one-bin oracle; native/synthetic_tests.json',
        'gradient_scan.csv absolute/scaled errors, all8064 rows',
        'native/initial_audit.json and initial CSV rows/vector hash',
        'native/intermediate_audit.json; reproduction intermediate_index1000',
        'native/endpoint_audit.json; exact history reproduction and recovered vector hash',
        'block_summary.json; CSV block mapping and four audited blocks',
        'NUMERICAL_AUDIT.md; frozen_sources/frozen_offset.py; independent_ad.py fixed offset',
        'CSV likelihood_AD + ridge_AD; block_summary.json; zero ridge discrepancy',
        'native/*_audit.json PG/AD_PG; CSV probe bounds; synthetic projection tests',
        'native/*_audit.json exposure7200/mantissa52; independent objective equality',
        'CSV theta digests repeated across scales; independent objective equality',
        'native/decision.json analytical_gradient_validated; AD error maxima',
        'native/decision.json and full step/order scan, no original-gate substitution',
        'native/reproduction.json; independent endpoint AD_PG; original PG gate false',
        'native/decision.json FINITE_DIFFERENCE_INSTABILITY; saved reconstruction',
        'NUMERICAL_AUDIT.md separate bounded future proposal only',
        'NUMERICAL_AUDIT.md; CSV; block_summary.json; figures/',
        '13 independent synthetic +6 saved integrity regressions; preserved failed attempts',
        'reproduce.ps1; actual replay receipt (created after sealing)',
        'review_final.md final independent review (required before closure)',
        'external final Git closure receipt: exact path/blob hashes, origin/test SHA and clean tree',
        'scope_audit.json; no downstream execution; STOP after verified diagnosis'
    ]
    old=(EVIDENCE/'goldenstandards.md').read_text(encoding='utf-8')
    requirements=re.findall(r'^\| (REQ-\d{3}) \| (.*?) \| (.*?) \|$',old,re.M)
    if len(requirements)!=36:raise RuntimeError('EXACT_ORIGINAL_36_DEFINITIONS_REQUIRED')
    items=[{'id':rid,'original_requirement':req,'original_verification':oracle,'evidence':ev,'status':'PENDING_FINAL_REVIEW' if rid=='REQ-034' else 'PENDING_REMOTE_CLOSURE' if rid=='REQ-035' else 'VERIFIED'} for (rid,req,oracle),ev in zip(requirements,evidence)]
    r.save(EVIDENCE/'acceptance_candidate.json',{'mission':'P12-M4-CONTINUOUS-GRADIENT-DIAG-1','base':r.BASE,'original_requirement_count':36,'definitions_identical_to_original':True,'verified_before_final_review_and_git':34,'items':items,'final_review_and_git_closure_updates_are_append_only':True})
    lines=['# Original 36-item acceptance plan execution','',f'BASE {r.BASE}. Original definitions below are verbatim, individually retained. Final independent review and actual remote closure are the last gates; neither is preclaimed. Saved numerical certification does not clear scientific FAIL.','', '| ID | Original requirement | Verification/evidence | Candidate status |','|---|---|---|---|']
    lines += [f"| {z['id']} | {z['original_requirement']} | {z['evidence']} | {z['status']} |" for z in items]
    text(EVIDENCE/'acceptance_candidate.md','\n'.join(lines)+'\n')
    r.save(r.HERE/'scope_audit.json',{'mission':'P12-M4-CONTINUOUS-GRADIENT-DIAG-1','real_fits':1,'real_configuration_count':1,'AD_audit_vectors':3,'FD_coordinate_rows':8064,'independent_forward_evaluations':48384,'M3_refits':0,'offset_refits':0,'full_cohort_M4':False,'M5':False,'nulls':False,'M6':False,'development_validation_scores':False,'final_holdout_evaluation':False,'mathematical_source_repair':False,'optimizer_amendment':False,'thresholds_unchanged':True,'stop_after_diagnosis':True})
    text(EVIDENCE/'claim_audit.md','''# Claim audit

Supported: exact single-target scalar and history reproduction; identical frozen inputs/model/objective/options; independently validated analytical derivatives at three audited vectors and synthetic oracles; complete predefined FD/order scan; fixed-step finite-difference instability; independently measured failing endpoint PG; original FAIL preservation; fresh saved-only native certification distinct from numerical execution.

Unsupported and prohibited: global mathematical correctness theorem; all optimizer-call gradients independently validated; original endpoint theta was historically preserved; recovered original native exit/cleanup values; original gradient/PG gate now passes; universally optimal FD step; extra precision on Windows; scientifically recovered M4; regime selection; generalization, cohort, null or final claims.

Engineering bugs resolved: pre-numerical decision stability predicate and optimizer attribution (review_admission1); serialization arity and append-only regression (native_attempt1.log); saved-test temp scope (saved_recovery_regressions.log); frozen saved-payload binding (review_recovery1). Every unsuccessful attempt remains archived. No mathematical or optimizer change was made. Final engineering bug_count=0/warn_count=0 is contingent on clean final review and remote closure. Historical scientific FAILs are not recounted as resolved product bugs.

Scientific limitations: one configuration, three vectors, finite precision, no original saved theta, unpublished original native exit/cleanup, no corrected-gradient refit, no empirical conditioning intervention. Each limitation is explicit in the numerical audit. A separate native certificate has fresh exit/cleanup and zero additional numerical experiments; it cannot infer missing historical metadata.
''')
    text(EVIDENCE/'candidate_verdict.md',f'''# Final numerical candidate — review and closure pending

Mission P12-M4-CONTINUOUS-GRADIENT-DIAG-1. Mode REVIEW_MODE. BASE {r.BASE}.

D4 FINITE_DIFFERENCE_INSTABILITY. Original gradient/PG gate FAIL remains. Analytical AD maximum7.259443046692127e-12; endpoint independent PG0.6926047710553235. Complete8064 rows, one frozen real fit. The fresh native saved-certificate exit0/cleanup0 and rolePASS certify saved evidence only; original controller exit1 and original native metadata UNPUBLISHED retained.

Baseline36,34 verified before final review/Git. REQ034 final independent review and REQ035 exact scoped normal origin/test push/readback/clean gate remain pending. No required item omitted/narrowed, no source repair/optimizer amendment, no unapproved behavior removal or test deletion, no temporary mathematical substitute. Old original three draft files remain immutable. Final acceptance and terminal PASS require both pending gates.

Test oracle:13 independent synthetic mathematical/instability cases plus6 saved corruption/append-only checks, complete probe arithmetic/coverage/decision reconstruction and sealed hashes. Actual final saved reproduction receipt is retained separately after sealing. Figure visual inspection completed. No UI/channel product requirement applies to this scientific diagnostic.

Carryover: no mathematical repair justified. Separately authorized bounded conditioning/optimizer study recommended; no next mission started. STOP after diagnosis and closure. Final review and remote closure provide append-only updates; this candidate record stays historical.
''')
    print('CLOSEOUT_DOCUMENTS_PREPARED_36_ORIGINAL_DEFINITIONS')

if __name__=='__main__':main()
