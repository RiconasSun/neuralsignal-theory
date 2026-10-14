"""Necessary deterministic endpoint reconstruction for the unchanged legacy PG oracle."""
import ast
import shutil
import launch
import study as r
def main():
    phase='original_pg_certificate'
    if (r.HERE/(phase+'_execution_registration.json')).exists():raise RuntimeError('NO_CERTIFICATE_RETRY')
    a=launch.security();code=r.HERE/'exports/code_original_pg_certificate';shutil.copytree(r.HERE/'exports/code_science',code)
    old={}
    for p in (r.HERE/'results/science/native').glob('*_fit.json'):
        v=r.load(p);old[v['case']+'_'+v['model']]=v['coefficient_sha256']
    r.save(code/'old_coefficient_hashes.json',old)
    text=(r.HERE/'fit_worker.py').read_text()
    text=text.replace('rows=[];arrays={};attempts=0;',"old_hashes=load(code/'old_coefficient_hashes.json')\n    rows=[];arrays={};attempts=0;")
    text=text.replace("record.update(unit_id=str(z[region+'_unit_ids'][ids[u]]),attempt=attempts)","record.update(unit_id=str(z[region+'_unit_ids'][ids[u]]),attempt=attempts)\n                                xx=xa[:,:,u,indices].reshape(-1,len(indices));yy=y[:,:,u].ravel();ff,gg=obj(theta,xx,yy);af,ag=independent_ad(theta,xx,yy)\n                                legacy=gg.copy();legacy[(theta<=-8)&(legacy>0)]=0;legacy[(theta>=8)&(legacy<0)]=0\n                                adlegacy=ag.copy();adlegacy[(theta<=-8)&(adlegacy>0)]=0;adlegacy[(theta>=8)&(adlegacy<0)]=0\n                                record['original_definition_PG']=float(np.abs(legacy).max());record['AD_original_definition_PG']=float(np.abs(adlegacy).max())\n                                record['passed']=record['passed'] and record['original_definition_PG']<=.001 and record['AD_original_definition_PG']<=.001")
    text=text.replace("case_count+=1;save(case+'_'+name+'_fit.json'", "if hashlib.sha256(np.ascontiguousarray(w).tobytes()).hexdigest()!=old_hashes[case+'_'+name]:raise RuntimeError('ENDPOINT_RECONSTRUCTION_NOT_IDENTICAL')\n                            case_count+=1;save(case+'_'+name+'_fit.json'")
    text=text.replace("maxpg=max(maxpg,pg(mean[u],g));", "legacy=g.copy();legacy[(mean[u]<=-8)&(legacy>0)]=0;legacy[(mean[u]>=8)&(legacy<0)]=0\n                                adlegacy=ag.copy();adlegacy[(mean[u]<=-8)&(adlegacy>0)]=0;adlegacy[(mean[u]>=8)&(adlegacy<0)]=0\n                                maxpg=max(maxpg,float(np.abs(legacy).max()),float(np.abs(adlegacy).max()));")
    ast.parse(text)
    (code/'worker.py').unlink();(code/'worker.py').write_text(text,encoding='utf-8');a.protect(code)
    hashes={p.name:r.sha(p) for p in code.iterdir() if p.is_file()};original=r.load(r.HERE/'science_execution_registration.json')
    r.save(r.HERE/(phase+'_execution_registration.json'),{'utc':r.datetime.now(r.timezone.utc).isoformat(),'before_original_PG_reconstruction':True,'code_sha256':hashes,'source_sha256':{'certify_original_pg.py':r.sha(r.HERE/'certify_original_pg.py')},'reason':'Acceptance implementation defect: step-projection norm is not the original outward-gradient PG definition. Existing coefficients absent for sensitivities, so deterministic endpoint reconstruction is necessary verification, not model replacement or favorable rerun. Original GLM source/optimizer/settings are byte-identical. Require all 910 coefficient hashes exactly identical. Stop if any legacy PG fails. No old M3 or offset refits. Retain both complete passes and total repeated fit counts.','baseline_record':'REQ-020 original numerical oracle clarified, not threshold weakened. Protocol one scientific fit attempt remains recorded; supplementary necessary certification replays are separately recorded before execution, with unchanged per-fit/phase caps.','registered_expected_reconstructed_cases':910,'registered_expected_unit_fit_replays':21476,'scientific_model_selection':False,'optimizer_changes':False,'protocol_sha256':r.sha(r.HERE/'PROTOCOL.md'),'original_science_registration_sha256':r.sha(r.HERE/'science_execution_registration.json'),'AB_manifest_sha256':original['AB_manifest_sha256'],'runtime_sha256':original['runtime_sha256'],'final_access':False})
    launch.native(phase,r.HERE/'exports/development_AB',code,hashes,a)
if __name__=='__main__':main()
