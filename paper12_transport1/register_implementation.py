"""Trusted metadata-only private artifact binding and before-request code seal."""
from datetime import datetime,timezone
import common as r
import custodian as c


def main():
    registration=r.verify();c.require_custodian()
    private=r.OLD/'.private/transport_recovery1';private.mkdir(exist_ok=True);c.protect(private)
    artifacts={}
    for sid,entry in registration['reuse'].items():
        receipt=r.load(r.OLD/'results/M2/index2/sessions'/(sid+'.json'))
        namespace=receipt.get('custody_artifact_namespace','real_index2')
        if namespace not in ('real_index2','real_transport1'):raise RuntimeError('REUSE_NAMESPACE_INVALID')
        root=r.OLD/'.private'/namespace/sid
        fingerprints={}
        for compartment,expected in receipt['ciphertext_receipts'].items():
            path=root/(compartment+'.gcm')
            if r.sha(path)!=expected['ciphertext_sha256'] or path.stat().st_size!=expected['ciphertext_bytes']:
                raise RuntimeError('PRIOR_CIPHERTEXT_ARTIFACT_CHANGED')
            key=root/(compartment+'.key')
            if key.stat().st_size!=32:raise RuntimeError('PRIOR_KEY_INVALID')
            fingerprints[path.name]=r.sha(path);fingerprints[key.name]=r.sha(key)
        fingerprints['private_provenance.json']=r.sha(root/'private_provenance.json')
        artifacts[sid]=dict(namespace=namespace,fingerprints=fingerprints)
    issuer=private/'reuse_issuer.json';r.save(issuer,artifacts,True);c.protect(issuer)
    names=('bounded_core.py','range_transport.py','test_transport.py','test_completion.py','preflight.py','fresh_isolation.py','run_recovery.py','register_implementation.py')
    record=dict(utc=datetime.now(timezone.utc).isoformat(),implementation_sha256={p:r.sha(r.HERE/p) for p in names},
                registration_sha256=r.sha(r.HERE/'registration.json'),private_reuse_issuer_sha256=r.sha(issuer),
                redirects='Disabled;30Xfatal;no hidden requests',fatal_restart='Permanent STOP plus saved FATAL journal validation',
                read_timeout_scope='120seconds socket inactivity,not a hard total wall-time deadline;fixed4MiB blocks andthree requests perblock',
                source_requests_executed=0,final_values_exposed_to_analysis=False,final_holdout_evaluated=False)
    r.save(r.HERE/'implementation_registration.json',record,True)
    print('TRANSPORT_IMPLEMENTATION_AND_EIGHT_PRIVATE_REUSE_ARTIFACTS_BOUND;NO_SOURCE_REQUEST')


if __name__=='__main__':main()
