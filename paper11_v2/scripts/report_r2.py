"""Render saved R2 evidence only; no new fits, tests, nulls or holdout access."""
import argparse
import csv
from datetime import datetime, timezone

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import run_r2 as run

OUT = run.base.STUDY/'results/R2_report'


def register():
    run.verify()
    target = OUT/'registration.json'
    if not target.exists():
        run.base.save(target,{'registered_utc':datetime.now(timezone.utc).isoformat(),
            'source_sha256':run.base.digest(__file__),
            'R2_registration_sha256':run.base.digest(run.OUT/'registration.json'),
            'scope':'Saved descriptive receipts/tables only; no new scientific fitting/inference/selection',
            'partial_models_never_ranked':True},immutable=True)


def write_csv(path,fields,rows):
    with path.open('w',encoding='utf-8',newline='') as stream:
        writer = csv.DictWriter(stream,fieldnames=fields,extrasaction='ignore')
        writer.writeheader(); writer.writerows(rows)


def report():
    run.verify()
    reg = run.load(OUT/'registration.json')
    if run.base.digest(__file__)!=reg['source_sha256']:
        raise RuntimeError('Report source changed')
    for rel,sha in run.load(run.OUT/'artifact_lock.json')['sha256'].items():
        if run.base.digest(run.base.ROOT/rel)!=sha:
            raise RuntimeError('Report prohibited: saved R2 evidence changed')
    if (OUT/'artifact_lock.json').exists():
        for rel,sha in run.load(OUT/'artifact_lock.json')['sha256'].items():
            if run.base.digest(run.base.ROOT/rel)!=sha:
                raise RuntimeError('Saved report changed')
        print('Saved report verified without regeneration.')
        return
    gate = run.load(run.OUT/'gate_result.json')
    fits = [run.load(p) for p in (run.OUT/'fits').rglob('*.json')]
    sessions = run.roster()
    summary = []
    for key in sessions:
        for family in run.KINDS+['discrete','continuous','hybrid']:
            rows = [r for r in fits if r['session']==key and r['config']['family']==family]
            expected = (1 if family=='stationary' else 12 if family in run.KINDS else
                        24 if family=='discrete' else 36 if family=='continuous' else 48)
            summary.append({'subject':key.split('/')[0],'session':key,'family':family,
                            'expected':expected,'attempted':len(rows),'converged':sum(r['converged'] for r in rows),
                            'failed':sum(not r['converged'] for r in rows),'not_executed':expected-len(rows),
                            'optimizer_seconds':sum(r.get('elapsed_seconds',0.) for r in rows),
                            'one_iteration_stops':sum(r.get('iterations')==1 for r in rows),
                            'gradient_above_gtol_successes':sum(r['converged'] and r.get('gradient_norm',0)>1e-5 for r in rows)})
    write_csv(OUT/'convergence_coverage.csv',list(summary[0]),summary)
    input_qc = run.load(run.OUT/'input_QC.json') if (run.OUT/'input_QC.json').exists() else []
    write_csv(OUT/'subject_session_coverage.csv',['subject','key','units','train_trials','validation_trials',
              'training_spikes','validation_spikes','feature_sha256','event_metadata_sha256'],input_qc)
    if (run.OUT/'baseline_selection.json').exists():
        selection = run.load(run.OUT/'baseline_selection.json')
        configs = selection['all_configurations']
        table,patients = [],[]
        for c in configs:
            matching = [r for r in fits if r['config']['family']==c['family'] and r['config']['ridge']==c['ridge']]
            resolved = []
            for key in sessions:
                seeds = [r for r in matching if r['session']==key]
                seeds.sort(key=lambda r: -1 if r['seed'] is None else run.SEEDS.index(r['seed']))
                resolved.append(run.resolved(seeds))
            complexity = run.stats.aggregate([{'subject':r['subject'],'session':r['session'],
                                              'trial_scores':[r['total_parameters']]} for r in resolved])['mean']
            table.append({'family':c['family'],'ridge':c['ridge'],'dev_nats_unit_bin':c['mean'],
                          'patient_count':c['subject_count'],'session_count':len(sessions),
                          'patient_weighted_mean_parameters':complexity,
                          'strongest_baseline':c['family']==selection['strongest_baseline']['family'] and c['ridge']==selection['strongest_baseline']['ridge']})
            for subject,score in c['patient_means'].items():
                patients.append({'subject':subject,'family':c['family'],'ridge':c['ridge'],'dev_nats_unit_bin':score})
        write_csv(OUT/'baseline_comparison.csv',list(table[0]),table)
        write_csv(OUT/'baseline_subject_scores.csv',list(patients[0]),patients)
        fig,ax = plt.subplots(figsize=(10,7),layout='constrained')
        colors = ['#151515','#007C91','#9C4A7D','#427E31','#BB5A29','#315EB0']
        for i,row in enumerate(table):
            ax.scatter(row['dev_nats_unit_bin'],i,color=colors[run.KINDS.index(row['family'])],s=35)
        ax.set_yticks(range(len(table)),[f"{r['family']} / ridge {r['ridge']:g}" for r in table])
        ax.invert_yaxis(); ax.grid(axis='x',alpha=.25)
        ax.set_xlabel('Development predictive log likelihood (nats/unit-bin)')
        ax.set_title('Complete baseline grid: equal-session then equal-patient means\nExploratory development; not a dynamical-family verdict',fontsize=12)
        fig.savefig(OUT/'baseline_comparison.png',dpi=160); plt.close(fig)
    else:
        table = []
    failures = [r for r in fits if not r['converged']]
    diagnostic = {'scientific_gate':gate['gate_verdict'],'scientific_verdict':gate['scientific_verdict'],
                  'attempted':len(fits),'converged':sum(r['converged'] for r in fits),'failed':failures,
                  'not_executed':23*169-len(fits),'no_new_fits_or_inference':True,
                  'design_rank_disclosure':'Original design_rank is rank of the first unit design only, not the joint design. Comparisons use nominal total free coefficients, including shared offsets.',
                  'optimizer_disclosure':'L-BFGS-B success can be ftol rather than gtol; one-iteration stops and residual gradients disclosed. Neither is global-optimum evidence.',
                  'no_regime_preference_from_partial_grid':True,'oldtest_and_external_locked':True}
    run.base.save(OUT/'diagnostics.json',diagnostic,immutable=True)
    fig,ax = plt.subplots(figsize=(10,6),layout='constrained')
    families = run.KINDS+['discrete','continuous','hybrid']
    attempted = [sum(r['attempted'] for r in summary if r['family']==f) for f in families]
    expected = [sum(r['expected'] for r in summary if r['family']==f) for f in families]
    ax.barh(families,expected,color='#DDDDDD',label='Frozen required runs')
    ax.barh(families,attempted,color='#007C91',label='Attempted (including failures)')
    ax.set_xlabel('Candidate/initialization fits'); ax.set_title('Execution coverage, not model performance',fontsize=12)
    ax.invert_yaxis(); ax.legend(); fig.savefig(OUT/'execution_coverage.png',dpi=160); plt.close(fig)
    run.base.save(OUT/'artifact_lock.json',{'sha256':{run.relative(p):run.base.digest(p)
                   for p in OUT.iterdir() if p.is_file()}},immutable=True)
    print(diagnostic)


if __name__=='__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('action',choices=['register','report'])
    action = parser.parse_args().action
    register() if action=='register' else report()
