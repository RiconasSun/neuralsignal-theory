"""Append-only saved-evidence verifier; never optimize or unlock a holdout."""
import argparse
import subprocess
import sys
from datetime import datetime, timezone

import numpy as np
import run_r2 as run

OUT = run.base.STUDY/'results/R2_saved_audit'
SOURCES = ['scripts/r2_saved_audit.py','scripts/reproduce-r2-audit.ps1','tests/test_r2_saved_audit.py']


def register():
    run.verify()
    if (OUT/'registration.json').exists():
        verify()
        return
    run.base.save(OUT/'registration.json',{
        'registered_utc':datetime.now(timezone.utc).isoformat(),
        'before_saved_audit_tests':True,'scope':'Saved evidence only, no new scientific fits or selection',
        'reason':'Original negative-replay baseline constructor failure could lack theta. Skip failed rows BEFORE constructing/accessing theta; no original source/gate overwrite.',
        'source_sha256':{f'paper11_v2/{p}':run.base.digest(run.base.STUDY/p) for p in SOURCES},
        'R2_registration_sha256':run.base.digest(run.OUT/'registration.json'),
        'no_model_or_optimizer_or_split_changes':True},immutable=True)


def verify():
    run.verify()
    reg = run.load(OUT/'registration.json')
    for path,sha in reg['source_sha256'].items():
        if run.base.digest(run.base.ROOT/path)!=sha:
            raise RuntimeError('Saved audit source changed: '+path)
    if run.base.digest(run.OUT/'registration.json')!=reg['R2_registration_sha256']:
        raise RuntimeError('Original R2 registration changed')


def check_row(row,d,offset=None):
    # Failed evidence is preserved, not re-fitted, rehabilitated or selected.
    if not row['converged']:
        return {'state':'PRESERVED_FAILURE','refitted':False,'record':row}
    c = row['config']
    theta = np.asarray(row['theta'])
    if c['family']=='stationary':
        np.testing.assert_allclose(theta,run.models.fit_stationary(d['ytrain']),rtol=0,atol=1e-12)
        scores = run.models.poisson_logpmf(d['yval'],theta).sum(axis=-1)
        loss = -run.models.poisson_logpmf(d['ytrain'],theta).mean()
        norm = 0.
    else:
        t,v = run.make_pair(d,c,offset)
        loss,gradient = t.objective(theta,c['ridge'])
        norm = float(np.linalg.norm(gradient,ord=np.inf))
        scores = v.score_bins(theta)
    trials = scores.sum(axis=1)/(d['yval'].shape[1]*d['yval'].shape[2])
    np.testing.assert_allclose(trials,row['trial_scores'],rtol=0,atol=1e-10)
    np.testing.assert_allclose([loss,norm],[row['loss'],row['gradient_norm']],rtol=0,atol=1e-10)
    return {'state':'SAVED_SCORE_VERIFIED','max_score_error':float(np.max(np.abs(trials-row['trial_scores']))),
            'objective_error':float(abs(loss-row['loss'])),'refitted':False}


def find_offset(d,c,folder):
    rows = [run.load(p) for p in folder.glob(run.configuration_id(c)+'_seed*.json')]
    rows.sort(key=lambda r:run.SEEDS.index(r['seed']))
    return run.offset_pair(d,c,run.resolved(rows))[0]


def replay():
    verify()
    locked = run.load(run.OUT/'artifact_lock.json')['sha256']
    for path,sha in locked.items():
        if run.base.digest(run.base.ROOT/path)!=sha:
            raise RuntimeError('R2 saved artifact changed: '+path)
    gate = run.load(run.OUT/'gate_result.json')
    paths = sorted((run.OUT/'fits').rglob('*.json'))
    output = []
    cache,offsets = {},{}
    oc = (run.load(run.OUT/'baseline_selection.json')['combined_offset']['selected_config']
          if (run.OUT/'baseline_selection.json').exists() else None)
    for path in paths:
        row = run.load(path)
        if not row['converged']:
            output.append({'path':run.relative(path),**check_row(row,None)})
            continue
        key = row['session']
        if key not in cache:
            cache[key] = run.data.session(key)
        d = cache[key]
        offset = None
        if row['config']['family'] not in run.KINDS:
            if key not in offsets:
                offsets[key] = find_offset(d,oc,run.OUT/'fits/baselines'/key.replace('/','_'))
            offset = offsets[key]
        output.append({'path':run.relative(path),**check_row(row,d,offset)})
    # Null fitted rows use exactly the registered partition-local transformation.
    for path in sorted((run.OUT/'nulls').rglob('*_seed*.json')):
        row = run.load(path)
        if not row['converged']:
            output.append({'path':run.relative(path),**check_row(row,None)})
            continue
        kind,replicate = path.relative_to(run.OUT/'nulls').parts[:2]
        d = dict(cache.setdefault(row['session'],run.data.session(row['session'])))
        for split in ['train','val']:
            d['y'+split],d['x'+split],_ = run.stats.transform_null(d['y'+split],d['x'+split],kind,int(replicate),
                                                   partition=f"{row['session']}/{split}")
        offset = None
        if row['config']['family'] not in run.KINDS:
            folder = run.OUT/'nulls'/kind/replicate/'offset'/row['session'].replace('/','_')
            offset = find_offset(d,oc,folder)
        output.append({'path':run.relative(path),**check_row(row,d,offset)})
    tests = subprocess.run([sys.executable,'-m','unittest','discover','-s',str(run.base.STUDY/'tests'),
                            '-p','test_r2*.py','-v'],capture_output=True,text=True)
    receipt = {'scientific_gate_unchanged':gate['gate_verdict'],'scientific_verdict':gate['scientific_verdict'],
               'tests_exit_code':tests.returncode,'checked_rows':len(output),
               'verified_successful_rows':sum(r['state']=='SAVED_SCORE_VERIFIED' for r in output),
               'preserved_failure_rows':sum(r['state']=='PRESERVED_FAILURE' for r in output),
               'max_score_error':max([r.get('max_score_error',0.) for r in output],default=0.),
               'max_objective_error':max([r.get('objective_error',0.) for r in output],default=0.),
               'no_refitting':True,'no_oldtest_or_external_spikes':True,
               'original_artifact_count':len(locked),'original_artifact_lock_sha256':run.base.digest(run.OUT/'artifact_lock.json')}
    if not (OUT/'receipt.json').exists():
        run.base.save(OUT/'receipt.json',receipt,immutable=True)
        (OUT/'tests.log').write_text(tests.stdout+tests.stderr,encoding='utf-8')
        run.base.save(OUT/'row_audit.json',output,immutable=True)
        run.base.save(OUT/'artifact_lock.json',{'sha256':{run.relative(p):run.base.digest(p) for p in OUT.iterdir() if p.is_file()}},immutable=True)
    else:
        if receipt!=run.load(OUT/'receipt.json'):
            raise RuntimeError('Saved audit receipt is not reproducible')
        for path,sha in run.load(OUT/'artifact_lock.json')['sha256'].items():
            if run.base.digest(run.base.ROOT/path)!=sha:
                raise RuntimeError('Saved audit artifact changed: '+path)
    print(tests.stdout+tests.stderr)
    print(receipt)
    return tests.returncode


if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('action',choices=['register','replay'])
    action = parser.parse_args().action
    if action=='register':
        register()
    else:
        sys.exit(replay())
