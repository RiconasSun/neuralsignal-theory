"""One explicit metadata prefix exception; scientific archives remain byte-identical."""
import hashlib
import subprocess
import study as r


def validate_prefix(original,current,prefix,original_sha,new_sha):
    return (hashlib.sha256(original).hexdigest()==original_sha and current==prefix+original and
            hashlib.sha256(current).hexdigest()==new_sha)


def validate_failure(gate,digest,expected):
    if digest!=expected or gate.get('gate')!='FAIL':
        raise RuntimeError('SCIENTIFIC_STOP_EVIDENCE_CHANGED')


def verify():
    record=r.load(r.HERE/'registration.json')
    closure=r.HERE/'closure_registration.json'
    allowed=r.load(closure) if closure.exists() else None
    if allowed is not None:
        failed=(r.HERE/allowed['failed_gate']).resolve()
        if not failed.is_relative_to((r.HERE/'results').resolve()):raise RuntimeError('INVALID_STOP_EVIDENCE_PATH')
        validate_failure(r.load(failed),r.sha(failed),allowed['failed_gate_sha256'])
    for name,digest in record['prior_sha256'].items():
        if r.sha(r.ROOT/name)==digest:continue
        if name!='ops/daily-operations.md' or allowed is None:raise RuntimeError('ARCHIVED_BYTES_CHANGED:'+name)
        original=subprocess.check_output(['git','show',record['base']+':'+name],cwd=r.ROOT)
        note=r.HERE/'ops_prefix_note.md'
        if r.sha(note)!=allowed['prefix_sha256']:raise RuntimeError('CLOSURE_PREFIX_CHANGED')
        if not validate_prefix(original,(r.ROOT/name).read_bytes(),note.read_bytes(),digest,allowed['new_ops_sha256']):
            raise RuntimeError('ORIGINAL_OPERATIONS_BYTES_NOT_PRESERVED')
    for name,digest in record['prospective_sha256'].items():
        if r.sha(r.ROOT/name)!=digest:raise RuntimeError('FROZEN_PROTOCOL_CHANGED:'+name)
    return record
