"""Public frozen metadata only. Never opens custody source/key/count artifacts."""
from pathlib import Path
import shutil
from .common import *
from . import study as r

def materialize(output):
    output=Path(output);output.mkdir(exist_ok=False)
    sources={'C_state_manifest.json':r.EVIDENCE.parent.parent/'2026-10-14/p12-c-seal-host-import-repair-1/complete_C_state_manifest.json','animals.json':r.ROOT/'paper12_curated_v1/locks/animals.json','units.json':r.ROOT/'paper12_curated_v1/locks/units.json','trials.json':r.ROOT/'paper12_curated_v1/locks/trials.json','final_D_partition_manifest.json':r.ROOT/'paper12_controls1/final_D_partition_manifest.json'}
    for name,source in sources.items():shutil.copyfile(source,output/name)
    c=read_json(output/'C_state_manifest.json');trials=read_json(output/'trials.json');units=read_json(output/'units.json');conditions=sorted({t['condition'] for t in trials})
    partition={'cohort':c['cohort'],'D_trial_ids':{},'sessions':{}};catalog={'realm':'REAL_D','cohort':c['cohort'],'sessions':{}};ordered={};roots={'realm':'REAL_D','repository_root':str(r.ROOT),'sessions':{}}
    for mouse in c['cohort']:
        sid=next(v['session_id'] for v in c['cases'] if v['mouse_id']==mouse);receipt_path=r.ROOT/'paper12_resume1/results/M2/sessions'/(sid+'.json');receipt=read_json(receipt_path)
        shutil.copyfile(receipt_path,output/('source_receipt_'+sid+'.json'))
        rows=[t for t in trials if t['session_id']==sid and t['partition']=='locked_evaluation' and t['metadata_admitted']];ids=[t['trial_id'] for t in rows];ordered[sid]=[u['unit_id'] for u in units if u['session_id']==sid]
        partition['D_trial_ids'][mouse]=ids;partition['sessions'][mouse]={'session_id':sid,'trial_ids':ids,'conditions':[conditions.index(t['condition']) for t in rows],'orders':[t['provider_row_index'] for t in rows]}
        context={'study':'P12-M2-ISOLATED-CUSTODY-1','mouse':mouse,'source_etag':receipt['source_etag'],'trial_lock_sha256':sha(output/'trials.json'),'unit_lock_sha256':sha(output/'units.json'),'compartment':'D','shape':[len(ids),20,len(ordered[sid])],'dtype':'<u4'}
        catalog['sessions'][mouse]={'mouse_id':mouse,'session_id':sid,'trial_ids_D':ids,'source_unit_ids':ordered[sid],'context':context,'cipher_file':sid+'/D.gcm','key_file':sid+'/D.key','ciphertext_sha256':receipt['ciphertext_receipts']['D']['ciphertext_sha256']}
        roots['sessions'][mouse]={'root':str(r.ROOT/receipt['artifact_study']/'.private'/receipt['custody_artifact_namespace']),'artifact_study':receipt['artifact_study'],'namespace':receipt['custody_artifact_namespace']}
    validate_partition(c,partition,read_json(output/'animals.json'),trials)
    for name,value in (('partition_manifest.json',partition),('source_units.json',ordered),('source_catalog.json',catalog),('source_roots.json',roots)):new(output/name,value)
    return {'metadata_only':True,'neural_array_or_key_reads':0,'mice':len(c['cohort']),'cases':len(c['cases']),'distinct_custody_roots':len({v['root'] for v in roots['sessions'].values()}),'sha256':{p.name:sha(p) for p in output.iterdir()}}
