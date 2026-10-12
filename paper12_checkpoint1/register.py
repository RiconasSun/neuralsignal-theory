import subprocess
from datetime import datetime,timezone
import study as r


def main():
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=r.ROOT,text=True).strip()
    if head!=r.load(r.HERE/'protocol.json')['base']:raise RuntimeError('BASE_CHANGED')
    files=subprocess.check_output(['git','ls-files'],cwd=r.ROOT,text=True).splitlines()
    paths=['paper12_checkpoint1/'+name for name in ('.gitignore','mission.json','protocol.json','study.py','register.py')]
    paths+=['ops/evidence/2026-10-12/p12-m2-checkpoint-repair-1/goldenstandards.md']
    r.save(r.HERE/'registration.json',dict(utc=datetime.now(timezone.utc).isoformat(),base=head,
        prior_sha256={name:r.sha(r.ROOT/name) for name in files},
        prospective_sha256={name:r.sha(r.ROOT/name) for name in paths},
        old_operations=(r.ROOT/'ops/daily-operations.md').read_text(encoding='utf-8'),
        synthetic_trials_executed=0,neural_source_requests=0,protected_neural_contents_read=False),True)
    print('SYNTHETIC_CHECKPOINT_STUDY_PROSPECTIVELY_REGISTERED;NO_NEURAL_ACCESS')


if __name__=='__main__':main()
