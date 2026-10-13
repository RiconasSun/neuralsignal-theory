"""Saved real smoke outputs only; no new fitting or scientific remediation."""
import csv
from collections import Counter
import study as r


def main():
    root=r.HERE/'results/M3/progressive1'
    gate=r.load(root/'gate_result.json')
    rows=[];fingerprints={}
    for path in sorted(root.glob('*.json')):
        value=r.load(path)
        if value.get('family')=='baseline':rows.append(value);fingerprints[path.name]=r.sha(path)
    if len(rows)!=126 or len({x['mouse_id'] for x in rows})!=1 or len({x['session_id'] for x in rows})!=1:
        raise RuntimeError('SMOKE_FIT_DENOMINATOR_INVALID')
    required={(roi,kind,ridge,seed) for roi in ('CA1','DG') for kind in ('stationary','history','population','event','drift','combined')
              for ridge in ([None] if kind=='stationary' else [.001,.01,.1,1.]) for seed in (11,23,37)}
    if {(x['region'],x['kind'],x['ridge'],x['seed']) for x in rows}!=required:raise RuntimeError('SMOKE_CONFIG_SEED_DENOMINATOR_INVALID')
    failures=[x for x in rows if not x['converged']]
    summary=dict(gate=gate['gate'],scientific_verdict=gate['scientific_verdict'],stage='smoke',mouse_count=1,
        enrolled_development_mice=13,completed_fit_count=len(rows),planned_full_development_fit_count=13*126,
        converged_fit_count=len(rows)-len(failures),failed_fit_count=len(failures),
        optimizer_success_count=sum(x.get('optimizer_success',False) for x in rows),
        minimum_failed_projected_gradient=min(x['projected_gradient'] for x in failures),
        maximum_failed_projected_gradient=max(x['projected_gradient'] for x in failures),
        frozen_projected_gradient_threshold=.001,
        failed_optimizer_messages=dict(Counter(x['optimizer_message'] for x in failures)),
        failure_reason=gate['reason'],eligible_ridges=gate['eligible_ridges'],
        full_development_evaluation_completed=False,subject_level_statistics_executed=False,
        M4_executed=False,M5_executed=False,mandatory_nulls_executed=False,
        final_evaluation_exposed_to_analysis=False,final_holdout_evaluated=False,
        analysis_visible_neural_data='Development A/B only, first enrolled mouse scored; authorized export roster13mice',
        gate_sha256=r.sha(root/'gate_result.json'),all_fit_files_sha256=fingerprints)
    r.save(r.HERE/'results/M3/smoke_failure_summary.json',summary)
    table=[]
    for row in rows:
        table.append({k:row.get(k) for k in ('mouse_id','session_id','region','kind','ridge','seed','converged','optimizer_success',
             'projected_gradient','iterations','objective_calls','parameter_count','training_unit_bins','validation_unit_bins',
             'training_LL_nats_per_unit_bin','validation_LL_nats_per_unit_bin','bound_hits','elapsed_seconds','optimizer_message')})
    with (r.HERE/'results/M3/baseline_smoke_comparison.csv').open('w',encoding='utf-8',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(table[0]));writer.writeheader();writer.writerows(table)
    print({k:v for k,v in summary.items() if k not in ('all_fit_files_sha256','eligible_ridges')})


if __name__=='__main__':main()
