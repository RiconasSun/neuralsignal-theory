"""Append source-security revision; initial registered files are never overwritten."""
import ast
import study as r
from worker2 import transformed


def main():
    r.verify();compiled=transformed((r.HERE/'worker.py').read_text());ast.parse(compiled)
    names=('worker2.py','launch_phase2.py','roster_guard.py','register_guards.py','test_roster.py','amend.py')
    r.save(r.HERE/'guard_registration.json',dict(utc=r.datetime.now(r.timezone.utc).isoformat(),
        before_repaired_evaluation=True,scope='P1 source and reused-state integrity guards only; v1 preserved unchanged',
        sha256={n:r.sha(r.HERE/n) for n in names},transformed_worker_sha256=r.hashlib.sha256(compiled.encode()).hexdigest(),
        mathematical_definitions_changed=False,thresholds_changed=False,offset_optimizer_policies=1),True)
    print('GUARD_ONLY_PROSPECTIVE_REVISION_REGISTERED')


if __name__=='__main__':main()
