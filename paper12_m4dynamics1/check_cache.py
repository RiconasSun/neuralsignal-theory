"""Synthetic-only exact equivalence and cost check; no protected inputs."""
import importlib.util
import sys
import time
import numpy as np
import study as r

def main():
    r.save(r.HERE/'cache_registration.json',dict(utc=r.datetime.now(r.timezone.utc).isoformat(),before_testing=True,
        rationale='Independent oracle factorial evaluation dominates replay cost; constant integer factorial cache only, no optimizer or model change',
        sha256={n:r.sha(r.HERE/n) for n in ('oracle.py','oracle_cached.py','check_cache.py')},
        criteria='Exactly equal integer-factorial/PMF values for counts 0..10000; exact fixture likelihoods and identical independent oracle bytecode; all original checks retained',
        scope='Only a future prospectively registered phase; active original-budget replay source unchanged'))
    sys.path.insert(0,str(r.PREVIOUS))
    spec=importlib.util.spec_from_file_location('oracle_original',r.HERE/'oracle.py');old=importlib.util.module_from_spec(spec);sys.modules['oracle_original']=old;spec.loader.exec_module(old)
    import oracle_cached as fast
    y=np.arange(10001,dtype=float);eta=np.full_like(y,-.3)
    assert np.array_equal(old.pmf(y,eta),fast.pmf(y,eta))
    rows=[]
    for f,k,ridge,seed,m,theta in old.synthetic_cases():
        x=m.x if f=='Continuous' else np.empty(m.y.shape[:2]+(0,))
        original=old.scalar_ll(theta,f,m.y,x,m.offset,k)
        cached=fast.scalar_ll(theta,f,m.y,x,m.offset,k)
        assert original==cached
        rows.append(dict(family=f,size=k,ridge=ridge,seed=seed,error=abs(original-cached)))
    for name in ('state_parts','scalar_ll','scalar_objective','check_gradient'):
        assert getattr(fast,name).__code__ is getattr(old,name).__code__
    values=np.random.default_rng(20261013).poisson(.7,(360,20,4,32)).astype(float);eta=np.zeros_like(values)
    start=time.perf_counter();a=old.pmf(values,eta);oldtime=time.perf_counter()-start
    start=time.perf_counter();b=fast.pmf(values,eta);newtime=time.perf_counter()-start
    assert np.array_equal(a,b)
    r.save(r.HERE/'results/cache_equivalence.json',dict(gate='PASS',integer_cases=10001,likelihood_cases=rows,
        bytecode_identity=True,exact_PMF=True,original_seconds=oldtime,cached_seconds=newtime,synthetic_only=True,active_replay_changed=False))
    print('EXACT_CACHE_EQUIVALENCE_PASS',oldtime,newtime)

if __name__=='__main__':main()
