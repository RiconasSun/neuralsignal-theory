"""Final public source/results seal; never runs a numerical experiment."""
import subprocess
import study as r
def main():
    outcome=r.load(r.HERE/'results/study_outcome.json')
    if outcome['candidate_count']!=3 or outcome['objective_gradient_calls']>24500:raise RuntimeError('EXACT_BOUNDED_COMPLETION')
    for registration in ('trial_registration.json',):
        for name,digest in r.load(r.HERE/registration)['source_sha256'].items():
            if r.sha(r.ROOT/name)!=digest:raise RuntimeError('NUMERICAL_SOURCE_CHANGED_AFTER_TRIAL:'+name)
    paths=[p for p in subprocess.check_output(['git','ls-files','--others','--exclude-standard','-z'],cwd=r.ROOT).decode().split('\0') if p]
    permitted=('paper12_condition1/','ops/evidence/2026-10-14/p12-m4-conditioning-optimizer-1/')
    if any(not p.startswith(permitted) for p in paths):raise RuntimeError('UNRELATED_UNTRACKED')
    paths.append('ops/daily-operations.md')
    r.save(r.HERE/'final_manifest.json',{'base':r.BASE,'scientific_outcome':outcome['scientific_outcome'],'scope':'Final public source/results candidate; excludes self and subsequent append-only review/closure receipts','sha256':{p:r.sha(r.ROOT/p) for p in sorted(paths)}})
    print('FINAL_PUBLIC_CANDIDATE_SEALED',len(paths),r.sha(r.HERE/'final_manifest.json'))
if __name__=='__main__':main()
