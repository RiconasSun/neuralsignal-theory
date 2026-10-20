"""External FG/iteration broker and frozen checkpoint AD/FD certificates."""
import json,math,os,subprocess,sys
from pathlib import Path
import numpy as np
from .core import R,P,once,event,arrays,sha,guard,require_job,BudgetStop,NumericalStop,ImplementationStop,spec,NUMERIC

class Counter:
    def __init__(self):self.calls=0;self.iterations=0
    def value_gradient(self):
        if self.calls>=6000 or self.iterations>=1500:raise BudgetStop('External broker denies before unauthorized FG or next iteration')
        self.calls+=1
    def accepted(self):
        if self.iterations>=1500:raise BudgetStop('External accepted-iteration cap')
        self.iterations+=1

def finite(value,gradient):
    if not np.isfinite(value) or not np.isfinite(gradient).all():raise NumericalStop('Nonfinite identical objective/gradient')

def certificate(objective,points,folder,stage):
    p=len(objective.x0);rows=[];saved={};fd_calls=ad_calls=analytic_calls=0
    for name,x in zip(['initial','halfway','endpoint'],points):
        guard(stage);value,g=objective.analytic(x);analytic_calls+=1;finite(value,g)
        advalue,ad=objective.AD(x);ad_calls+=1;finite(advalue,ad)
        error=np.abs(g-ad)/np.maximum(1,np.maximum(np.abs(g),np.abs(ad)))
        fd_errors={};saved[name+'_x']=x;saved[name+'_analytic']=g;saved[name+'_AD']=ad;saved[name+'_AD_error']=error
        for h in NUMERIC['FD_steps']:
            derivative=np.empty(p)
            for k in range(p):
                guard(stage)
                if fd_calls+2>24*p:raise BudgetStop('Fixed diagnostic objective-call cap')
                plus=x.copy();minus=x.copy();plus[k]+=h;minus[k]-=h
                a=objective.analytic(plus)[0];b=objective.analytic(minus)[0];fd_calls+=2
                if not np.isfinite(a+b):raise NumericalStop('Nonfinite fixed FD extension')
                derivative[k]=(a-b)/(2*h)
            delta=np.abs(derivative-g)/np.maximum(1,np.maximum(np.abs(derivative),np.abs(g)))
            fd_errors[str(h)]=float(delta.max());saved[name+'_FD_'+str(h)]=derivative
            saved[name+'_FD_error_'+str(h)]=delta
        row={'checkpoint':name,'objective':float(value),'AD_objective':float(advalue),
            'AD_scaled_coordinate_error_max':float(error.max()),'FD_scaled_coordinate_errors':fd_errors,
            'frozen_FD_scaled_error':fd_errors[str(NUMERIC['FD_frozen_acceptance_step'])]}
        row['pass']=bool(np.isclose(value,advalue,atol=1e-10,rtol=1e-12) and error.max()<=1e-8 and row['frozen_FD_scaled_error']<=2e-5)
        rows.append(row)
    receipt=arrays(Path(folder)/'coordinate_certificates.npz',**saved)
    report={'checkpoints':rows,'free_coordinates':p,'FD_objective_calls':fd_calls,'AD_calls':ad_calls,
        'analytic_checkpoint_calls':analytic_calls,'coordinate_state':receipt,'all_checkpoints_pass':all(r['pass'] for r in rows),
        'FD_step_not_selected_post_result':True,'central_smooth_extension_not_optimizer_feasibility':True}
    once(Path(folder)/'DIAGNOSTICS.json',report)
    return report

def fit(objective,folder,stage,task):
    require_job(os.environ['P16_R2_JOB']);guard(stage)
    folder=Path(folder);folder.mkdir(parents=True,exist_ok=False)
    once(folder/'ATTEMPT.json',{'task':task,'no_retry':True,'parameters':len(objective.x0),
        'bounds':arrays(folder/'initial.npz',x0=objective.x0,lo=objective.lo,hi=objective.hi)})
    config=folder/'CLIENT.json';once(config,{'x0':objective.x0.tolist(),'lo':objective.lo.tolist(),'hi':objective.hi.tolist()})
    counter=Counter();accepted=[];result=None;error=None;proc=None
    try:
        with (folder/'CLIENT_STDERR.log').open('xb') as stderr:
            proc=subprocess.Popen([sys.executable,'-B','-m','paper16_development_r2.optim_child',str(config)],
                cwd=R,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=stderr,text=True,encoding='utf8',bufsize=1)
            while True:
                line=proc.stdout.readline()
                if not line:raise ImplementationStop('Optimizer client ended without full termination receipt')
                guard(stage);message=json.loads(line);op=message['op'];x=np.asarray(message['x'],dtype=float)
                if x.shape!=objective.x0.shape or not np.isfinite(x).all():raise NumericalStop('Optimizer vector integrity')
                if np.any(x<objective.lo-1e-12) or np.any(x>objective.hi+1e-12):raise NumericalStop('Optimizer bounds')
                if op=='FG':
                    counter.value_gradient()
                    event(folder/'CALLS.jsonl',event='RESERVED_BEFORE_EVALUATION',call=counter.calls,iterations=counter.iterations)
                    value,g=objective.analytic(x);finite(value,g)
                    event(folder/'CALLS.jsonl',event='COMPLETED',call=counter.calls,objective=float(value),gradient_inf=float(np.abs(g).max()))
                    reply={'allowed':True,'value':value,'gradient':g.tolist()}
                elif op=='ITER':
                    counter.accepted();accepted.append(x.copy())
                    event(folder/'ACCEPTED.jsonl',iteration=counter.iterations,x=x.tolist())
                    reply={'allowed':True}
                elif op=='DONE':result=message;break
                else:raise ImplementationStop('Unknown broker operation')
                proc.stdin.write(json.dumps(reply)+'\n');proc.stdin.flush()
            code=proc.wait(timeout=30)
            if code!=0:raise ImplementationStop('Optimizer client nonzero exit')
        if result['nfev']!=counter.calls or result['nit']!=counter.iterations:raise ImplementationStop('External/client counters disagree')
        endpoint=np.asarray(result['x']);gradient=np.asarray(result['jac'])
        # The SciPy-reported endpoint is one of the externally supplied FG pairs.
        # Recomputations are the three explicitly counted certificate checkpoints.
        midpoint=accepted[max(0,math.ceil(len(accepted)/2)-1)] if accepted else endpoint.copy()
        diagnostics=certificate(objective,[objective.x0.copy(),midpoint,endpoint],folder,stage)
        with np.load(folder/'coordinate_certificates.npz',allow_pickle=False) as saved:checked=saved['endpoint_analytic'].copy()
        if not np.allclose(checked,gradient,atol=1e-12,rtol=1e-12) or not np.isclose(result['fun'],diagnostics['checkpoints'][-1]['objective'],atol=1e-10,rtol=1e-12):raise ImplementationStop('Optimizer endpoint differs from identical-objective checkpoint')
        gradient=checked;pg=float(np.abs(spec.projected_gradient(endpoint,gradient,objective.lo,objective.hi)).max())
        passed=bool(pg<=1e-5 and diagnostics['all_checkpoints_pass'])
        report={**result,'task':task,'objective':result['fun'],'projected_gradient_inf':pg,
            'external_value_gradient_pairs':counter.calls,'external_accepted_iterations':counter.iterations,
            'accepted_vector_count':len(accepted),'halfway_accepted_iteration':math.ceil(len(accepted)/2),
            'numerical_pass':passed,'diagnostic_state_sha256':sha(folder/'DIAGNOSTICS.json'),
            'endpoint_state':arrays(folder/'endpoint.npz',x=endpoint,gradient=gradient),
            'success_flag_is_not_gate':True}
        once(folder/'RESULT.json',report)
        if not passed:raise NumericalStop('Mandatory original PG/AD/frozen-FD gate failed')
        return endpoint,report
    except BaseException as exc:
        error=exc
        once(folder/'FAILURE.json',{'task':task,'type':type(exc).__name__,'message':str(exc),
            'value_gradient_pairs':counter.calls,'accepted_iterations':counter.iterations,'retry_authorized':False})
        raise
    finally:
        if proc is not None and proc.poll() is None:
            proc.kill();proc.wait()
        if proc is not None:
            for stream in [proc.stdin,proc.stdout]:
                if stream is not None:stream.close()
