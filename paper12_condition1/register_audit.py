"""Freeze source and synthetic admission before Stage1 real audit."""
import study as r
def main():
    names=['paper12_condition1/'+p for p in ('study.py','conditioning.py','policies.py','worker.py','launch.py','prepare.py','test_conditioning.py','independent_ad.py','saved_vectors.json','audit_protocol.json')]
    names+=['paper12_m4offset1/launch_phase.py','paper12_custody1/launch_analysis.py','paper12_resume1/verified_atomic.py','paper12_contgrad1/execution_registration.json']
    r.save(r.HERE/'audit_source_registration.json',{'utc':r.datetime.now(r.timezone.utc).isoformat(),'before_real_audit':True,'before_real_optimization':True,'baseline_registration_sha256':r.sha(r.HERE/'baseline_registration.json'),'synthetic_log_sha256':r.sha(r.HERE/'synthetic_attempt2.log'),'source_sha256':{name:r.sha(r.ROOT/name) for name in names}})
    print('AUDIT_SOURCE_REGISTERED',r.sha(r.HERE/'audit_source_registration.json'))
if __name__=='__main__':main()
