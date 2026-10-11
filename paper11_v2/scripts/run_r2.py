"""Prospectively registered real-development evaluation with immediate fail-stop.

No external neural accessor exists here. R2-C needs a separate frozen accessor
and source-supported observation audit after all mandatory development gates.
"""
import argparse
import csv
import json
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import scipy
import run_r0 as base
import r2_data as data
import r2_models as models
import r2_statistics as stats

OUT = base.STUDY/'results/R2'
SOURCE = ['protocol/r2_execution.json','scripts/r2_data.py','scripts/r2_models.py',
          'scripts/r2_statistics.py','scripts/run_r2.py','scripts/reproduce-r2.ps1',
          'tests/test_r2.py','tests/test_r2_statistics.py','tests/test_r2_runner.py']
RIDGES, SEEDS = [.001,.01,.1,1.], [11,23,37]
KINDS = ['stationary','history','event','drift','combined','population']


def load(path):
    return data.load(path)


def relative(path):
    return str(path.relative_to(base.ROOT)).replace('\\','/')


def verify():
    reg = load(OUT/'registration.json')
    for field in ['source_sha256','preceding_sha256','archive_sha256']:
        for rel,sha in reg[field].items():
            if base.digest(base.ROOT/rel)!=sha:
                raise RuntimeError(f'R2 immutable identity changed: {rel}')
    for milestone in ['R0_amendment1_code1','R1_code1']:
        if load(base.STUDY/'results'/milestone/'gate_result.json')['gate_verdict']!='PASS':
            raise RuntimeError('Preceding gate not PASS')
    return reg


def register():
    if (OUT/'registration.json').exists():
        verify()
        print('Existing R2 prospective registration verified; no overwrite.')
        return
    subprocess.run([sys.executable,str(base.STUDY/'scripts/run_r1_code1.py'),'verify'],check=True)
    prior = load(base.STUDY/'results/R1_code1/registration.json')
    mutable = {'paper11_v2/MILESTONE_STATUS.md','paper11_v2/CLAIM_AUDIT.md','ops/daily-operations.md'}
    names = base.git('ls-files','-z').split('\0')
    preceding = {p:base.digest(base.ROOT/p) for p in names if p and p not in mutable
                 and (p.startswith('paper11_v2/') or p.startswith('ops/evidence/'))}
    base.save(OUT/'registration.json',{
        'study':'P11-v2','milestone':'R2','registered_utc':datetime.now(timezone.utc).isoformat(),
        'checkpoint':'6f5e33e3b18f9ccc630e12757d42f271ba859bbe',
        'base_commit':base.git('rev-parse','HEAD'),
        'source_sha256':{f'paper11_v2/{p}':base.digest(base.STUDY/p) for p in SOURCE},
        'preceding_sha256':preceding,'archive_sha256':prior['archive_sha256'],
        'policy':load(base.STUDY/'protocol/r2_execution.json'),
        'before_tests_and_real_fits':True,'python':platform.python_version(),
        'numpy':np.__version__,'scipy':scipy.__version__,
        'external_split_sha256':base.digest(base.STUDY/'results/R0_schema1/final_validation_lock.json'),
        'engineering_wrapper':'CLI exit1 unsupported gpt-6.1-sol with ChatGPT account; no generated edits; direct-tools fallback, no auth/model override.',
        'mutable_current_status_exceptions':sorted(mutable),
        'external_accessor_enabled':False},immutable=True)
    print('R2 registered before tests and real-data fitting.')


def baseline_configs():
    return [{'family':kind,'ridge':ridge} for kind in KINDS
            for ridge in ([0.] if kind=='stationary' else RIDGES)]


def family_configs():
    shapes = [('discrete',k,0) for k in [2,4]]
    shapes += [('continuous',d,0) for d in [1,2,4]]
    shapes += [('hybrid',k,l) for k in [2,4] for l in [1,5]]
    return [{'family':f,'size':s,'lags':l,'ridge':r} for f,s,l in shapes for r in RIDGES]


def configuration_id(config):
    return '_'.join(str(config[k]) for k in sorted(config))


def roster():
    names = sorted(p.stem.replace('_','/') for p in (data.COHORT/'sessions').glob('*.json')
                   if load(p)['admitted'])
    if len(names)!=23 or len({k.split('/')[0] for k in names})!=9:
        raise RuntimeError('Frozen9patient23session cohort mismatch')
    return names


def make_pair(d,c,offset=None):
    if c['family'] in KINDS[1:]:
        dt = models.make_design(d['ytrain'],d['xtrain'],c['family'],5,d['ptrain'])
        dv = models.make_design(d['yval'],d['xval'],c['family'],5,d['pval'])
        return models.PoissonGLM(dt,d['ytrain']),models.PoissonGLM(dv,d['yval'])
    if offset is None:
        raise ValueError('Family models require the SAME frozen combined offset')
    ot,ov = offset
    if c['family']=='continuous':
        return (models.RecurrentPoisson(d['ytrain'],d['xtrain'],ot,c['size']),
                models.RecurrentPoisson(d['yval'],d['xval'],ov,c['size']))
    return (models.StatePoisson(d['ytrain'],ot,c['size'],c['lags']),
            models.StatePoisson(d['yval'],ov,c['size'],c['lags']))


def resolved(rows):
    if not rows or any(not r['converged'] for r in rows):
        raise RuntimeError('Cannot select a seed from incomplete/failed required seeds')
    required = [None] if rows[0]['config']['family']=='stationary' else SEEDS
    if [r['seed'] for r in rows]!=required:
        raise RuntimeError('Missing or reordered required seeds')
    return min(enumerate(rows),key=lambda pair:(pair[1]['loss'],pair[0]))[1]


def run_candidate(d,c,folder,offset=None,shared=0):
    rows = []
    stationary = c['family']=='stationary'
    train_model,val_model = None,None
    for seed in ([None] if stationary else SEEDS):
        row = {'session':d['key'],'subject':d['subject'],'config':c,'seed':seed,
               'real_data':True,'validation_trial_ids':d['validation_ids'],
               'feature_sha256':d['feature_sha256'],'shared_parameters':shared,
               'training_unit_bins':int(d['ytrain'].size),'validation_unit_bins':int(d['yval'].size)}
        try:
            if stationary:
                theta = models.fit_stationary(d['ytrain'])
                row.update(theta=theta.tolist(),converged=True,iterations=0,nfev=0,
                           loss=float(-models.poisson_logpmf(d['ytrain'],theta).mean()),
                           elapsed_seconds=0.,gradient_norm=0.,bound_hits=0,error=None,
                           message='Exact constant-rate maximum likelihood',status=0,
                           total_loglik=float(models.poisson_logpmf(d['ytrain'],theta).sum()))
                score = models.poisson_logpmf(d['yval'],theta).sum(axis=-1)
                parameters = len(theta)
            else:
                if train_model is None:
                    train_model,val_model = make_pair(d,c,offset)
                row.update(models.fit_model(train_model,c['ridge'],seed))
                parameters = train_model.n_parameters
                theta = np.asarray(row['theta'])
                score = val_model.score_bins(theta) if row['converged'] else None
                if score is not None and not np.isfinite(score).all():
                    raise FloatingPointError('Nonfinite validation score')
                if score is not None and c['family'] in ['discrete','hybrid']:
                    original = models.frozen.StatePoisson(val_model.y,val_model.offset,c['size'],c['lags'])
                    discrepancy = float(np.max(np.abs(score-original.score_bins(theta)))/val_model.y.shape[-1])
                    row['real_data_sequential_kernel_max_bin_discrepancy'] = discrepancy
                    if discrepancy>1e-10:
                        raise FloatingPointError('Real-data exact kernel parity threshold exceeded')
            row['extra_parameters'] = parameters
            row['total_parameters'] = parameters+shared
            if score is not None:
                trials = score.sum(axis=1)/(d['yval'].shape[1]*d['yval'].shape[2])
                row.update(trial_scores=trials.tolist(),validation_nats_per_unit_bin=float(trials.mean()))
            if not stationary:
                row['design_rank'] = (int(np.linalg.matrix_rank(train_model.design[:,:,0,:].reshape(-1,train_model.design.shape[-1])))
                                      if isinstance(train_model,models.PoissonGLM) else None)
        except Exception as exc:
            row.update(converged=False,error=f'{type(exc).__name__}: {exc}',message=str(exc))
        target = folder/d['key'].replace('/','_')/f'{configuration_id(c)}_seed{seed}.json'
        base.save(target,row,immutable=True)
        rows.append(row)
        print(f"FIT {d['key']} {c} seed={seed} converged={row['converged']} iterations={row.get('iterations')} error={row.get('error')}",flush=True)
        if not row['converged']:
            raise ScientificStop('Mandatory candidate/seed failure',row,relative(target))
    return resolved(rows)


class ScientificStop(RuntimeError):
    def __init__(self,reason,record=None,path=None):
        super().__init__(reason)
        self.record,self.path = record,path


def records(rows):
    return [{'subject':r['subject'],'session':r['session'],'trial_scores':r['trial_scores'],
             'trial_ids':r['validation_trial_ids']} for r in rows]


def selection(grid):
    candidates = []
    for c,rows in grid:
        complexity = stats.aggregate([{'subject':r['subject'],'session':r['session'],
                                      'trial_scores':[r['total_parameters']]} for r in rows])['mean']
        candidates.append({'config':c,'records':records(rows),'mean_parameters':complexity})
    return stats.choose_one_se(candidates)


def offset_pair(d,config,row):
    t,v = make_pair(d,config)
    theta = np.asarray(row['theta'])
    return (t.log_means(theta),v.log_means(theta)),t.n_parameters


def run_development(cohort):
    grid = []
    # Session-first progression exposes an entire frozen smoke grid before expansion.
    buckets = {configuration_id(c):[] for c in baseline_configs()}
    for d in cohort:
        for c in baseline_configs():
            buckets[configuration_id(c)].append(run_candidate(d,c,OUT/'fits/baselines'))
    grid = [(c,buckets[configuration_id(c)]) for c in baseline_configs()]
    combined = [(c,rows) for c,rows in grid if c['family']=='combined']
    offset_selection = selection(combined)
    oc,orows = combined[offset_selection['selected_index']]
    mean_scores = [stats.aggregate(records(rows))['mean'] for _,rows in grid]
    strongest = max(range(len(grid)),key=lambda i:(mean_scores[i],-stats.aggregate([
        {'subject':r['subject'],'session':r['session'],'trial_scores':[r['total_parameters']]} for r in grid[i][1]])['mean'],-i))
    base.save(OUT/'baseline_selection.json',{'combined_offset':offset_selection,
              'strongest_baseline':grid[strongest][0],
              'one_SE_baseline':selection(grid),
              'all_configurations':[{**c,**stats.aggregate(records(r))} for c,r in grid]},immutable=True)
    offsets = {d['key']:offset_pair(d,oc,row) for d,row in zip(cohort,orows)}
    fbuckets = {configuration_id(c):[] for c in family_configs()}
    for d in cohort:
        offset,shared = offsets[d['key']]
        for c in family_configs():
            fbuckets[configuration_id(c)].append(run_candidate(d,c,OUT/'fits/families',offset,shared))
    fgrid = [(c,fbuckets[configuration_id(c)]) for c in family_configs()]
    chosen = {}
    for family in ['discrete','continuous','hybrid']:
        subset = [(c,r) for c,r in fgrid if c['family']==family]
        sel = selection(subset)
        chosen[family] = {'selection':sel,'rows':subset[sel['selected_index']][1]}
    chosen['baseline'] = {'selection':{'selected_config':grid[strongest][0]},'rows':grid[strongest][1]}
    manifest = {'families':{f:v['selection'] for f,v in chosen.items()},
                'global_family_selection':selection(fgrid),'offset_config':oc,
                'freeze_utc':datetime.now(timezone.utc).isoformat(),
                'external_spikes_accessed':False,'final_locked':True,
                'development_inference':'Exploratory/postselection conditional, not confirmatory'}
    base.save(OUT/'model_selection_manifest.json',manifest,immutable=True)
    base.save(OUT/'selected_development_rows.json',chosen,immutable=True)
    return chosen,oc


def comparisons(chosen):
    means = {f:stats.aggregate(records(v['rows'])) for f,v in chosen.items()}
    pairs = [('discrete','continuous'),('discrete','hybrid'),('continuous','hybrid')]
    pairs += [(f,'baseline') for f in ['discrete','continuous','hybrid']]
    result = []
    for left,right in pairs:
        subjects = sorted(means[left]['patient_means'])
        differences = {s:means[left]['patient_means'][s]-means[right]['patient_means'][s] for s in subjects}
        result.append({'left':left,'right':right,'patient_differences':differences,
                       **stats.subject_statistics(list(differences.values()))})
    for row,p in zip(result,stats.holm([r['sign_flip']['p_value'] for r in result])):
        row['holm_p_value'] = float(p)
    return {'comparisons':result,'means':means,'postselection_exploratory':True}


def run_statistics_nulls(cohort,chosen,oc):
    base.save(OUT/'subject_statistics.json',comparisons(chosen),immutable=True)
    uncertainty = {f:[{'subject':r['subject'],'session':r['session'],
                       **stats.trial_ci(r['trial_scores'])} for r in v['rows']] for f,v in chosen.items()}
    patient_uncertainty = {f:{s:stats.patient_ci([r for r in records(v['rows']) if r['subject']==s])
                             for s in sorted({r['subject'] for r in v['rows']})} for f,v in chosen.items()}
    base.save(OUT/'conditional_uncertainty.json',{'sessions':uncertainty,'patients':patient_uncertainty},immutable=True)
    distribution = []
    for kind in ['bin_permutation','circular_shift','context_rotate']:
        for replicate in range(200):
            null_chosen = {f:{'rows':[]} for f in chosen}
            folder = OUT/'nulls'/kind/f'{replicate:03}'
            for d in cohort:
                nd = dict(d)
                audits = {}
                for split in ['train','val']:
                    yy,xx,audit = stats.transform_null(d['y'+split],d['x'+split],kind,replicate,
                                                       partition=f"{d['key']}/{split}")
                    nd['y'+split],nd['x'+split] = yy,xx
                    audits[split] = audit
                base.save(folder/d['key'].replace('/','_')/'count_audit.json',audits,immutable=True)
                orow = run_candidate(nd,oc,folder/'offset')
                offset,shared = offset_pair(nd,oc,orow)
                for family,v in chosen.items():
                    c = v['selection']['selected_config']
                    row = run_candidate(nd,c,folder/family, None if family=='baseline' else offset,
                                        0 if family=='baseline' else shared)
                    null_chosen[family]['rows'].append(row)
            result = comparisons(null_chosen)
            base.save(folder/'subject_results.json',result,immutable=True)
            distribution.append({'kind':kind,'replicate':replicate,'results':result})
    base.save(OUT/'null_distributions.json',distribution,immutable=True)
    observed = comparisons(chosen)
    tails = []
    for kind in ['bin_permutation','circular_shift','context_rotate']:
        for index in [3,4,5]:
            values = [r['results']['comparisons'][index]['mean'] for r in distribution if r['kind']==kind]
            gain = observed['comparisons'][index]['mean']
            tails.append({'kind':kind,'family':observed['comparisons'][index]['left'],
                          'observed_gain':gain,'null_gains':values,
                          'upper_tail_p':(1+sum(v>=gain for v in values))/201,
                          'multiplicity':'9 descriptive family/null comparisons; not physical validation'})
    base.save(OUT/'null_summary.json',tails,immutable=True)


def artifact_lock():
    base.save(OUT/'artifact_lock.json',{'sha256':{relative(p):base.digest(p) for p in OUT.rglob('*')
              if p.is_file() and p.name!='artifact_lock.json'}},immutable=True)


def execute():
    verify()
    if (OUT/'gate_result.json').exists() or (OUT/'execution_started.json').exists():
        raise RuntimeError('Execution already started; saved replay only. Never replace a failure or repeat final evaluation.')
    base.save(OUT/'execution_started.json',{'utc':datetime.now(timezone.utc).isoformat()},immutable=True)
    tests = subprocess.run([sys.executable,'-m','unittest','discover','-s',str(base.STUDY/'tests'),
                            '-p','test_r2*.py','-v'],capture_output=True,text=True)
    (OUT/'tests.log').write_text(tests.stdout+tests.stderr,encoding='utf-8')
    gate = {'study':'P11-v2','milestone':'R2','gate_verdict':'FAIL','scientific_verdict':'INCONCLUSIVE',
            'tests_exit_code':tests.returncode,'R2_A':'NOT_EXECUTED','R2_B':'NOT_EXECUTED',
            'R2_C':'NOT_EXECUTED','R3':'NOT_EXECUTED','oldtest_accessed':False,
            'external_spikes_accessed':False,'final_holdout_locked':True,'failures':[]}
    try:
        if tests.returncode:
            raise ScientificStop('Mandatory automated verification failed before real fitting')
        sys.path.insert(0,str(base.STUDY/'tests'))
        import test_r2
        oracle = test_r2.kernel_audit()
        base.save(OUT/'numerical_oracle.json',oracle,immutable=True)
        gate['numerical_oracle'] = oracle
        cohort = [data.session(key) for key in roster()]
        qc = [{k:v for k,v in d.items() if not isinstance(v,np.ndarray)} for d in cohort]
        for row,d in zip(qc,cohort):
            row.update(train_trials=len(d['ytrain']),validation_trials=len(d['yval']),
                       units=d['ytrain'].shape[-1],training_spikes=int(d['ytrain'].sum()),
                       validation_spikes=int(d['yval'].sum()))
        base.save(OUT/'input_QC.json',qc,immutable=True)
        gate.update(eligible_subjects=9,eligible_sessions=23,R2_A='RUNNING')
        chosen,oc = run_development(cohort)
        gate['R2_A']='PASS'
        gate['R2_B']='RUNNING'
        run_statistics_nulls(cohort,chosen,oc)
        gate['R2_B']='PASS'
        # No spontaneous external access: establish eligibility/coverage first.
        raise ScientificStop('Development passed; R2-C requires registered independent observation-support audit and sealed external accessor before any external spikes')
    except ScientificStop as exc:
        gate['failures'].append(str(exc))
        if exc.record is not None:
            gate['failed_candidate'],gate['failed_candidate_path'] = exc.record,exc.path
        for stage in ['R2_A','R2_B','R2_C']:
            if gate[stage]=='RUNNING':
                gate[stage]='FAIL'
    except Exception as exc:
        gate['failures'].append(f'Execution/input integrity: {type(exc).__name__}: {exc}')
        for stage in ['R2_A','R2_B','R2_C']:
            if gate[stage]=='RUNNING':
                gate[stage]='FAIL'
    verify()
    fits = [load(p) for p in (OUT/'fits').rglob('*.json')]
    gate.update(attempted_development_fits=len(fits),converged_development_fits=sum(r['converged'] for r in fits),
                mandatory_development_fits=23*169,
                unexecuted_development_fits=23*169-len(fits),
                fit_seconds=sum(r.get('elapsed_seconds',0.) for r in fits))
    base.save(OUT/'QC.json',gate,immutable=True)
    base.save(OUT/'gate_result.json',gate,immutable=True)
    with (OUT/'attempted_comparison.csv').open('w',encoding='utf-8',newline='') as stream:
        fields = ['subject','session','family','ridge','seed','total_parameters','converged',
                  'iterations','nfev','elapsed_seconds','validation_nats_per_unit_bin','error']
        writer = csv.DictWriter(stream,fieldnames=fields)
        writer.writeheader()
        for r in fits:
            writer.writerow({k:r.get(k,r.get('config',{}).get(k)) for k in fields})
    artifact_lock()
    print(json.dumps(gate,indent=2))
    return 1


def replay():
    verify()
    for rel,sha in load(OUT/'artifact_lock.json')['sha256'].items():
        if base.digest(base.ROOT/rel)!=sha:
            raise RuntimeError('Saved R2 output changed: '+rel)
    gate = load(OUT/'gate_result.json')
    for path in (OUT/'fits').rglob('*.json'):
        row = load(path)
        d = data.session(row['session'])
        if row['config']['family']=='stationary':
            theta = models.fit_stationary(d['ytrain'])
            score = models.poisson_logpmf(d['yval'],theta).mean()
        elif row['config']['family'] in KINDS:
            t,v = make_pair(d,row['config'])
            theta = np.asarray(row['theta'])
            if not row['converged']:
                continue
            objective,_ = t.objective(theta,row['config']['ridge'])
            if not np.isclose(objective,row['loss'],rtol=0,atol=1e-10):
                raise RuntimeError('Saved training objective not reproducible')
            score = v.score(theta)/v.y.size
        else:
            # Full successful family replay requires frozen offset reconstruction.
            if not row['converged']:
                continue
            oc = load(OUT/'baseline_selection.json')['combined_offset']['selected_config']
            files = sorted((OUT/'fits/baselines'/row['session'].replace('/','_')).glob(configuration_id(oc)+'_seed*.json'))
            candidates = sorted([load(p) for p in files],key=lambda r:SEEDS.index(r['seed']))
            offset,_ = offset_pair(d,oc,resolved(candidates))
            t,v = make_pair(d,row['config'],offset)
            score = v.score(np.asarray(row['theta']))/v.y.size
        if not np.isclose(score,row['validation_nats_per_unit_bin'],rtol=0,atol=1e-10):
            raise RuntimeError('Saved predictive score not reproducible')
    tests = subprocess.run([sys.executable,'-m','unittest','discover','-s',str(base.STUDY/'tests'),
                            '-p','test_r2*.py','-v'])
    if tests.returncode:
        return tests.returncode
    print('Saved-only replay verified; no refitting, no holdout unlock. Scientific gate='+gate['gate_verdict'])
    return 0


if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('action',choices=['register','execute','verify','replay'])
    action = parser.parse_args().action
    if action=='register':
        register()
    elif action=='execute':
        sys.exit(execute())
    elif action=='replay':
        sys.exit(replay())
    else:
        verify()
        print('R2 sources, preceding gates, archived evidence and split hashes verified.')
