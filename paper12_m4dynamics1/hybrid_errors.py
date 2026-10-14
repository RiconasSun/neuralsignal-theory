import sys
import study as r

def main():
    r.save(r.HERE/'hybrid_errors_registration.json',dict(utc=r.datetime.now(r.timezone.utc).isoformat(),before_testing=True,
        sha256={n:r.sha(r.HERE/n) for n in ('hybrid_errors.py','test_hybrid_history.py','oracle.py')},synthetic_only=True))
    sys.path.insert(0,str(r.PREVIOUS))
    import numpy as np
    from model_math import make
    from oracle import check_gradient,scalar_ll
    y=np.array([[[1,2],[0,1],[2,0],[1,1],[0,2],[2,1]],[[2,1],[1,0],[0,2],[2,2],[1,0],[0,1]]],dtype=float)
    x=np.zeros((2,6,3));offset=np.full(y.shape,-.3);rows=[]
    for size in (2,3,4):
        for ridge in (.001,.01,.1,1.):
            for seed in (11,23,37):
                m=make('Hybrid',y,x,offset,size);theta=m.initial(seed)
                z=check_gradient(theta,m,ridge,'Hybrid',size,range(len(theta)))
                error=abs(m.score(theta)-scalar_ll(theta,'Hybrid',y,x,offset,size,True))
                rows.append(dict(size=size,ridge=ridge,seed=seed,forward_error=error,**z))
    passed=len(rows)==36 and all(z['passed'] and z['forward_error']<=1e-10 for z in rows)
    r.save(r.HERE/'results/hybrid_full_history_errors.json',dict(gate='PASS' if passed else 'FAIL',rows=rows,synthetic_only=True))
    print('HYBRID_FULL_HISTORY',passed,'MAX_GRADIENT_ERROR',max(z['scaled_gradient_error'] for z in rows),'MAX_FORWARD_ERROR',max(z['forward_error'] for z in rows))
    if not passed:raise SystemExit(2)

if __name__=='__main__':main()
