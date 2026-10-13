"""Only a registered status prefix may differ from historical base bytes."""
import subprocess
import study as r


def prefix_ok(original,current,prefix,old_sha,new_sha):
    return r.hashlib.sha256(original).hexdigest()==old_sha and current==prefix+original and r.hashlib.sha256(current).hexdigest()==new_sha


def failure_ok(gate,digest,expected):
    if gate.get('gate')!='FAIL' or digest!=expected:raise RuntimeError('STOP_GATE_CHANGED')


def archive_admission(closure):
    if not closure or closure.get('failed_gate')!='results/M4/native/gate_result.json':
        raise RuntimeError('EXACT_M4_STOP_REGISTRATION_REQUIRED')


def verify(archive_required=False):
    record=r.load(r.HERE/'registration.json');path=r.HERE/'closure_registration.json'
    closure=r.load(path) if path.exists() else None
    if archive_required:archive_admission(closure)
    if closure:
        archive_admission(closure)
        stop=(r.HERE/closure['failed_gate']).resolve()
        if not stop.is_relative_to((r.HERE/'results').resolve()):raise RuntimeError('INVALID_STOP_PATH')
        failure_ok(r.load(stop),r.sha(stop),closure['failed_gate_sha256'])
    for name,digest in record['prior_sha256'].items():
        if r.sha(r.ROOT/name)==digest:continue
        if name!='ops/daily-operations.md' or not closure:raise RuntimeError('HISTORICAL_BYTES_CHANGED:'+name)
        original=subprocess.check_output(['git','show',record['base']+':'+name],cwd=r.ROOT)
        prefix=r.HERE/'ops_prefix_note.md'
        if r.sha(prefix)!=closure['prefix_sha256'] or not prefix_ok(original,(r.ROOT/name).read_bytes(),prefix.read_bytes(),digest,closure['new_ops_sha256']):
            raise RuntimeError('HISTORICAL_OPERATIONS_SUFFIX_CHANGED')
    for name,digest in record['implementation_sha256'].items():
        if r.sha(r.ROOT/name)!=digest:raise RuntimeError('REGISTERED_SOURCE_CHANGED:'+name)


def main():
    r.verify();stop=r.HERE/'results/M4/native/gate_result.json'
    if not stop.exists() or r.load(stop)['gate']!='FAIL':raise RuntimeError('NO_MANDATORY_FAILED_GATE_TO_ARCHIVE')
    note=r.HERE/'ops_prefix_note.md';original=(r.ROOT/'ops/daily-operations.md').read_bytes();prefix=note.read_bytes()
    r.save(r.HERE/'closure_registration.json',dict(utc=r.datetime.now(r.timezone.utc).isoformat(),
        failed_gate=stop.relative_to(r.HERE).as_posix(),failed_gate_sha256=r.sha(stop),prefix_sha256=r.sha(note),
        original_ops_sha256=r.hashlib.sha256(original).hexdigest(),new_ops_sha256=r.hashlib.sha256(prefix+original).hexdigest(),
        scope='Status prefix only; original complete bytes retained verbatim',scientific_gates_modified=False,
        authorization='User mission STOP and AGENTS.md closure metadata update'),True)
    (r.ROOT/'ops/daily-operations.md').write_bytes(prefix+original);verify(archive_required=True)
    print('REGISTERED_STATUS_PREFIX; HISTORICAL_SCIENTIFIC_BYTES_PRESERVED')


if __name__=='__main__':main()
