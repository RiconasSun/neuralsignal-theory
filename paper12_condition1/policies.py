"""Three fixed policies, original objective under exact diagonal coordinates."""
import numpy as np
from scipy.optimize import minimize,Bounds,BFGS

class BudgetExhausted(RuntimeError):pass
class NumericalFailure(RuntimeError):pass

class Coordinates:
    def __init__(self,scale):
        self.scale=np.asarray(scale,dtype=float)
        if not np.isfinite(self.scale).all() or np.any(self.scale<=0):raise ValueError('POSITIVE_FINITE_SCALE')
    def forward(self,z):
        t=self.scale*z
        # Canonical physical endpoints avoid one-ulp outward bound rounding.
        return np.where(z==self.bounds[:,0],-8.,np.where(z==self.bounds[:,1],8.,t))
    def inverse(self,theta):return theta/self.scale
    def gradient(self,g):return self.scale*g
    @property
    def bounds(self):return np.column_stack((-8/self.scale,8/self.scale))
    def project(self,z):return np.clip(z,self.bounds[:,0],self.bounds[:,1])

def physical_pg(theta,g):
    p=g.copy();p[(theta<=-8)&(g>0)]=0;p[(theta>=8)&(g<0)]=0
    return float(np.abs(p).max())

def adam_step(z,g,m,v,step,rate,beta1=.9,beta2=.999,eps=1e-8):
    m=beta1*m+(1-beta1)*g;v=beta2*v+(1-beta2)*g*g
    return z-rate*(m/(1-beta1**step))/(np.sqrt(v/(1-beta2**step))+eps),m,v

def run(policy,theta,scale,objective,progress=None):
    coordinates=Coordinates(scale);current=coordinates.inverse(theta);calls=[];accepted=[];warnings=[];cache=None;latest=current.copy();latest_info=None
    def evaluate(z):
        nonlocal cache,latest_info
        if len(calls)>=policy['objective_gradient_call_cap']:raise BudgetExhausted('HARD_OBJECTIVE_GRADIENT_CALL_CAP')
        t=coordinates.forward(z)
        if np.any(t < -8-1e-12) or np.any(t > 8+1e-12):raise NumericalFailure('PHYSICAL_BOUNDS_VIOLATION')
        try:value,g=objective(t)
        except Exception as error:
            calls.append({'call':len(calls)+1,'objective':None,'PG':None,'gradient_inf':None,'finite':False,'objective_exception_type':type(error).__name__,'objective_exception_message':str(error)})
            raise NumericalFailure('OBJECTIVE_EXCEPTION:'+type(error).__name__+':'+str(error)) from error
        finite=bool(np.isfinite(value) and np.isfinite(g).all())
        entry={'call':len(calls)+1,'objective':float(value) if np.isfinite(value) else None,'PG':physical_pg(t,g) if finite else None,'gradient_inf':float(np.abs(g).max()) if finite else None,'finite':finite}
        calls.append(entry)
        if not finite:raise NumericalFailure('NONFINITE_OBJECTIVE_OR_GRADIENT')
        cache=(z.copy(),float(value),g.copy());latest_info=entry
        return float(value),coordinates.gradient(g)
    def record(z,phase):
        nonlocal latest
        if cache is None or not np.array_equal(cache[0],z):evaluate(z)
        latest=z.copy();value,g=cache[1:];entry={'accepted':len(accepted)+1,'phase':phase,'objective':value,'PG':physical_pg(coordinates.forward(z),g),'call_count':len(calls)}
        accepted.append(entry)
        if progress and len(accepted)%50==0:progress(entry)
    status='NOT_STARTED';success=False;message='';nit=0;solver=None;captured=[]
    import warnings as warning_module
    try:
        with warning_module.catch_warnings(record=True) as captured:
            warning_module.simplefilter('always')
            if policy['kind']=='adam_lbfgsb':
                m=np.zeros_like(current);v=m.copy()
                for k in range(1,policy['warm_steps']+1):
                    _,g=evaluate(current);rate=next(rate for end,rate in policy['warm_schedule'] if k<=end)
                    current,m,v=adam_step(current,g,m,v,k,rate,policy['beta1'],policy['beta2'],policy['epsilon']);current=coordinates.project(current);record(current,'warm')
            def callback(z,*args):
                record(z,'trust_region' if policy['kind']=='trust_constr' else 'lbfgsb')
                return False
            arguments=dict(fun=evaluate,x0=current,jac=True,callback=callback,options=policy['options'])
            if policy['kind']=='trust_constr':
                solver=minimize(method='trust-constr',bounds=Bounds(coordinates.bounds[:,0],coordinates.bounds[:,1],keep_feasible=True),hess=BFGS(exception_strategy='skip_update',min_curvature=1e-8,init_scale='auto'),**arguments)
            else:solver=minimize(method='L-BFGS-B',bounds=coordinates.bounds,**arguments)
            current=solver.x.copy();latest=current.copy();success=bool(solver.success);nit=int(solver.nit);status=str(solver.status);message=str(solver.message)
    except (BudgetExhausted,NumericalFailure) as error:
        status=type(error).__name__;message=str(error);current=latest.copy();warnings.append(message)
    except Exception as error:
        status='OptimizerException:'+type(error).__name__;message=str(error);current=latest.copy();warnings.append(message)
    finally:
        warnings.extend(str(w.message) for w in captured)
    # No hidden best-value selection; use final accepted/solver state.
    return {'theta':coordinates.forward(current),'calls':calls,'accepted':accepted,'solver_success':success,'solver_status':status,'solver_message':message,'solver_iterations':nit if solver else None,'solver_nfev':int(solver.nfev) if solver else None,'warnings':warnings,'call_count':len(calls),'accepted_count':len(accepted),'warm_accepted':sum(z['phase']=='warm' for z in accepted),'endpoint_selection':'solver_final_or_last_accepted_on_declared_abort','coordinate_roundtrip_abs_max':float(np.abs(coordinates.forward(coordinates.inverse(coordinates.forward(current)))-coordinates.forward(current)).max())}
