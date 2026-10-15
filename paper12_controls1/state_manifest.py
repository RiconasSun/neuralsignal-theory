"""Trusted sealing of complete C states and numerical certificates; no D data."""
import shutil
import importlib.util
import zipfile
from pathlib import Path
import numpy as np
from release_control import canonical,digest,read_json,validate_state_manifest

def create(output,destination):
    output=Path(output);destination=Path(destination);destination.mkdir(exist_ok=False)
    report=read_json(output/'calibration_states.json');cases=[];seeds={};artifacts={}
    job=output.parents[2];data=job/'exports/C_only'
    def copy(name):
        shutil.copy2(output/name,destination/name);artifacts[name]=digest((destination/name).read_bytes())
    def provenance(source,name):
        target='provenance_'+name
        shutil.copy2(source,destination/target);artifacts[target]=digest((destination/target).read_bytes())
    def write(name,value):
        (destination/name).write_bytes(canonical(value)+b'\n');artifacts[name]=digest((destination/name).read_bytes())
    inputs=read_json(data/'manifest.json');metadata=read_json(data/'metadata.json')
    if report['input_manifest_sha256']!=digest((data/'manifest.json').read_bytes()) or report['metadata_sha256']!=digest((data/'metadata.json').read_bytes()):raise ValueError('INPUT_PROVENANCE_DRIFT')
    provenance(data/'manifest.json','input_manifest.json');provenance(data/'metadata.json','metadata.json')
    provenance(output/'calibration_states.json','calibration_states.json')
    for name in ('role_proof.json','gate_result.json','extra_role_denials.json','protected_open_checks_without_reading.json'):
        provenance(output/name,name)
    receipts=list((job/'results').glob('*_launch_receipt.json'))
    if len(receipts)!=1:raise ValueError('EXACT_ACTUAL_LAUNCH_RECEIPT_REQUIRED')
    provenance(receipts[0],'launch_receipt.json')
    roster=output/'private_prefit_roster.json'
    if roster.exists():provenance(roster,'roster.json')
    elif inputs['synthetic'] is True:
        # Reconstruct only saved synthetic fixtures; never mislabel this as prospective.
        import sys
        sys.path.insert(0,str(job/'exports/code'))
        spec=importlib.util.spec_from_file_location('current_roster_calibration',Path(__file__).parent/'calibration.py')
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);collected=[]
        md={(m['session_id'],m['unit_id']):m for m in metadata}
        def read(s):
            p=data/s['file']
            if digest(p.read_bytes())!=s['sha256']:raise ValueError('SAVED_SYNTHETIC_INPUT_DRIFT')
            with np.load(p,allow_pickle=False) as z:return {k:z[k] for k in module.FIELDS}
        module.coverage(inputs['sessions'],read,md,lambda k,v:collected.append(v));sys.path.pop(0)
        value=collected[0];value['registration']='RETROSPECTIVE_SAVED_SYNTHETIC';write('provenance_roster.json',value)
    else:raise ValueError('REAL_PROSPECTIVE_ROSTER_REQUIRED')
    if inputs['synthetic']:write('provenance_QC.json',{'scope':'SYNTHETIC_FIXTURE_NO_PHYSIOLOGICAL_CLAIM','synthetic':True})
    else:provenance(data/'C_QC_attestation.json','QC.json')
    import study as r
    write('provenance_identity.json',{'source_code_sha256':{p.name:r.sha(p) for p in (job/'exports/code').glob('*.py')},
        'runtime_sha256':r.load(r.ROOT/'paper12_contgrad1/execution_registration.json')['runtime_sha256'],
        'frozen_source_sha256':r.verify()['source_sha256'],'C_approval_sha256':inputs.get('C_approval_sha256'),
        'sealer_sha256':r.sha(Path(__file__)),'checkpoint_sha256':{p.name:r.sha(p) for p in sorted(output.glob('*.npy'))}})
    journals={}
    with zipfile.ZipFile(destination/'attempt_journals.zip','x',zipfile.ZIP_DEFLATED) as archive:
        for p in sorted(output.glob('*.json')):
            if p.name.startswith('private_'):continue
            raw=p.read_bytes();journals[p.name]=digest(raw);archive.writestr(p.name,raw)
    artifacts['attempt_journals.zip']=digest((destination/'attempt_journals.zip').read_bytes());write('attempt_journals_index.json',journals)
    copy('complete_states.npz')
    with np.load(output/'complete_states.npz',allow_pickle=False) as arrays:
        for row in report['cases']:
            case=row['case'];models={}
            for model in row['models']:
                name=case+'_'+model+'.json';copy(name);v=dict(row['arrays'][model]);v['certificate_sha256']=artifacts[name];models[model]=v
            m=arrays[case+'_mean'];s=arrays[case+'_scale']
            cases.append({'case':case,'mouse_id':row['mouse_id'],'session_id':row['session_id'],'region':row['region'],'view':row['view'],'unit_ids':row['unit_ids'],'selection':row['selection'],
                'trial_ids':row['C_trial_ids'],'trial_mask_sha256':digest(canonical(row['C_trial_ids'])),'mean_key':case+'_mean','scale_key':case+'_scale',
                'scaler_sha256':digest(np.ascontiguousarray(m).tobytes()+np.ascontiguousarray(s).tobytes()),'models':models})
            if row['view']=='primary':
                prefix=row['session_id']+'_'+row['region']
                for seed in ('11','23','37','mean'):
                    name=prefix+('_N_mean' if seed=='mean' else '_N_seed'+seed)+'.json';copy(name);cert=read_json(output/name)
                    if not cert['passed']:raise ValueError('FAILED_N_CERTIFICATE')
                    array_key=case+'_N' if seed=='mean' else prefix+'_N_seed'+seed
                    seeds[row['mouse_id']+'_'+row['region']+'_'+seed]={'file':name,'sha256':artifacts[name],'original_PG':cert['original_PG'],'AD_error':cert['AD_scaled_error'],
                        'array_key':array_key,'array_sha256':digest(np.ascontiguousarray(arrays[array_key]).tobytes())}
    roster=read_json(destination/'provenance_roster.json')
    expected=[[s['mouse_id'],region,view] for s in roster['sessions'] for view in s['views'] for region in ('CA1','DG')]
    manifest={'version':2,'cohort':[s['mouse_id'] for s in inputs['sessions']],'cases':cases,'expected_cases':expected,'seed_certificates':seeds,
              'coverage':roster['paired_counts'],'synthetic':inputs['synthetic'],'artifact_sha256':artifacts}
    validate_state_manifest(manifest,destination)
    (destination/'C_state_manifest.json').write_bytes(canonical(manifest)+b'\n')
    return manifest
