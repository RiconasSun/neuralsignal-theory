"""Prospective bridge registration only, not model execution or original amendment."""
from datetime import datetime,timezone
import study as r


def guard_adapter():
    from preflight import guard
    guard()
    versions=[r.HERE/name for name in ('M3_adapter_registration_code4.json','M3_adapter_registration_code3.json','M3_adapter_registration_code2.json','M3_adapter_registration.json')]
    policy=r.load(next(path for path in versions if path.exists()))
    for name,digest in policy['sha256'].items():
        if r.sha(r.HERE/name)!=digest:raise RuntimeError('M3_ADAPTER_CHANGED')
    if policy['original_development_registration_sha256']!=r.sha(r.OLD/'development_registration.json') or policy['original_method_sha256']!=r.sha(r.OLD/'M3_METHOD_DECISION1.json'):
        raise RuntimeError('M3_ORIGINAL_POLICY_BINDING_CHANGED')
    if policy['new_M2_gate_sha256']!=r.sha(r.HERE/'results/M2/gate_result.json') or r.load(r.HERE/'results/M2/gate_result.json')['gate']!='PASS':
        raise RuntimeError('M3_NEW_M2_GATE_BINDING_CHANGED')
    return policy


def main():
    r.verify()
    if r.load(r.HERE/'results/M2/gate_result.json')['gate']!='PASS':raise RuntimeError('NEW_M2_PASS_REQUIRED')
    name='M3_adapter_registration_code4.json' if (r.HERE/'M3_adapter_registration_code3.json').exists() else 'M3_adapter_registration_code3.json' if (r.HERE/'M3_adapter_registration_code2.json').exists() else 'M3_adapter_registration_code2.json' if (r.HERE/'M3_adapter_registration.json').exists() else 'M3_adapter_registration.json'
    output=r.HERE/name
    r.save(output,dict(utc=datetime.now(timezone.utc).isoformat(),
        sha256={name:r.sha(r.HERE/name) for name in ('development.py','launch_m3.py','register_m3.py','fingerprints.py','test_development_adapter.py')},
        original_development_registration_sha256=r.sha(r.OLD/'development_registration.json'),
        original_method_sha256=r.sha(r.OLD/'M3_METHOD_DECISION1.json'),
        new_M2_gate_sha256=r.sha(r.HERE/'results/M2/gate_result.json'),
        original_adapter_registration_sha256=r.sha(r.HERE/'M3_adapter_registration.json') if (r.HERE/'M3_adapter_registration.json').exists() else None,
        policy='Only receipt/private storage/new gate bindings change. Original A/B trials, SHA-ranked <=32 units, per-unit exposure ridge, all21 grids/all3 seeds and progressive smoke/small/full gates unchanged. Original code copied into new mission runtime, never old runtime ACL mutation.'),True)
    print('M3_STORAGE_BRIDGE_FROZEN; NO MODEL FITTING')


if __name__=='__main__':main()
