"""Same pinned metadata audit, separate network-recovery evidence namespace."""
import argparse
import importlib.util
import sys
from datetime import datetime, timezone

import run_r2 as run

spec = importlib.util.spec_from_file_location('r2_support_code2_adapter',run.base.STUDY/'scripts/run_r2_external_support_code1.py')
adapter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(adapter)
adapter.support.NAMESPACE = 'R2_external_support_code2'
adapter.support.POLICY = {**adapter.support.POLICY,'namespace':adapter.support.NAMESPACE}
adapter.OUT = run.base.STUDY/'results'/adapter.support.NAMESPACE
PRIOR = run.base.STUDY/'results/R2_external_support_code1'
ORIGINAL_VERIFY = adapter.verify


def verify():
    reg,sessions = ORIGINAL_VERIFY()
    for rel,sha in reg['preserved_network_attempt_sha256'].items():
        if run.base.digest(run.base.ROOT/rel)!=sha:
            raise RuntimeError('Original metadata network failure evidence changed')
    return reg,sessions


def register():
    run.verify()
    if (adapter.OUT/'registration.json').exists():
        verify(); return
    reg = run.load(PRIOR/'registration.json')
    for rel,sha in reg['source_sha256'].items():
        if run.base.digest(run.base.ROOT/rel)!=sha:
            raise RuntimeError('Preceding metadata audit source changed')
    if (PRIOR/'gate_result.json').exists():
        raise RuntimeError('No retry of a previously adjudicated scientific support gate')
    failure = run.load(PRIOR/'transport_failure.json')
    if failure['error_class']!='ConnectionError' or failure['neural_values_decoded']:
        raise RuntimeError('Not the diagnosed pre-response network failure')
    reg.update(namespace=adapter.support.NAMESPACE,
               range_policy=adapter.support.POLICY,
               registered_utc=datetime.now(timezone.utc).isoformat(),
               original_failure='CODE1 ConnectionError before any response bytes; no source/clock support verdict or spike access.',
               repair='Identical52asset IDs, scalar endpoints, split and support/transport criteria; network recovery under approved escalation. Separate output namespace; no prior overwrite.',
               preserved_network_attempt_sha256={run.relative(p):run.base.digest(p) for p in PRIOR.rglob('*') if p.is_file()})
    reg['source_sha256'].update({f'paper11_v2/{rel}':run.base.digest(run.base.STUDY/rel) for rel in
        ['scripts/run_r2_external_support_code2.py','tests/test_r2_external_support_code2.py']})
    run.base.save(adapter.OUT/'registration.json',reg,immutable=True)
    verify(); print('CODE2 identical metadata audit registered; prior transport failure preserved.')


if __name__=='__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('action',choices=['register','execute'])
    action = parser.parse_args().action
    if action=='register':
        register()
    else:
        adapter.verify = verify
        sys.exit(adapter.execute())
