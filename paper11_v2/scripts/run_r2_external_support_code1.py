"""Append-only registration repair: missing ordering proof, no empirical change."""
import argparse
import hashlib
import importlib.util
import json
import subprocess
import sys
from contextlib import contextmanager
from datetime import datetime, timezone

import run_r2 as run

spec = importlib.util.spec_from_file_location('r2_support_code1_isolated',run.base.STUDY/'scripts/r2_external_support.py')
support = importlib.util.module_from_spec(spec)
spec.loader.exec_module(support)
support.NAMESPACE = 'R2_external_support_code1'
support.POLICY = {**support.POLICY,'namespace':support.NAMESPACE}
OUT = run.base.STUDY/'results'/support.NAMESPACE
ORIGINAL = run.base.STUDY/'results/R2_external_support/registration.json'
SOURCES = list(support.FILES)+['paper11_v2/scripts/run_r2_external_support.py',
           'paper11_v2/scripts/run_r2_external_support_code1.py','paper11_v2/tests/test_r2_external_support_code1.py']


def source_audit():
    return {'url':support.SOURCE_URL,'line_refs':[101,103,136,156],
        'prose':'Published continuous acquisition, upstream task-long stable units and experiment-relative event seconds provide a documented acquisition model. Map every pinned frozen scoring epoch to independently read source-defined55/66 event boundaries. This is source-supported interval containment, not measured per-unit dropout or training-spike eligibility. Missing/inconsistent endpoints stay UNKNOWN_SUPPORT; do not infer support from spikes or fill unknown intervals with zero counts.',
        'support_kind':'DOCUMENTED_CONTINUOUS_SUPPORT','direct_dropout_certification':False,
        'execution_order_proof':support.ORDERING_PROOF}


def verify():
    reg,sessions = support.verify_registration(run.base.ROOT,OUT/'registration.json')
    if run.base.digest(ORIGINAL)!=reg['original_registration_sha256']:
        raise RuntimeError('Original failed metadata registration changed')
    return reg,sessions


def register():
    run.verify()
    if (OUT/'registration.json').exists():
        verify(); return
    source = source_audit()
    gate = run.OUT/'gate_result.json'
    lock = run.load(run.base.STUDY/'results/R0_schema1/final_validation_lock.json')
    run.base.save(OUT/'registration.json',{
        'study':'P11-v2','namespace':support.NAMESPACE,'phase':support.PHASE,
        'ab_prerequisite':support.SPIKE_PREREQUISITE,
        'registered_utc':datetime.now(timezone.utc).isoformat(),
        'source_sha256':{p:run.base.digest(run.base.ROOT/p) for p in SOURCES},
        'original_registration_sha256':run.base.digest(ORIGINAL),
        'original_failure':'RegistrationError missing source-audit execution_order_proof, no tests or external metadata reads executed.',
        'repair':'Supply required ordering proof and isolate a new output namespace. Same original helper, endpoints, range limits, split, source-support criterion and tests; no spike/score access.',
        'r2_registration_sha256':run.base.digest(run.OUT/'registration.json'),
        'r2_gate_sha256':run.base.digest(gate) if gate.exists() else None,
        'split_sha256':run.base.digest(run.base.STUDY/'results/R0_schema1/final_validation_lock.json'),
        'assets':{s['asset_id']:support._session_identity(s) for s in lock['eligible_sessions']},
        'version':support.VERSION,'allowed_decodes':{k:list(v) for k,v in support.ALLOWED.items()},
        'range_policy':support.POLICY,'timestamp_clock':support.CLOCK,
        'source_audit':source,'source_audit_sha256':hashlib.sha256(json.dumps(source,sort_keys=True,separators=(',',':')).encode()).hexdigest(),
        'before_tests_and_metadata_access':True},immutable=True)
    verify(); print('CODE1 metadata-only registration verified; original failure preserved.')


def execute():
    verify()
    if (OUT/'execution_started.json').exists():
        raise RuntimeError('Metadata execution already started; no silent retry/overwrite')
    run.base.save(OUT/'execution_started.json',{'utc':datetime.now(timezone.utc).isoformat()},immutable=True)
    tests = subprocess.run([sys.executable,'-m','unittest','discover','-s',str(run.base.STUDY/'tests'),
                            '-p','test_r2_external_support*.py','-v'],capture_output=True,text=True)
    (OUT/'tests.log').write_text(tests.stdout+tests.stderr,encoding='utf-8')
    if tests.returncode:
        run.base.save(OUT/'engineering_test_failure.json',{'tests_exit_code':tests.returncode,
                         'external_values_accessed':False},immutable=True)
        print(tests.stdout+tests.stderr); return 3
    import requests
    session = requests.Session()
    receipts = []
    @contextmanager
    def opener(identity,policy):
        if policy!=support.POLICY:
            raise RuntimeError('Metadata range policy mismatch')
        reader = support.MetadataRangeReader(session,identity)
        try:
            yield reader
        finally:
            receipt = {'asset_id':identity['asset_id'],'range_receipts':reader.receipts,
                       'transport_bytes':reader.fetched,'spike_values_decoded':False}
            receipts.append(receipt)
            run.base.save(OUT/'transport'/f"{identity['asset_id']}.json",receipt,immutable=True)
            print(f"METADATA {identity['path']} bytes={reader.fetched}",flush=True)
            reader.close()
    try:
        result = support.audit(run.base.ROOT,OUT/'registration.json',opener)
    except Exception as exc:
        run.base.save(OUT/'transport_failure.json',{'error_class':type(exc).__name__,
                      'completed_transports':len(receipts),'neural_values_decoded':False},immutable=True)
        print('Transport/registration error '+type(exc).__name__+'; scientific support not adjudicated.')
        return 4
    run.base.save(OUT/'support_audit.json',result,immutable=True)
    unknown = [{'asset_id':r['asset_id'],'path':r['path'],'reason':r.get('reason')}
               for r in result['sessions'] if r['status']!='DOCUMENTED_CONTINUOUS_SUPPORT']
    gate = {'gate_verdict':'PASS' if result['support_complete'] else 'FAIL',
            'scientific_verdict':'NOT_EVALUATED' if result['support_complete'] else 'DATA_INSUFFICIENT',
            'scope':'External documented observation support only, not predictive validation',
            'candidate_sessions':len(result['sessions']),'documented_support_sessions':len(result['sessions'])-len(unknown),
            'unknown_support':unknown,'tests_exit_code':tests.returncode,'spikes_decoded':False,
            'final_locked':True,'direct_dropout_certification':False,
            'external_training_QC_executed':False,'external_model_evaluation_executed':False}
    run.base.save(OUT/'gate_result.json',gate,immutable=True)
    run.base.save(OUT/'artifact_lock.json',{'sha256':{run.relative(p):run.base.digest(p)
                   for p in OUT.rglob('*') if p.is_file()}},immutable=True)
    print(json.dumps(gate,indent=2)); return 0 if result['support_complete'] else 2


if __name__=='__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('action',choices=['register','execute'])
    action = parser.parse_args().action
    if action=='register':
        register()
    else:
        sys.exit(execute())
