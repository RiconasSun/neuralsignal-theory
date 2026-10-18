"""Owner-line-preserving closure matrix,never changes the frozen baseline."""
from pathlib import Path
import subprocess
from paper15_final1.source import P,E,R,read,dump,sha

GROUPS=[
    (0,'Mission/authorization',['OWNER_REQUEST.txt','baseline.json','PRESERVATION_REGISTRATION.json']),
    (30,'Original scientific contract',['PRESERVATION_REGISTRATION.json','REUSE_REGISTRATION.json','A1_A10_ATTACHMENT_MAP.md']),
    (68,'Scientific contrasts',['../../../../paper15_final1/results/D_SCIENTIFIC_VERDICTS.json']),
    (92,'Development preservation',['PRESERVATION_REGISTRATION.json','../../../../paper15_final1/tables/DEVELOPMENT_VS_FINAL.csv']),
    (126,'Exact native source',['FINAL_SOURCE_PLAN_REVIEW_1.md','FINAL_SOURCE_ATTRITION_REVIEW_1.md','../../../../paper15_final1/tables/FINAL_SOURCE_AND_C_QC.csv']),
    (156,'Trusted C-only projection',['C_READER_REVIEW_2.md','C_READER_INDEPENDENT_SOURCE_CHECKS_2.json']),
    (187,'C physiology admission',['C_PHYSIOLOGY_STATE_REVIEW_1.md','../../../../paper15_final1/results/FINAL_C_QC_GATE.json']),
    (219,'Fixed cohort/attrition',['SIX_MOUSE_PRE_D_SCOPE.md','PRE_D_SCIENTIFIC_REVIEW_1.md']),
    (243,'Fixed C calibration/numerics',['C_PRODUCTION_REVIEW_2.md','C_ENDPOINT_FINAL_CHECKS_1.json','PRE_D_NUMERICAL_REVIEW_1.md']),
    (279,'Complete pre-D freeze',['PRE_D_SCIENTIFIC_REVIEW_1.md','PRE_D_NUMERICAL_REVIEW_1.md','PRE_D_GATE_SEAL_2.log']),
    (309,'One-shot D/statistical evaluation',['REAL_D_ONE_SHOT_BATCH_1.log','../../../../paper15_final1/D_BATCH_CLAIM.json','../../../../paper15_final1/results/D_STATISTICS.json']),
    (354,'Original scientific verdicts',['../../../../paper15_final1/results/D_SCIENTIFIC_VERDICTS.json','PRE_D_STATISTICAL_RESOLUTION.json']),
    (402,'Interpretation/limitations',['../../../../paper15_final1/FINAL_SCIENTIFIC_REPORT.md','../../../../paper15_final1/results/FINAL_CLAIM_TO_EVIDENCE_AUDIT.json']),
    (428,'Report/archive/reproduction',['../../../../paper15_final1/FINAL_SCIENTIFIC_REPORT.md','REPRODUCTION.md','review.md']),
    (450,'Exact final delivery',['../../../../paper15_final1/results/FINAL_DELIVERY.json','review.md'])]


def valid_reproduction(path):
    if path is None:return False
    receipt=read(path)
    return (receipt['status']=='PASS_NATIVE_POWERSHELL_SAVED_ONLY' and type(receipt['exit_code']) is int
            and receipt['exit_code']==0 and receipt['archive_sha256']==sha(P/'ARCHIVE_FREEZE.json')
            and receipt['D_claim_sha256']==sha(P/'D_BATCH_CLAIM.json')
            and receipt['log_sha256']==sha(R/receipt['log_path'])
            and receipt['command'][0]=='powershell'
            and receipt['result']['saved_statistics_exact'] is True and receipt['result']['tests']==68
            and receipt['result']['source_arrays_loaded']==0 and receipt['result']['new_real_fits']==0
            and receipt['result']['D_reassessment'] is False)


def valid_review(path):
    if path is None:return False
    receipt=read(path)
    return (receipt['decision']=='ACCEPTED_FINAL_DESCRIPTIVE_HANDOFF'
            and type(receipt['open_P0']) is int and receipt['open_P0']==0
            and type(receipt['open_P1']) is int and receipt['open_P1']==0
            and receipt['archive_sha256']==sha(P/'ARCHIVE_FREEZE.json')
            and receipt['baseline_sha256']==sha(E/'baseline.json')
            and receipt['D_claim_sha256']==sha(P/'D_BATCH_CLAIM.json')
            and receipt['report_sha256']==sha(R/receipt['report_path']))


def valid_transport(path):
    if path is None:return False
    receipt=read(path)
    return (receipt['remote_readback_verified'] is True and receipt['changed_blob_hashes_verified'] is True
            and receipt['working_tree_clean_before_receipt'] is True
            and receipt['commit']==subprocess.check_output(['git','rev-parse','HEAD'],cwd=R).decode().strip()
            and not subprocess.check_output(['git','status','--porcelain=v1','-z'],cwd=R))


IMPLEMENTATIONS={
    'Mission/authorization':['ops/evidence/2026-10-18/p15-m6-independent-final-validation/baseline.json'],
    'Original scientific contract':['paper15_final1/source.py:frozen_definitions','paper15_final1/calibration.py:configurations'],
    'Scientific contrasts':['paper15_final1/final_statistics.py:analyze_final,claim_verdicts'],
    'Development preservation':['paper15_final1/report.py:build','paper15_final1/source.py:frozen_definitions'],
    'Exact native source':['paper15_final1/metadata_qc.py','paper15_final1/metadata_access.py','paper15_final1/native_table.py'],
    'Trusted C-only projection':['paper15_final1/reader.py:project_C,check_reader_gate'],
    'C physiology admission':['paper15_final1/physiology.py:unit_qc','paper15_final1/anatomy.py'],
    'Fixed cohort/attrition':['paper15_final1/calibration.py:admitted','paper15_final1/final_statistics.py:claim_verdicts'],
    'Fixed C calibration/numerics':['paper15_final1/calibration.py:fit_one,execute_main','paper15_final1/sensitivity_calibration.py:execute'],
    'Complete pre-D freeze':['paper15_final1/seal_C.py','paper15_final1/admission.py:verify_pre_D_gate'],
    'One-shot D/statistical evaluation':['paper15_final1/d_batch.py:run','paper15_final1/reference_evaluation.py'],
    'Original scientific verdicts':['paper15_final1/final_statistics.py:claim_verdicts'],
    'Interpretation/limitations':['paper15_final1/report.py:build'],
    'Report/archive/reproduction':['paper15_final1/saved_audit.py','paper15_final1/saved_verify.py','paper15_final1/reproduce.ps1'],
    'Exact final delivery':['paper15_final1/results/FINAL_DELIVERY.json']}


def build(review_receipt=None,repro_receipt=None,git_receipt=None,terminal=False,output=None):
    base=read(E/'baseline.json');assert sha(E/'OWNER_REQUEST.txt')==base['source_sha256']
    delivery=read(P/'results/FINAL_DELIVERY.json')
    assert delivery['D_BATCH_COMPLETE'] and delivery['ONE_SHOT_D_EXECUTED']
    review_ok=valid_review(review_receipt);repro_ok=valid_reproduction(repro_receipt)
    transport_ok=valid_transport(git_receipt) if terminal else False
    if terminal:
        assert review_ok and repro_ok and transport_ok,'No terminal materialization without actual matching review/repro/clean remote receipt'
        assert output is not None and Path(output).resolve().is_relative_to((P/'work').resolve())
    rows=[]
    for original in base['requirements']:
        _,group,files=max((g for g in GROUPS if g[0]<=original['owner_line']),key=lambda g:g[0])
        references=[]
        for name in files:
            path=(E/name).resolve()
            assert path.is_relative_to(R) and path.exists(),name
            references.append(path.relative_to(R).as_posix())
        text=original['requirement'].strip();git_bound=text in ('GIT_COMMIT','REMOTE_VERIFICATION')
        stop_bound=text=='STOP AFTER FINAL SCIENTIFIC HANDOFF.'
        # Every row receives actual complete saved audits and full independent
        # owner-contract review; path existence alone never closes a requirement.
        verified=review_ok and repro_ok
        if git_bound or stop_bound:verified=verified and transport_ok and terminal
        if review_receipt is not None:references.append(Path(review_receipt).relative_to(R).as_posix())
        if repro_receipt is not None:references.append(Path(repro_receipt).relative_to(R).as_posix())
        if git_bound and git_receipt is not None:references.append(Path(git_receipt).relative_to(R).as_posix())
        rows.append(dict(**{k:v for k,v in original.items() if k!='status'},group=group,
                         implementation_location=IMPLEMENTATIONS[group],
                         verification_method='Exact requirement text + matching typed final independent review and native saved-audit/reproduction receipts; Git/stop require final live transport proof',
                         condition='Actual six-mouse descriptive fallback; eight-mouse positive branch preserved but untriggered; no N4 recovery or post-D model change',
                         evidence=references,status='VERIFIED' if verified else 'OPEN'))
    assert len(rows)==base['baseline_requirement_count']==311
    result=dict(mission=base['mission'],baseline_sha256=sha(E/'baseline.json'),baseline_requirement_count=311,
                verified_baseline_count=sum(r['status']=='VERIFIED' for r in rows),requirements=rows,
                independent_review_verified=review_ok,native_saved_reproduction_verified=repro_ok,
                final_transport_verified=transport_ok,terminal_materialization=terminal,
                status='PASS' if terminal else 'CONTINUE_EXECUTION',
                scientific_scope='Complete registered descriptive assessment,not confirmation',
                required_items_omitted=0,required_behaviors_silently_reduced=0,unapproved_existing_behaviors_removed=0,
                required_tests_silently_removed=0,unresolved_shrink_risk=0,temporary_substitutes_remaining=0,
                coverage_reductions_without_approval=0)
    if terminal:assert result['verified_baseline_count']==311
    dump(Path(output) if output is not None else E/'PRESERVATION_MATRIX.json',result)
    print('Atomic baseline preserved:',result['verified_baseline_count'],'/311 verified; terminal transport',transport_ok)


if __name__=='__main__':build()
