"""Summarize completed saved gates only; no model, data or selection access."""
from datetime import datetime,timezone
import study as r
from reproduce_saved import table


def rows(phase):
    values=[]
    for p in sorted((r.HERE/'results'/phase).glob('*.json')):
        x=r.load(p)
        if 'kind' in x:values.append(x)
    return values


def main():
    r.verify();diagnosis=r.load(r.HERE/'results/diagnosis_audit.json')
    stages={}
    for phase in ('smoke','full'):
        path=r.HERE/'results'/phase/'gate_result.json'
        local=rows(phase)
        if path.exists():
            gate=r.load(path)
            stages[phase]=dict(gate=gate,fit_count=len(local),converged=sum(x['converged'] for x in local),
                maximum_projected_gradient=max((x['projected_gradient'] for x in local),default=None),
                failed=[{k:x.get(k) for k in ('session_id','region','kind','ridge','seed','optimizer_message','iterations','objective_calls','projected_gradient')} for x in local if not x['converged']],
                input_preflight_sha256=r.sha(r.HERE/('results/'+phase+'_preflight.json')),
                gate_sha256=r.sha(path),launch_receipt=r.load(r.HERE/('results/'+phase+'_launch_receipt.json')))
        else:stages[phase]=dict(gate='NOT_EXECUTED',fit_count=len(local))
    m4=r.HERE/'results/M4/native/gate_result.json'
    if m4.exists():stages['M4']=r.load(m4)
    elif (r.HERE/'results/M4/numerical_gate.json').exists():stages['M4']=r.load(r.HERE/'results/M4/numerical_gate.json')
    else:stages['M4']=dict(gate='NOT_EXECUTED')
    r.save(r.HERE/'results/result_summary.json',dict(utc=datetime.now(timezone.utc).isoformat(),diagnosis=diagnosis,
        stages=stages,final_evaluation_access=False,source_requests=0,historical_gates_reclassified=False))
    (r.HERE/'results/fit_diagnostics.csv').write_text(table(),encoding='utf-8',newline='')
    print({p:stages[p].get('fit_count',stages[p].get('gate')) for p in stages})


if __name__=='__main__':main()
