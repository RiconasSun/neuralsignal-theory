"""Prospective fixed optimizer amendment after verified training-only diagnosis."""
import difflib
import study as r
from launch_phase import completed


OLD=b'options=dict(maxiter=500,maxfun=20000,ftol=1e-5,gtol=1e-5)'
NEW=b'options=dict(maxiter=2000,maxfun=80000,ftol=1e-10,gtol=1e-5)'


def main():
    r.verify();bindings=completed('diagnosis');gate=r.load(r.HERE/'results/diagnosis/native/gate_result.json')
    if not gate['original_replay_exact'] or not gate['premature_relative_stopping'] or gate['completed_fit_count']!=3:
        raise RuntimeError('OFFSET_AMENDMENT_NOT_SUPPORTED_STOP')
    original=(r.PREVIOUS/'task_offset.py').read_bytes()
    if original.count(OLD)!=1:raise RuntimeError('ONLY_REGISTERED_OFFSET_OPTIMIZER_LOCATION')
    revised=original.replace(OLD,NEW,1)
    r.save(r.HERE/'optimizer_amendment.json',dict(utc=r.datetime.now(r.timezone.utc).isoformat(),
        diagnostic_sha256=bindings,original_offset_source_sha256=r.sha(r.PREVIOUS/'task_offset.py'),
        amended_offset_source_sha256=r.hashlib.sha256(revised).hexdigest(),before_repaired_fits=True,
        options=r.load(r.HERE/'protocol.json')['conditional_offset_amendment']['options'],
        scientific_criteria_unchanged=True,model_optimizer_unchanged=True,retry_budget=0,
        amendment_code_sha256=r.sha(r.HERE/'amend.py')),True)
    target=r.HERE/'patched';target.mkdir(exist_ok=False)
    (target/'task_offset.py').write_bytes(revised)
    (r.HERE/'offset_optimizer.diff').write_text(''.join(difflib.unified_diff(original.decode().splitlines(keepends=True),revised.decode().splitlines(keepends=True),fromfile='original/task_offset.py',tofile='amended/task_offset.py')),encoding='utf-8',newline='')
    print('EVIDENCE_SUPPORTED_OFFSET_ONLY_FIXED_AMENDMENT_REGISTERED')


if __name__=='__main__':main()
