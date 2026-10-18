"""Fail-closed admission for the actual corrected scientific fit inputs."""
from .source import P,R,load_json
from .training import sha,configurations,admitted

def required_hashes(subjects):
    required={'source.py','native_table.py','cached_source.py','metadata_access.py','metadata_qc.py','reader.py','physiology.py',
        'models.py','features.py','independent_ad.py','training.py','production_admission.py','input_oracle.py','revalidate_inputs.py','verify_wheel_indices.py',
        'SOURCE_FILE_FREEZE.json','NEURAL_HEADER_FREEZE.json','A_FIT_PLAN.json','READER_GATE.json',
        'results/M2_PHYSIOLOGY_GATE.json','results/A_FEATURE_PREPARATION.json','results/FULL_A_SOURCE_REVALIDATION.json',
        'results/EXACT_WHEEL_INDEX_VERIFICATION.json','results/PRODUCTION_SYNTHETIC_CERTIFICATE.json',
        'results/A_PREPARATION_SOURCE_CONTINUITY.json','source_snapshots/training_A_preparation.py'}
    for subject in subjects:required|={f'metadata/{subject}_task.json',f'results/{subject}_A_QC.json',f'states/{subject}_A_PREPROCESSING.json'}
    return required

def verify(gate,plan):
    subjects=admitted()
    assert gate['mission']=='P15-DEV-EXACT-NATIVE-REPAIR-R1' and gate['PRODUCTION_NUMERICAL_PASS']
    assert required_hashes(subjects)<=set(gate['hashes'])
    assert plan['subjects']==subjects and plan['configurations']==configurations() and plan['per_mouse']==61
    assert plan['total_main']==61*len(subjects)<=732 and plan['max_retries']==0
    assert plan['solver']==dict(method='L-BFGS-B',maxiter=2000,maxfun=80000,maxls=40,ftol=1e-12,gtol=1e-6)
    assert plan['numerical']==dict(PG_max=.001,AD_max=1e-5,FD_steps=[1e-4,1e-5,1e-6],all_steps_required=True)
    assert plan['historical_started_attempts']==359 and plan['historical_coefficients_reused'] is False
    reviews=gate['independent_review_evidence'];assert set(reviews)=={'full_native_input','production'}
    for item in reviews.values():
        path=(R/item['path']).resolve();assert path.is_relative_to(R.resolve()) and sha(path)==item['sha256']
    full=load_json((P/'results/FULL_A_SOURCE_REVALIDATION.json').read_text());wheel=load_json((P/'results/EXACT_WHEEL_INDEX_VERIFICATION.json').read_text())
    assert full['FULL_A_SOURCE_REVALIDATION'] and full['NATIVE_TIME_BITWISE_VERIFICATION'] and full['candidates']==len(full['rows'])==12
    assert all(r['all_native_bits_verified'] and r['independent_role_and_mask_agreement'] for r in full['rows'])
    assert [r['subject'] for r in full['rows'] if r['prephysiology_possible']]==subjects
    assert wheel['STRICT_PAST_WHEEL_GATE'] and wheel['PL033_trial224']['equal_event_excluded']
    for row in full['rows']:
        if row['subject'] not in subjects:continue
        assert row['A_source_exact_full_role'] and row['all_37_nuisance_columns_exact_independent'] and row['all_QC_ranks_exact']
        assert row['preprocessing_sha256']==sha(P/'states'/(row['subject']+'_A_PREPROCESSING.json'))
        assert row['A_QC_sha256']==sha(P/'results'/(row['subject']+'_A_QC.json'))
