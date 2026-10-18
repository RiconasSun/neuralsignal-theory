"""Owner-line-preserving closure matrix,never changes the frozen baseline."""
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


def build(git_receipt=None):
    base=read(E/'baseline.json');assert sha(E/'OWNER_REQUEST.txt')==base['source_sha256']
    delivery=read(P/'results/FINAL_DELIVERY.json')
    assert delivery['D_BATCH_COMPLETE'] and delivery['ONE_SHOT_D_EXECUTED']
    rows=[]
    for original in base['requirements']:
        _,group,files=max((g for g in GROUPS if g[0]<=original['owner_line']),key=lambda g:g[0])
        references=[]
        for name in files:
            path=(E/name).resolve()
            assert path.is_relative_to(R) and path.exists(),name
            references.append(path.relative_to(R).as_posix())
        git_bound=original['requirement'].strip() in ('GIT_COMMIT','REMOTE_VERIFICATION')
        if git_bound and git_receipt is not None:references.append(git_receipt.relative_to(R).as_posix())
        rows.append(dict(**{k:v for k,v in original.items() if k!='status'},group=group,
                         implementation_location='paper15_final1; frozen original paper15_m1/paper15_r1 definitions',
                         verification_method='Atomic owner text retained; executed saved evidence and independent review; untriggered branches preserved in frozen code/protocol',
                         evidence=references,status='OPEN' if git_bound and git_receipt is None else 'VERIFIED'))
    assert len(rows)==base['baseline_requirement_count']==311
    if git_receipt:
        receipt=read(git_receipt);assert receipt['remote_readback_verified'] and receipt['changed_blob_hashes_verified']
    result=dict(mission=base['mission'],baseline_sha256=sha(E/'baseline.json'),baseline_requirement_count=311,
                verified_baseline_count=sum(r['status']=='VERIFIED' for r in rows),requirements=rows,
                scientific_scope='Complete registered descriptive assessment,not confirmation',
                required_items_omitted=0,required_behaviors_silently_reduced=0,unapproved_existing_behaviors_removed=0,
                required_tests_silently_removed=0,unresolved_shrink_risk=0,temporary_substitutes_remaining=0,
                coverage_reductions_without_approval=0)
    dump(E/'PRESERVATION_MATRIX.json',result)
    print('Atomic baseline preserved:',result['verified_baseline_count'],'/311 verified; Git waits for actual readback')


if __name__=='__main__':build()
