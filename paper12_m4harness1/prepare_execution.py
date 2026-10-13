"""Conditional reuse of existing development artifacts; no extraction or fitting."""
import importlib.util
import shutil
import sys
from types import SimpleNamespace
import study as r


def security():
    sys.path.append(str(r.PREVIOUS))
    spec=importlib.util.spec_from_file_location('harness_scoped_atomic',r.PREVIOUS/'verified_atomic.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    module.verify_parity();module.require_custodian()
    return module


def numerical():
    record=r.load(r.HERE/'registration.json');gate=r.load(r.HERE/'results/numerical_gate.json')
    if gate['gate']!='PASS' or gate['tests_run']!=5 or gate['exit_code']!=0 or gate['errors'] or gate['failures'] or gate['skipped']:
        raise RuntimeError('FIVE_COMPLETE_NUMERICAL_CHECKS_REQUIRED')
    if gate['registration_sha256']!=r.sha(r.HERE/'registration.json') or gate['repaired_sha256']!=record['candidate_sha256']:
        raise RuntimeError('NUMERICAL_REGISTRATION_CHANGED')
    if r.sha(r.HERE/'patched/m4_numerical_tests.py')!=record['candidate_sha256'] or gate['log_sha256']!=r.sha(r.HERE/'results/numerical_tests.log'):
        raise RuntimeError('NUMERICAL_PROOF_CHANGED')
    if gate['syntax_receipt_sha256']!=r.sha(r.HERE/'results/syntax_receipt.json'):
        raise RuntimeError('SYNTAX_PROOF_CHANGED')
    review=r.load(r.HERE/'review_clearance.json')
    if review['decision']!='SYNTAX_SCOPE_AND_FIVE_CHECKS_CLEARED' or review['numerical_gate_sha256']!=r.sha(r.HERE/'results/numerical_gate.json'):
        raise RuntimeError('INDEPENDENT_REVIEW_REQUIRED')
    return gate


def main():
    r.verify();numerical();a=security()
    spec=importlib.util.spec_from_file_location('harness_saved_m3_links',r.M3/'saved_links.py')
    sys.path.insert(0,str(r.M3));links=importlib.util.module_from_spec(spec);spec.loader.exec_module(links)
    links.r=SimpleNamespace(HERE=r.M3,load=r.load,sha=r.sha)
    if links.verify()!=13:raise RuntimeError('UNCHANGED_FULL_M3_REQUIRED')
    old_policy=r.load(r.M3/'M4_registration.json')
    for name,digest in old_policy['source_sha256'].items():
        if r.sha(r.ROOT/name)!=digest:raise RuntimeError('FROZEN_SCIENTIFIC_SOURCE_CHANGED')
    exports=r.HERE/'exports';exports.mkdir(exist_ok=False)
    source=r.M3/'exports/full_AB';data=exports/'development_AB';shutil.copytree(source,data);a.protect(data)
    manifest=r.load(data/'manifest.json')
    if r.sha(data/'manifest.json')!=old_policy['input_manifest_sha256'] or len(manifest['sessions'])!=13 or manifest['group']!='development' or manifest['compartments']!=['A','B']:
        raise RuntimeError('FROZEN_DEVELOPMENT_INPUT_REQUIRED')
    for session in manifest['sessions']:
        if r.sha(data/session['file'])!=session['sha256']:raise RuntimeError('DEVELOPMENT_ARTIFACT_HASH_CHANGED')
    code=exports/'code';code.mkdir()
    for name,digest in old_policy['native_code_sha256'].items():
        original=r.M3/'exports/m4code'/name
        if r.sha(original)!=digest:raise RuntimeError('ARCHIVED_NATIVE_CODE_CHANGED')
        selected=r.HERE/'patched/m4_numerical_tests.py' if name=='m4_numerical_tests.py' else original
        shutil.copy2(selected,code/name)
    a.protect(code)
    runtime=exports/'runtime';shutil.copytree(r.M3/'exports/runtime',runtime);a.protect(runtime)
    runtime_hashes=r.load(r.M3/'optimizer_amendment.json')['runtime_sha256']
    for name,digest in runtime_hashes.items():
        if r.sha(runtime/name)!=digest:raise RuntimeError('VERIFIED_RUNTIME_HASH_CHANGED')
    private=r.HERE/'.private';a.prepare(private)
    for name in ('source_canary.bin','key_canary.bin'):
        path=private/name
        with path.open('xb') as f:f.write(b'SYNTHETIC_NO_NEURAL_CONTENT')
        a.protect(path)
    r.save(r.HERE/'execution_registration.json',dict(utc=r.datetime.now(r.timezone.utc).isoformat(),
        before_real_fits=True,numerical_gate_sha256=r.sha(r.HERE/'results/numerical_gate.json'),
        independent_review_sha256=r.sha(r.HERE/'review_clearance.json'),
        M3_gate_sha256=r.sha(r.M3/'results/full/gate_result.json'),M3_reused_fit_count=1638,
        source_sha256=old_policy['source_sha256'],native_code_sha256={p.name:r.sha(p) for p in code.iterdir() if p.is_file()},
        runtime_sha256=runtime_hashes,input_manifest_sha256=r.sha(data/'manifest.json'),
        implementation_sha256={n:r.sha(r.HERE/n) for n in ('prepare_execution.py','launch_m4.py')},
        original_M4_optimizer_offset_grids_seeds_unchanged=True,source_requests=0,final_evaluation_access=False),True)
    print('FROZEN_M3_REUSED; DEVELOPMENT_ONLY_M4_PROSPECTIVELY_REGISTERED')


if __name__=='__main__':main()
