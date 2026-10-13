import subprocess
import study as r

ALLOWED={'results/'+p+'/native/gate_result.json' for p in ('diagnosis','smoke','small','full','M4')}
ALLOWED.add('results/M4/numerical_gate.json')


def admission(record):
    if not record or record.get('failed_gate') not in ALLOWED:raise RuntimeError('REGISTERED_EXACT_STOP_REQUIRED')


def prefix_ok(original,current,prefix,old_sha,new_sha):
    return r.hashlib.sha256(original).hexdigest()==old_sha and current==prefix+original and r.hashlib.sha256(current).hexdigest()==new_sha


def native_complete(receipt,proof):
    if receipt.get('exit_code')!=2 or receipt.get('timed_out') is not False or receipt.get('role_proof_pass') is not True or receipt.get('profile_cleanup_hresult')!='0x00000000' or proof.get('pass') is not True or proof.get('is_appcontainer') is not True or proof.get('capability_count')!=0:
        raise RuntimeError('COMPLETED_FAILED_NATIVE_RECEIPT_REQUIRED')


def bind_completion(record):
    stop=record['failed_gate']
    if '/native/' not in stop:
        gate=r.load(r.HERE/stop)
        if gate.get('exit_code')!=1 or gate['log_sha256']!=r.sha(r.HERE/'results/M4/numerical_tests.log'):
            raise RuntimeError('COMPLETED_SYNTHETIC_FAILURE_REQUIRED')
        return {'synthetic_log_sha256':gate['log_sha256']}
    phase=stop.split('/')[1];receipt=r.HERE/f'results/{phase}_launch_receipt.json';proof=r.HERE/f'results/{phase}/native/role_proof.json'
    native_complete(r.load(receipt),r.load(proof))
    return dict(receipt_sha256=r.sha(receipt),proof_sha256=r.sha(proof),failed_gate_sha256=r.sha(r.HERE/stop))


def verify(archive_required=True):
    record=r.load(r.HERE/'registration.json');path=r.HERE/'closure_registration.json'
    closure=r.load(path) if path.exists() else None
    if archive_required:admission(closure)
    if closure:
        admission(closure);stop=r.HERE/closure['failed_gate']
        if r.sha(stop)!=closure['failed_gate_sha256'] or r.load(stop)['gate']!='FAIL':raise RuntimeError('STOP_EVIDENCE_CHANGED')
        completion=r.load(r.HERE/'closure_completion_binding.json')
        if completion['closure_registration_sha256']!=r.sha(path) or completion['completed_failure_bindings']!=bind_completion(closure):
            raise RuntimeError('ARCHIVE_COMPLETION_BINDINGS_CHANGED')
    for name,digest in record['prior_sha256'].items():
        if r.sha(r.ROOT/name)==digest:continue
        if name!='ops/daily-operations.md' or not closure:raise RuntimeError('HISTORICAL_BYTES_CHANGED:'+name)
        original=subprocess.check_output(['git','show',record['base']+':'+name],cwd=r.ROOT)
        prefix=r.HERE/'ops_prefix_note.md'
        if r.sha(prefix)!=closure['prefix_sha256'] or not prefix_ok(original,(r.ROOT/name).read_bytes(),prefix.read_bytes(),digest,closure['new_ops_sha256']):raise RuntimeError('HISTORICAL_STATUS_SUFFIX_CHANGED')
    for name,digest in record['implementation_sha256'].items():
        if r.sha(r.ROOT/name)!=digest:raise RuntimeError('INITIAL_DIAGNOSTIC_SOURCE_CHANGED')
    guards=r.load(r.HERE/'guard_registration.json')
    for name,digest in guards['sha256'].items():
        if r.sha(r.HERE/name)!=digest:raise RuntimeError('PROSPECTIVE_GUARD_SOURCE_CHANGED')


def main():
    r.verify();failed=[p for p in sorted(ALLOWED) if (r.HERE/p).exists() and r.load(r.HERE/p)['gate']=='FAIL']
    if not failed:raise RuntimeError('NO_MANDATORY_FAILED_GATE_TO_ARCHIVE')
    stop=failed[0];original=(r.ROOT/'ops/daily-operations.md').read_bytes();prefix=(r.HERE/'ops_prefix_note.md').read_bytes()
    completion=bind_completion({'failed_gate':stop})
    r.save(r.HERE/'closure_registration.json',dict(utc=r.datetime.now(r.timezone.utc).isoformat(),failed_gate=stop,
        failed_gate_sha256=r.sha(r.HERE/stop),prefix_sha256=r.sha(r.HERE/'ops_prefix_note.md'),
        original_ops_sha256=r.hashlib.sha256(original).hexdigest(),new_ops_sha256=r.hashlib.sha256(prefix+original).hexdigest(),
        authorization='User scientific STOP and AGENTS.md status closure; original scientific bytes preserved',scientific_gates_modified=False),True)
    r.save(r.HERE/'closure_completion_binding.json',dict(utc=r.datetime.now(r.timezone.utc).isoformat(),
        closure_registration_sha256=r.sha(r.HERE/'closure_registration.json'),completed_failure_bindings=completion),True)
    (r.ROOT/'ops/daily-operations.md').write_bytes(prefix+original);verify();print('EXACT_STOP_REGISTERED; OLD_SCIENTIFIC_BYTES_PRESERVED')


if __name__=='__main__':main()
