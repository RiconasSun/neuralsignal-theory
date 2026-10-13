"""Development descriptive means only; no selection, inference or data access."""
import csv
import io
import math
from collections import defaultdict
import study as r


def render(phase):
    groups=defaultdict(list)
    for p in (r.HERE/'results'/phase).glob('*.json'):
        x=r.load(p)
        if x.get('family')=='baseline':groups[(x['mouse_id'],x['session_id'],x['region'],x['kind'],x['ridge'])].append(x)
    rows=[]
    for key,values in sorted(groups.items(),key=lambda x:str(x[0])):
        complete=len(values)==3 and {x['seed'] for x in values}=={11,23,37}
        allconv=complete and all(x['converged'] for x in values)
        rows.append(dict(zip(('mouse_id','session_id','region','kind','ridge'),key),
            seeds_recorded=len(values),all_three_seeds_converged=allconv,
            training_LL_nats_per_unit_bin=sum(x['training_LL_nats_per_unit_bin'] for x in values)/len(values),
            development_validation_LL_nats_per_unit_bin=sum(x['validation_LL_nats_per_unit_bin'] for x in values)/len(values),
            parameter_count=values[0]['parameter_count'],maximum_projected_gradient=max(x['projected_gradient'] for x in values)))
    return rows


def main():
    from closure_verify import verify
    verify()
    phase='full' if (r.HERE/'results/full/gate_result.json').exists() else 'smoke'
    rows=render(phase)
    path=r.HERE/'results/baseline_comparison.csv'
    if not rows:raise RuntimeError('NO_RECORDED_BASELINES')
    with path.open('w',encoding='utf-8',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');writer.writeheader();writer.writerows(rows)
    r.save(r.HERE/'results/baseline_table_scope.json',dict(phase=phase,rows=len(rows),
        independent_mouse_count=len({x['mouse_id'] for x in rows}),
        descriptive_development_only=True,seed_means_not_independent_subjects=True,
        significance_tests_executed=False,final_validation=False))
    print('DESCRIPTIVE_BASELINE_TABLE',phase,len(rows))


def csv_text(phase='full'):
    rows=render(phase)
    if not rows:raise RuntimeError('NO_RECORDED_BASELINES')
    stream=io.StringIO(newline='')
    writer=csv.DictWriter(stream,fieldnames=list(rows[0]),lineterminator='\n')
    writer.writeheader();writer.writerows(rows)
    return stream.getvalue()


if __name__=='__main__':main()
