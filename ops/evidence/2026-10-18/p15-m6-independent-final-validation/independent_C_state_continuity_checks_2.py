"""Bind unchanged C evidence to revised production candidate; no fits or D."""
import json,datetime,ast,numpy as np
from paper15_final1.source import P,E,R,read,sha,source_rows
c=read(P/'C_PRODUCTION_CANDIDATE.json');old=read(E/'C_PHYSIOLOGY_STATE_INDEPENDENT_CHECKS_1.json')
changed={k for k,h in old['hashes'].items() if c['hashes'].get(k)!=h}
assert changed=={'calibration.py','sensitivity_calibration.py','test_calibration.py'}
for rel,h in c['hashes'].items():assert sha(P/rel)==h,rel
for mod,names in [('calibration.py',['admitted','configurations','c_export','wheel','prepare','register']),('sensitivity_calibration.py',['prepare','register'])]:
    oldpath=E/'source_snapshots'/('C_PRODUCTION_ATTEMPT1_'+mod);assert sha(oldpath)==old['hashes'][mod]
    def funcs(p):return {x.name:ast.dump(x,include_attributes=False) for x in ast.parse(p.read_text()).body if isinstance(x,ast.FunctionDef)}
    a,b=funcs(oldpath),funcs(P/mod)
    for n in names:assert a[n]==b[n],(mod,n)
gate=read(P/'results/FINAL_C_QC_GATE.json');plan=read(P/'C_FIT_PLAN.json');sens=read(P/'SENSITIVITY_FIT_PLAN.json')
prep=read(P/'results/C_SENSITIVITY_PREPARATION.json');lookup={r['subject']:r for r in gate['subjects']}
for row in source_rows():
    s=row['subject']
    if s=='NYU-21':assert not lookup[s]['C_neural_access'] and not lookup[s]['admitted'];continue
    qc=read(P/'results'/(s+'_C_QC.json'));state=read(P/'metadata'/(s+'_task.json'))
    assert qc['subject']==s and qc['role']=='C' and qc['admitted']==lookup[s]['admitted'] and qc['qualified_units']==lookup[s]['C_qualified_units']
    assert qc['C_epochs']==lookup[s]['C_epochs']==state['result']['structural_eligible_epochs']['C'] and qc['all_C_role_source_observations_retained'] is True
    assert len(qc['files'])==2
    for f in [f for f in row['files'] if f['role'] in ('times','clusters')]:
        r=next(x for x in qc['files'] if x['role']==f['role']);assert r['key']==f['key'] and r['bytes']==f['bytes'] and r['etag']==f['etag']
    with np.load(P/'work/C_exports'/(s+'.npz'),allow_pickle=False) as arrays:
        t,l=arrays['times'],arrays['labels'];support=state['result']['recording_sync_support'];tol=1/state['result']['fs']
        assert not len(t) or (t[0]>=support[0]-tol and t[-1]<=support[1]+tol)
        assert np.issubdtype(l.dtype,np.integer) and len(t)==len(l) and (not len(l) or 0<=l.min()<=l.max()<len(state['native_uuid_list']))
for row in prep['records']:
    path=P/'sensitivity_states'/row['subject']/(row['case']+'.json');state=read(path)
    assert row['state_sha256']==sha(path) and row['status']==state['status']
for item in sens['attempts']:
    path=P/'sensitivity_states'/item['subject']/(item['case']+'.json')
    assert item['state_sha256']==sha(path) and read(path)['status']=='C_PREPROCESSING_SEALED'
    assert item['seed']==11 and item['family'] in ('B0','B1','B2','B3','B4')
    assert item['ridge']==next(config['ridge'] for config in plan['configurations'] if config['family']==item['family'])
for s,h in plan['state_hashes'].items():assert sha(P/'states'/(s+'_C_PREPROCESSING.json'))==h
out=dict(mission='P15-M6-INDEPENDENT-FINAL-VALIDATION',time=datetime.datetime.now(datetime.timezone.utc).isoformat(),candidate_sha256=sha(P/'C_PRODUCTION_CANDIDATE.json'),hashes=c['hashes'],external_hashes=c['external_hashes'],original_independent_full_C_state_checks_sha256=sha(E/'C_PHYSIOLOGY_STATE_INDEPENDENT_CHECKS_1.json'),changed_files_since_initial_state_check=sorted(changed),C_preparation_and_registration_function_ASTs_unchanged=True,all_actual_state_source_QC_files_unchanged=True,C_only_support_and_label_checks_verified=True,eight_subject_QC_gate_identity_join_verified=True,all_actual_native_source_receipt_headers_match=True,all_66_case_manifest_identities_verified=True,all_320_future_plan_case_bindings_and_selected_ridges_verified=True,production_failure_policy_reviewed_here=False,C_fitting_approved=False,D_approved=False,original_whole_record_neural_bodies_read=False)
(E/'C_PHYSIOLOGY_STATE_INDEPENDENT_CHECKS_2.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
print('PASS: C support/labels/8 ledger identities/66 case joins/320 bindings; states/preparation ASTs unchanged; no fits/raw source')
