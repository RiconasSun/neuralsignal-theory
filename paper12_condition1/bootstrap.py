"""Freeze baseline and historical manifests before numerical implementation."""
import subprocess
import csv
import study as r
def main():
    assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=r.ROOT).decode().strip()==r.BASE
    files=[p for p in subprocess.check_output(['git','ls-files','-z'],cwd=r.ROOT).decode().split('\0') if p]
    # Git blob identity is exact preservation proof without rereading1GB unrelated payloads here.
    identities={p:subprocess.check_output(['git','rev-parse',r.BASE+':'+p],cwd=r.ROOT).decode().strip() for p in []}
    tree=subprocess.check_output(['git','ls-tree','-r','-z',r.BASE],cwd=r.ROOT).decode().split('\0')
    for entry in tree:
        if entry:
            meta,name=entry.split('\t',1);identities[name]=meta.split()[2]
    r.save(r.HERE/'prior_git_manifest.json',{'base':r.BASE,'blob_sha1':identities,'tracked_paths':len(identities)})
    baseline=r.ROOT/'ops/evidence/2026-10-14/p12-m4-conditioning-optimizer-1/goldenstandards.md'
    r.save(r.HERE/'baseline_registration.json',{'utc':r.datetime.now(r.timezone.utc).isoformat(),'before_mathematical_implementation':True,'before_real_data_audit':True,'base':r.BASE,'baseline_requirements':42,'baseline_sha256':r.sha(baseline),'audit_protocol_sha256':r.sha(r.HERE/'audit_protocol.json'),'old_gradient_gate_sha256':r.sha(r.GRAD/'results/diagnostic/native/gate_result.json'),'old_CSV_sha256':r.sha(r.GRAD/'results/diagnostic/native/gradient_scan.csv'),'old_execution_sha256':r.sha(r.GRAD/'execution_registration.json')})
    source=r.GRAD/'results/diagnostic/native/gradient_scan.csv'
    with source.open(encoding='utf-8',newline='') as f:rows=list(csv.DictReader(f))
    vectors={name:[float(next(z for z in rows if z['stage']==name and int(z['coordinate'])==i)['theta']) for i in range(384)] for name in ('initial','intermediate','endpoint')}
    hashes={name:next(z for z in rows if z['stage']==name)['theta_sha256'] for name in vectors}
    r.save(r.HERE/'saved_vectors.json',{'source_CSV_sha256':r.sha(source),'theta_sha256':hashes,'vectors':vectors,'no_neural_arrays':True})
    r.save(r.HERE/'mission.json',{'mission':{'id':'P12-M4-CONDITIONING-OPTIMIZER-1','objective':'Prospectively registered A-only conditioning audit and exactly three bounded optimization feasibility policies; preserve every prior FAIL; STOP after independent review and origin/test closure.'},'target':{'workdir':str(r.ROOT),'files':['paper12_condition1/**','ops/evidence/2026-10-14/p12-m4-conditioning-optimizer-1/**','ops/daily-operations.md']},'instructions':{'constraints':['No source repairs','No model/ridge/offset/threshold changes','No validation/final data','No fourth candidate or retry/budget expansion']},'acceptance':{'criteria':['42 atomic requirements','all3 fixed outcomes','independent AD and full physical PG','normal origin/test clean readback']},'codex':{'sandbox':'workspace-write','approval':'on-request'},'openrouter':{'enabled':False}})
    print('BASELINE_REGISTERED',r.sha(baseline),'requirements42','priorpaths',len(files))
if __name__=='__main__':main()
