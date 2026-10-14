import study as r

def main():
    head=r.subprocess.check_output(['git','rev-parse','HEAD'],cwd=r.ROOT).decode().strip()
    if head!='e635724f2aae45b7fdf30edb5902beaab425b8e2':raise RuntimeError('BASE_MISMATCH')
    prior=r.subprocess.check_output(['git','ls-files','-z'],cwd=r.ROOT).decode().split('\0')
    files=list(r.HERE.glob('*.py'))+list(r.HERE.glob('*.json'))+[r.HERE/'.gitignore',r.ROOT/'ops/evidence/2026-10-13/p12-m4-dynamics-numerical-recovery-1/goldenstandards.md']
    r.save(r.HERE/'registration.json',dict(mission=r.ID,utc=r.datetime.now(r.timezone.utc).isoformat(),base=head,
        prior_sha256={n:r.sha(r.ROOT/n) for n in prior if n},
        implementation_sha256={p.relative_to(r.ROOT).as_posix():r.sha(p) for p in files},
        final_access=False,source_requests=0,before_synthetic_tests=True,before_training_access=True))

if __name__=='__main__':main()
