"""Saved-C endpoint/state sealing and prospective D specification; no D reads."""
import datetime
import numpy as np
from .source import P,R,read,dump,sha
from .calibration import admitted,configurations
from .models import pg
from .statistics import CONTRASTS


def verify_endpoint(record,config,state_hash):
    assert record['configuration']==config and record['C_state_sha256']==state_hash
    assert record['production_gate_sha256']==sha(P/'C_PRODUCTION_GATE.json') and record['attempt']==1
    assert record['status'] in ('NUMERICAL_PASS','NUMERICAL_FAIL') and 'error' not in record,'Interrupted/exception state is critical'
    if record['status']=='NUMERICAL_FAIL':return False
    theta=np.asarray(record['coefficients']);g=np.asarray(record['independent']['analytic_gradient']);bounds=np.asarray(record['bounds'])
    assert theta.shape==g.shape==(record['free_parameters'],) and bounds.shape==(len(theta),2)
    assert np.isfinite(theta).all() and np.isfinite(g).all() and np.isfinite(record['objective'])
    assert ((theta>=bounds[:,0])&(theta<=bounds[:,1])).all()
    assert pg(theta,g,bounds)==record['PG']<=.001 and record['finite_all'] and record['exact_bounds'] and not record['budget_exhausted']
    ind=record['independent'];ad=np.asarray(ind['AD_gradient']);scale=np.maximum(1.,np.maximum(abs(g),abs(ad)))
    assert np.isfinite(ad).all() and np.array_equal(abs(g-ad)/scale,np.asarray(ind['AD_coordinate_scaled']))
    assert np.max(abs(g-ad)/scale,initial=0)==ind['AD_max_scaled']<=1e-5
    assert record['objective']==ind['objective'] and abs(ind['objective']-ind['AD_objective'])<=1e-8*max(1,abs(ind['objective']))
    assert [x['step'] for x in ind['FD']]==[1e-4,1e-5,1e-6]
    for item in ind['FD']:
        fd=np.asarray(item['numerical_gradient']);scaled=abs(fd-g)/np.maximum(1.,np.maximum(abs(fd),abs(g)))
        assert np.isfinite(fd).all() and np.array_equal(scaled,np.asarray(item['coordinate_scaled']))
        assert scaled.max(initial=0)==item['max_scaled']<=1e-5
    assert ind['PASS'] is True and np.isfinite(record['training_score_LL'])
    return True


def run():
    assert not (P/'FINAL_C_STATE_SEAL.json').exists()
    assert not (P/'results/C_MAIN_REQUIRED_STOP.json').exists() and not (P/'results/C_SENSITIVITY_REQUIRED_STOP.json').exists()
    main_complete=read(P/'results/C_MAIN_ATTEMPTS_COMPLETE.json');sens_complete=read(P/'results/C_SENSITIVITY_ATTEMPTS_COMPLETE.json')
    plan=read(P/'C_FIT_PLAN.json');splan=read(P/'SENSITIVITY_FIT_PLAN.json');subjects=admitted();configs=configurations()
    assert main_complete['attempted']==plan['expected_attempts']==len(subjects)*12
    assert sens_complete['attempted']==splan['expected_attempts'] and plan['subjects']==splan['subjects']==subjects
    family_subjects={f:[] for f in ['B0','B1','B2','B3','B4','C','D','S']};main_rows=[]
    for subject in subjects:
        sh=sha(P/'states'/(subject+'_C_PREPROCESSING.json'));assert sh==plan['state_hashes'][subject]
        successful={}
        for config in configs:
            path=P/'fits'/subject/(config['id']+'.json');record=read(path);valid=verify_endpoint(record,config,sh)
            successful.setdefault(config['family'],[]).append(valid)
            main_rows.append(dict(subject=subject,configuration=config,path=path.relative_to(P).as_posix(),sha256=sha(path),valid=valid))
        assert all(all(successful[f]) for f in ['B0','B1','B2','B3','B4'])
        for family,valids in successful.items():
            if all(valids):family_subjects[family].append(subject)
    sensitivity_rows=[]
    for item in splan['attempts']:
        path=P/'sensitivity_fits'/item['subject']/item['case']/(item['family']+'.json')
        config=dict(id=item['family'],family=item['family'],ridge=item['ridge'],seed=11)
        valid=verify_endpoint(read(path),config,item['state_sha256'])
        sensitivity_rows.append(dict(item=item,path=path.relative_to(P).as_posix(),sha256=sha(path),valid=valid))
    artifacts=[]
    for folder in ['states','sensitivity_states','fits','sensitivity_fits','metadata','source']:
        artifacts += [dict(path=p.relative_to(P).as_posix(),sha256=sha(p)) for p in sorted((P/folder).rglob('*.json'))]
    for name in ['C_FIT_PLAN.json','SENSITIVITY_FIT_PLAN.json','C_READER_GATE.json','C_PRODUCTION_GATE.json',
                 'SOURCE_FILE_FREEZE.json','FINAL_SOURCE_HEADER_FREEZE.json','METADATA_SOURCE_EXTERNAL_FREEZE.json',
                 'REFERENCE_METADATA_FREEZE.json','results/FINAL_C_QC_GATE.json','results/FINAL_METADATA_GATE.json',
                 'results/C_MAIN_ATTEMPTS_COMPLETE.json','results/C_SENSITIVITY_ATTEMPTS_COMPLETE.json',
                 'results/C_FEATURE_PREPARATION.json','results/C_SENSITIVITY_PREPARATION.json']:
        artifacts.append(dict(path=name,sha256=sha(P/name)))
    for path in sorted((P/'results').glob('*_C_QC.json')):artifacts.append(dict(path=path.relative_to(P).as_posix(),sha256=sha(path)))
    seal=dict(time=datetime.datetime.now(datetime.timezone.utc).isoformat(),primary_subjects=subjects,
        source_QC_primary_coverage=False,mandatory_descriptive_only=True,family_subjects=family_subjects,
        main_attempts=len(main_rows),sensitivity_attempts=len(sensitivity_rows),main=main_rows,sensitivities=sensitivity_rows,
        artifacts=artifacts,raw_work_arrays_in_public_archive=False,complete_calibration_state=True,D_neural_scientific_access=False,
        initial_filters='Reset pi at epoch start; no C posterior crosses trial or role. C-state pre-epoch history zero.',
        original_attempts=359,R1_corrective_attempts=1135,cumulative_attempts=1494+len(main_rows)+len(sensitivity_rows))
    dump(P/'FINAL_C_STATE_SEAL.json',seal)
    comparisons={c:[s for s in subjects if s in family_subjects[a] and s in family_subjects[b]] for c,(a,b) in CONTRASTS.items()}
    ref=read(P/'REFERENCE_METADATA_FREEZE.json')
    specification=dict(time=datetime.datetime.now(datetime.timezone.utc).isoformat(),mission='P15-M6-INDEPENDENT-FINAL-VALIDATION',
        primary_subjects=subjects,family_subjects=family_subjects,contrast_subjects=comparisons,
        mandatory_descriptive_only=True,confirmatory_assumptions_defensible=False,
        assumption_scope='Frozen sign-flip computation is conditional on independence and symmetric sign exchangeability; observational convenience sample/shared labs cannot establish them. No D pretest or alternative test; confirmatory labels withheld, in addition to six-mouse floor.',
        source_main_numerical_valid=True,static_capacity_pair_valid=True,D_batches=1,all11cases=True,
        reference_suites=['N1','N2','N3','N4'],replicates_per_available_suite=999,
        expected_reference_bundles=999*sum(v['available'] for r in ref['records'] for v in r['coverage'].values()),
        source_exclusions=['NYU-21'],C_QC_exclusions=['UCLA033'],
        source_exclusions_fixed_before_D=True,C_model_policies_selected_only_in_Development_B=True,
        interrupted_or_essential_D_failure='Preserve partial outputs, mark INCONCLUSIVE REQUIRED GATE, STOP without rerun or repair',
        no_D_fit_or_selection=True,no_Prompt5=True)
    dump(P/'ONE_SHOT_D_SPECIFICATION.json',specification)
    print('Saved C state sealed',len(main_rows),len(sensitivity_rows),'attempts; six-mouse descriptive D specification registered, not released')


if __name__=='__main__':run()
