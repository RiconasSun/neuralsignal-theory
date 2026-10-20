"""Reviewed metadata compatibility receipts; no neural or model imports."""
from .identity import R,P,E,load,sha,check,ProvenanceStop,exact_record

def verify_phase_a():
    approval=load(E/'PHASE_A_APPROVAL.json')
    if approval.get('decision')!='ACCEPTED_R3_PHASE_A_METADATA_COMPATIBILITY' or approval.get('open_P0')!=0 or approval.get('open_P1')!=0:raise ProvenanceStop('Independent Phase A acceptance required')
    check(R/approval['review_path'],approval['review_sha256'])
    for row in approval['files']:check(R/row['path'],row['sha256'])
    result=load(P/'PHASE_A_RESULTS.json')
    if result['compatible_representations']!=27 or len(result['files'])!=27:raise ProvenanceStop('Complete actual metadata coverage required')
    return result

def compatibility(record):
    exact_record(record);result=verify_phase_a()
    rows=[r for r in result['files'] if r['session_id']==record['source']['session_id'] and r['mouse_id']==record['source']['mouse_id']]
    if len(rows)!=1:raise ProvenanceStop('Exact reviewed compatibility identity required')
    row=rows[0];check(R/row['path'],row['sha256']);state=load(R/row['path'])
    if state['source']!=record['source'] or state['original_admitted_common_mask']!=record['selection']['common_mask']:raise ProvenanceStop('Source or admitted mask changed')
    return state
