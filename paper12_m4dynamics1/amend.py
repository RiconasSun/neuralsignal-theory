import study as r
from controls import verify,completed

def main():
    verify();bindings=completed('diagnosis');gate=r.load(r.HERE/'results/diagnosis/native/gate_result.json')
    if gate['scientific_verdict']!='DYNAMICS_AMENDMENT_ELIGIBLE' or gate['completed_fit_count']!=216 or gate['gradient_failures']!=0:raise RuntimeError('ELIGIBILITY_REQUIRED')
    r.save(r.HERE/'optimizer_amendment.json',dict(utc=r.datetime.now(r.timezone.utc).isoformat(),before_new_fits=True,scope='Dynamical-model optimizer only',
        diagnosis_bindings=bindings,options=dict(ftol=1e-10,gtol=1e-5,maxiter=2000,maxfun=80000),
        unchanged=['PG<=.001','bounds','ridge','all seeds','model mathematics','shared offset weights','data/splits','one-SE rules'],
        no_validation_guidance=True,no_offset_refits=True,implementation='Original objective and architecture unchanged; worker passes explicitly registered solver options'))

if __name__=='__main__':main()
