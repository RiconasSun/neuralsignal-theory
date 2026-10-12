"""Additive ops annotation only; conserve exact base bytes and all other hashes."""
import hashlib
import subprocess
import study as r


def verify():
    record=r.load(r.HERE/'registration.json')
    for name,digest in record['prior_sha256'].items():
        if name=='ops/daily-operations.md':
            original=subprocess.check_output(['git','show',record['base']+':'+name],cwd=r.ROOT)
            if hashlib.sha256(original).hexdigest()!=digest or not (r.ROOT/name).read_bytes().endswith(original):
                raise RuntimeError('PRIOR_OPERATIONS_BYTES_CHANGED')
        elif r.sha(r.ROOT/name)!=digest:raise RuntimeError('PRIOR_EVIDENCE_CHANGED:'+name)
    for name,digest in record['prospective_sha256'].items():
        if r.sha(r.ROOT/name)!=digest:raise RuntimeError('PROTOCOL_CHANGED:'+name)
    return record
