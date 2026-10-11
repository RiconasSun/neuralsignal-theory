"""Metadata-only source/clock support preflight; no physiological accessor."""
import argparse
import hashlib
import json
import subprocess
import sys
from contextlib import contextmanager
from datetime import datetime, timezone

import run_r2 as run
import r2_external_support as support

OUT = run.base.STUDY/'results'/support.NAMESPACE
SOURCES = list(support.FILES)+['paper11_v2/scripts/run_r2_external_support.py']


def register():
    run.verify()
    if (OUT/'registration.json').exists():
        support.verify_registration(run.base.ROOT,OUT/'registration.json')
        return
    lock = run.load(run.base.STUDY/'results/R0_schema1/final_validation_lock.json')
    source = {'url':support.SOURCE_URL,'line_refs':[101,103,136,156],
              'prose':'The publisher describes continuous broadband acquisition, upstream stable task-long units, experiment-relative event seconds and unit-ragged timestamp storage. We will independently map each pinned asset frozen epoch to source-defined55/66 event boundaries. Containment plus this documented acquisition model supports a source-based continuous-observation inference, not a measured per-unit dropout certificate. Missing or inconsistent boundaries remain UNKNOWN_SUPPORT; no spike-derived recording interval or unknown-to-zero conversion is allowed.',
              'support_kind':'DOCUMENTED_CONTINUOUS_SUPPORT','direct_dropout_certification':False}
    gate = run.OUT/'gate_result.json'
    reg = {'study':'P11-v2','namespace':support.NAMESPACE,
           'registered_utc':datetime.now(timezone.utc).isoformat(),
           'source_sha256':{p:run.base.digest(run.base.ROOT/p) for p in SOURCES},
           'r2_registration_sha256':run.base.digest(run.OUT/'registration.json'),
           'r2_gate_sha256':run.base.digest(gate) if gate.exists() else None,
           'split_sha256':run.base.digest(run.base.STUDY/'results/R0_schema1/final_validation_lock.json'),
           'assets':{s['asset_id']:support._session_identity(s) for s in lock['eligible_sessions']},
           'version':support.VERSION,'allowed_decodes':{k:list(v) for k,v in support.ALLOWED.items()},
           'range_policy':support.POLICY,'timestamp_clock':support.CLOCK,
           'source_audit':source,'source_audit_sha256':hashlib.sha256(json.dumps(source,sort_keys=True,separators=(',',':')).encode()).hexdigest(),
           'phase':'METADATA_ONLY_PREFLIGHT','ab_prerequisite':'REQUIRED_BEFORE_SPIKES',
           'before_controlled_tests_and_metadata_execution':True,
           'execution_order_proof':'protocol/r2_execution.json requires completed A/B before external spikes, not before independent metadata-only coverage audit; no physiological accessor exists'}
    run.base.save(OUT/'registration.json',reg,immutable=True)
    support.verify_registration(run.base.ROOT,OUT/'registration.json')
    print('Registered source/clock metadata-only preflight before tests and access.')


def execute():
    support.verify_registration(run.base.ROOT,OUT/'registration.json')
    if (OUT/'execution_started.json').exists():
        raise RuntimeError('Metadata support execution already started; no overwriting or silent retries')
    run.base.save(OUT/'execution_started.json',{'utc':datetime.now(timezone.utc).isoformat()},immutable=True)
    tests = subprocess.run([sys.executable,'-m','unittest','discover','-s',str(run.base.STUDY/'tests'),
                            '-p','test_r2_external_support.py','-v'],capture_output=True,text=True)
    (OUT/'tests.log').write_text(tests.stdout+tests.stderr,encoding='utf-8')
    if tests.returncode:
        run.base.save(OUT/'engineering_test_failure.json',{'tests_exit_code':tests.returncode,
            'metadata_values_accessed':False,'scientific_coverage_not_evaluated':True},immutable=True)
        print(tests.stdout+tests.stderr)
        return 3
    import requests
    session = requests.Session()
    receipts = []
    @contextmanager
    def opener(identity,policy):
        if policy!=support.POLICY:
            raise RuntimeError('Range policy changed')
        reader = support.MetadataRangeReader(session,identity)
        try:
            yield reader
        finally:
            receipt = {'asset_id':identity['asset_id'],'range_receipts':reader.receipts,
                       'transport_bytes':reader.fetched,'spike_values_decoded':False}
            receipts.append(receipt)
            run.base.save(OUT/'transport'/f"{identity['asset_id']}.json",receipt,immutable=True)
            reader.close()
    try:
        result = support.audit(run.base.ROOT,OUT/'registration.json',opener)
    except Exception as exc:
        # Do not persist redirected/presigned URLs or credential-bearing messages.
        run.base.save(OUT/'transport_failure.json',{'error_class':type(exc).__name__,
                       'completed_transports':len(receipts),'neural_values_decoded':False},immutable=True)
        print('Transport/registration failed: '+type(exc).__name__+'; no scientific coverage verdict assigned.')
        return 4
    run.base.save(OUT/'support_audit.json',result,immutable=True)
    unknown = [{'asset_id':r['asset_id'],'path':r['path'],'reason':r.get('reason')}
               for r in result['sessions'] if r['status']!='DOCUMENTED_CONTINUOUS_SUPPORT']
    gate = {'gate_verdict':'PASS' if result['support_complete'] else 'FAIL',
            'scientific_verdict':'NOT_EVALUATED' if result['support_complete'] else 'DATA_INSUFFICIENT',
            'scope':'External source/clock observation support, NOT model validation or spike adequacy',
            'tests_exit_code':tests.returncode,'candidate_sessions':len(result['sessions']),
            'documented_support_sessions':len(result['sessions'])-len(unknown),'unknown_support':unknown,
            'spikes_decoded':False,'final_locked':True,'direct_dropout_certification':False,
            'external_unit_training_QC_executed':False,'external_parameter_fitting_executed':False}
    run.base.save(OUT/'gate_result.json',gate,immutable=True)
    run.base.save(OUT/'artifact_lock.json',{'sha256':{run.relative(p):run.base.digest(p)
                   for p in OUT.rglob('*') if p.is_file()}},immutable=True)
    print(json.dumps(gate,indent=2))
    return 0 if result['support_complete'] else 2


if __name__=='__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('action',choices=['register','execute'])
    action = parser.parse_args().action
    if action=='register':
        register()
    else:
        sys.exit(execute())
