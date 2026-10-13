import subprocess
import study as r


def main():
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=r.ROOT).decode().strip()
    if not head.startswith('3feccd53'):raise RuntimeError('BASE_MISMATCH')
    gate=r.load(r.HARNESS/'results/M4/native/gate_result.json')
    if gate['failure']!='MANDATORY_SHARED_OFFSET_FAILURE' or gate['gate']!='FAIL':raise RuntimeError('ORIGINAL_FAILURE_REQUIRED')
    if r.load(r.M3/'results/full/gate_result.json')['converged_fit_count']!=1638:raise RuntimeError('M3_UNCHANGED_PASS_REQUIRED')
    names=subprocess.check_output(['git','ls-files','-z'],cwd=r.ROOT).decode().split('\0')
    new=list(r.HERE.glob('*.py'))+[r.HERE/'protocol.json',r.HERE/'mission.json',r.HERE/'.gitignore',
        r.ROOT/'ops/evidence/2026-10-13/p12-m4-offset-numerical-recovery-1/goldenstandards.md']
    r.save(r.HERE/'registration.json',dict(mission=r.ID,base=head,utc=r.datetime.now(r.timezone.utc).isoformat(),
        prior_sha256={n:r.sha(r.ROOT/n) for n in names if n},
        implementation_sha256={p.relative_to(r.ROOT).as_posix():r.sha(p) for p in new},
        original_offset_failure_sha256=r.sha(r.HARNESS/'results/M4/native/766640955_CA1_offset.json'),
        prior_M4_gate_sha256=r.sha(r.HARNESS/'results/M4/native/gate_result.json'),source_requests=0,final_access=False),True)
    (r.HERE/'original_offset_diagnostics.json').write_bytes((r.HARNESS/'results/M4/native/766640955_CA1_offset.json').read_bytes())
    print('PROSPECTIVE_TRAINING_ONLY_OFFSET_RECOVERY_REGISTERED')


if __name__=='__main__':main()
