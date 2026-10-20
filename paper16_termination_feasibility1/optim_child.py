"""SciPy client: never receives counts/features; every FG is externally brokered."""
import json,os,sys
import numpy as np
from scipy.optimize import minimize
from .common import NUMERIC,require_job

def request(op,x):
    print(json.dumps({'op':op,'x':np.asarray(x).tolist()}),flush=True)
    reply=json.loads(sys.stdin.readline())
    if not reply.get('allowed'):raise RuntimeError('External optimizer broker denied request')
    return reply

def run(path):
    require_job(os.environ['P16_TF1_JOB'])
    with open(path,encoding='utf8') as f:config=json.load(f)
    fun=lambda x:(lambda r:(r['value'],np.asarray(r['gradient'])))(request('FG',x))
    result=minimize(fun,np.asarray(config['x0']),jac=True,method='L-BFGS-B',
        bounds=list(zip(config['lo'],config['hi'])),callback=lambda x:request('ITER',x),options=NUMERIC['options'])
    print(json.dumps({'op':'DONE','x':result.x.tolist(),'fun':float(result.fun),'jac':result.jac.tolist(),
        'success':bool(result.success),'message':str(result.message),'nit':int(result.nit),'nfev':int(result.nfev)}),flush=True)

if __name__=='__main__':run(sys.argv[1])
