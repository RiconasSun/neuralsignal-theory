"""Seal public candidate and derive block evidence from saved CSV only."""
import csv
import re
import subprocess
import study as r

def main():
    public=r.HERE/'results/diagnostic/native'
    with (public/'gradient_scan.csv').open(encoding='utf-8',newline='') as f:rows=list(csv.DictReader(f))
    blocks={}
    for stage in ('initial','intermediate','endpoint'):
        blocks[stage]={}
        for block in ('recurrent','past_count','context','readout'):
            group=[z for z in rows if z['stage']==stage and z['block']==block]
            at_frozen=[z for z in group if float(z['scale'])==1e-5]
            blocks[stage][block]={
                'coordinates':len(at_frozen),
                'analytic_AD_abs_max':max(float(z['AD_abs_error']) for z in group),
                'analytic_AD_scaled_max':max(float(z['AD_scaled_error']) for z in group),
                'central_frozen_scaled_max':max(float(z['central_scaled_error']) for z in at_frozen),
                'ridge_gradient_abs_max':max(abs(float(z['ridge_AD'])-.001*float(z['theta'])) for z in group)}
    r.save(r.HERE/'block_summary.json',{'CSV_sha256':r.sha(public/'gradient_scan.csv'),'stages':blocks,'free_dynamic_intercepts':0,'frozen_offset_intercept_derivative':0})
    # Old tracked files are immutable except the explicitly authorized daily-status prefix.
    old=r.load(r.HERE/'prior_manifest.json')['sha256'];changed=[]
    for name,digest in old.items():
        if r.sha(r.ROOT/name)!=digest:changed.append(name)
    if changed!=['ops/daily-operations.md']:raise RuntimeError('PRIOR_EVIDENCE_CHANGED:'+str(changed))
    original=r.HERE/'original_daily_operations.md'
    if r.sha(original)!=old['ops/daily-operations.md'] or not (r.ROOT/'ops/daily-operations.md').read_bytes().endswith(original.read_bytes()):raise RuntimeError('DAILY_HISTORY_CHANGED')
    r.save(r.HERE/'preservation_audit.json',{'base':r.BASE,'prior_files':len(old),'unchanged':len(old)-1,'changed_only_status_prefix':changed,'original_daily_sha256':r.sha(original),'historical_suffix_exact':True,'mathematical_model_changes':0,'optimizer_policy_changes':0,'historical_drafts_unchanged':True})
    paths=subprocess.check_output(['git','ls-files','--others','--exclude-standard','-z'],cwd=r.ROOT).decode().split('\0')
    allowed=('paper12_contgrad1/','ops/evidence/2026-10-13/p12-m4-continuous-gradient-diag-1/')
    paths=[p for p in paths if p and p.startswith(allowed)]
    paths.append('ops/daily-operations.md')
    excluded={'paper12_contgrad1/final_manifest.json'}
    r.save(r.HERE/'final_manifest.json',{'base':r.BASE,'scope':'Final public numerical/source candidate; excludes this self manifest and subsequent final review/closure receipts','sha256':{p:r.sha(r.ROOT/p) for p in sorted(set(paths)-excluded)}})
    print('SEALED_PUBLIC_CANDIDATE',len(paths)-1,'prior_files',len(old),'new_fits',0)

if __name__=='__main__':main()
