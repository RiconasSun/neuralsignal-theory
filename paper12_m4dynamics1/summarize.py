import csv
import study as r
from controls import completed

def main():
    phases=[p for p in ('diagnosis','smoke') if (r.HERE/f'results/{p}_launch_receipt.json').exists()]
    reports={}
    for phase in phases:
        bindings=completed(phase,False);summary=r.load(r.HERE/f'results/{phase}/native/summary.json');rows=summary['rows'];gate=r.load(r.HERE/f'results/{phase}/native/gate_result.json')
        families={}
        for family in ('Discrete','Continuous','Hybrid'):
            selected=[z for z in rows if z['family']==family]
            if not selected:continue
            families[family]=dict(fits=len(selected),converged=sum(z['converged'] for z in selected),
                projected_gradient_min=min(z['projected_gradient'] for z in selected),projected_gradient_max=max(z['projected_gradient'] for z in selected),
                max_initial_gradient_error=max(z['initial_gradient_check']['scaled_gradient_error'] for z in selected),
                max_terminal_gradient_error=max(z['terminal_gradient_check']['scaled_gradient_error'] for z in selected),
                max_independent_objective_error=max(max(z[c]['independent_objective_error'] for c in ('initial_gradient_check','terminal_gradient_check')) for z in selected),
                relative_objective_terminations=sum('RELATIVE REDUCTION' in z['optimizer_message'] for z in selected),
                active_bound_fits=sum(z['bound_hits']>0 for z in selected),max_iterations=max(z['iterations'] for z in selected),max_calls=max(z['objective_calls'] for z in selected),
                replay_matches=sum(z.get('original_replay_match',False) for z in selected))
        reports[phase]=dict(gate=gate,bindings=bindings,families=families)
        columns=['mouse_id','session_id','region','family','size','ridge','seed','converged','optimizer_message','iterations','objective_calls','projected_gradient','gradient_inf','bound_hits','parameter_count','elapsed_seconds']
        with (r.HERE/f'{phase}_216_fit_table.csv').open('x',encoding='utf-8',newline='') as f:
            writer=csv.DictWriter(f,fieldnames=columns,extrasaction='ignore');writer.writeheader();writer.writerows(rows)
    r.save(r.HERE/'results/family_diagnostics.json',reports)
    print(r.json.dumps({p:d['families'] for p,d in reports.items()},indent=2))

if __name__=='__main__':main()
