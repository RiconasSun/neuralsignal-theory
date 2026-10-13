"""Archive a required scientific stop; no data or experiment execution."""
import hashlib
from datetime import datetime,timezone
import study as r


def main():
    r.verify()
    sources=[r.HERE/'results/full/gate_result.json',r.HERE/'results/M4/numerical_gate.json',r.HERE/'results/M4/native/gate_result.json']
    failed=[p for p in sources if p.exists() and r.load(p)['gate']=='FAIL']
    if not failed:raise RuntimeError('NO_FAILED_MANDATORY_GATE_TO_CLOSE')
    stage=failed[0]
    # Prefix is explicit user-governed status metadata, never a scientific gate edit.
    note=r.HERE/'ops_prefix_note.md'
    original=(r.ROOT/'ops/daily-operations.md').read_bytes();prefix=note.read_bytes()
    r.save(r.HERE/'closure_registration.json',dict(utc=datetime.now(timezone.utc).isoformat(),
        scope='K4C closure status prefix only, original status bytes retained as suffix',
        authorization='User AGENTS.md sections13/16; scientific STOP from latest mission',
        failed_gate=stage.relative_to(r.HERE).as_posix(),failed_gate_sha256=r.sha(stage),
        original_ops_sha256=r.sha(r.ROOT/'ops/daily-operations.md'),prefix_sha256=r.sha(note),
        new_ops_sha256=hashlib.sha256(prefix+original).hexdigest(),scientific_gates_modified=False),True)
    (r.ROOT/'ops/daily-operations.md').write_bytes(prefix+original)
    from closure_verify import verify
    verify();print('STATUS_PREFIX_ADDED; ORIGINAL_ALL_SCIENTIFIC_BYTES_PRESERVED')


if __name__=='__main__':main()
