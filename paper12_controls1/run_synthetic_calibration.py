"""Trusted synthetic-only preparation; no original C/D/key/source read."""
import shutil
import sys
import numpy as np
import study as r
from native import security,prepare_job,launch

def science_code(code):
    code.mkdir()
    sources={n:r.HERE/n for n in ('calibration.py','test_calibration.py','access_check.py')}
    sources['worker.py']=r.HERE/'calibration_worker.py'
    sources.update({n:r.ROOT/'paper12_predictive_v2'/n for n in ('glm.py','accepted_fit.py','selection.py','test_glm.py','test_selection.py')})
    sources.update({n:r.OLD/n for n in ('baseline_fit.py','baseline_features.py','native_analysis_check.py')})
    sources['offset_math.py']=r.OFFSET/'offset_math.py'
    for name,p in sources.items():shutil.copy2(p,code/name)

def main():
    run_id=sys.argv[1] if len(sys.argv)>1 else '1'
    if not run_id.isdecimal():raise ValueError('SYNTHETIC_ATTEMPT_ID')
    r.verify();a=security();job=prepare_job('synthetic_C_'+run_id);data=job/'exports/C_only';data.mkdir();code=job/'exports/code';science_code(code)
    conditions=np.repeat(np.arange(8),24);orders=np.arange(192);sessions=[];metadata=[]
    for i in range(13):
        sid='synthetic_session_'+str(i);mouse='synthetic_mouse_'+str(i);values={}
        for region in ('CA1','DG'):
            ids=[f'{sid}_{region}_{j}' for j in range(32)]
            # Equal fixed rates keep every registered mandatory view available.
            base=np.random.default_rng(1200+i).poisson(.25,(192,20,32)).astype(np.uint32)
            values[region+'_C']=base;values[region+'_unit_ids']=np.array(ids)
            metadata.extend({'session_id':sid,'unit_id':uid,'probe_id':str(1+j%2),'nearest_other_channel_label_vertical_um':100.} for j,uid in enumerate(ids))
        values.update(conditions_C=conditions,orders_C=orders,trial_ids_C=np.array([sid+':'+str(j) for j in orders]))
        file=data/(sid+'.npz');np.savez(file,**values)
        sessions.append({'session_id':sid,'mouse_id':mouse,'file':file.name,'sha256':r.sha(file),'unit_ids':{k:values[k+'_unit_ids'].tolist() for k in ('CA1','DG')},'trial_ids':{'C':values['trial_ids_C'].tolist()}})
    r.save(data/'metadata.json',metadata)
    r.save(data/'manifest.json',{'group':'final','compartments':['C'],'synthetic':True,'sessions':sessions,
        'denial_probes':{'synthetic_D_key':str(job/'.private/key_canary.bin'),'synthetic_D_source':str(job/'.private/source_canary.bin')}})
    a.protect(data);a.protect(code)
    r.save(r.HERE/('synthetic_C_execution_registration_'+run_id+'.json'),{'utc':r.datetime.now(r.timezone.utc).isoformat(),'before_execution':True,'synthetic_only':True,
        'code_sha256':{p.name:r.sha(p) for p in code.iterdir()},'input_manifest_sha256':r.sha(data/'manifest.json'),'job':str(job.relative_to(r.HERE))})
    receipt,gate=launch('synthetic_C',job,data,code)
    r.save(r.HERE/('results/synthetic_C_'+run_id+'.json'),{'receipt':receipt,'gate':gate,'job':str(job.relative_to(r.HERE)),
        'state_output_directory':str((job/receipt['output_directory']).relative_to(r.HERE)),'certificate_receipt':receipt,'certificate_gate':gate})
    if receipt['exit_code']!=0 or receipt['timed_out'] or receipt['profile_cleanup_hresult']!='0x00000000' or not receipt['role_proof_pass'] or not gate or gate['gate']!='PASS':raise RuntimeError('SYNTHETIC_C_GATE_FAILED')
    print({'synthetic_C':'PASS','cases':gate['cases'],'D_consumed':False})
if __name__=='__main__':main()
