"""Append-only replay freshness repair; same saved-only scope, no neural access."""
import subprocess
import sys
from datetime import datetime, timezone
import register as r


def verify_manifest(expected=None):
    path = r.HERE / 'final_source_manifest2.json'
    digest = r.sha(path)
    if expected is not None and digest != expected:
        raise RuntimeError('REPLAY_MANIFEST_IDENTITY_CHANGED')
    manifest = r.load(path)
    for name, value in manifest['sha256'].items():
        if r.sha(r.HERE / name) != value:
            raise RuntimeError('REPLAY_INPUT_CHANGED:' + name)
    if r.sha(path) != digest:
        raise RuntimeError('REPLAY_MANIFEST_CHANGED_DURING_VERIFICATION')
    return digest


def main():
    start_digest = verify_manifest()
    output = r.HERE / 'replay/revision2'; output.mkdir(parents=True, exist_ok=True)
    commands = [[sys.executable, str(r.HERE / 'register.py'), '--verify'],
                [sys.executable, '-m', 'unittest', 'discover', '-s', str(r.HERE), '-p', 'test_*.py', '-v'],
                [sys.executable, str(r.HERE / 'aggregate4.py')]]
    checks = []
    for i, command in enumerate(commands):
        result = subprocess.run(command, cwd=r.ROOT, capture_output=True, text=True)
        path = output / ('check_%02d.log' % i)
        path.write_text(result.stdout + result.stderr, encoding='utf-8')
        checks.append(dict(command=command, exit_code=result.returncode,
                           log=path.relative_to(r.HERE).as_posix(), sha256=r.sha(path)))
        if result.returncode:
            break
    end_digest = verify_manifest(start_digest)
    receipt = dict(utc=datetime.now(timezone.utc).isoformat(), checks=checks,
                   start_manifest_sha256=start_digest, end_manifest_sha256=end_digest,
                   end_inputs_revalidated=True,
                   saved_checks_pass=len(checks) == 3 and all(x['exit_code'] == 0 for x in checks),
                   saved_M2_gate=r.load(r.HERE / 'results/M2/aggregate4/gate_result.json')['gate'],
                   scope='Saved public evidence/tests only', data_extraction_rerun=False,
                   live_security_rerun=False, experiments_reproduced=False, final_holdout_accessed=False)
    r.save(output / 'reproduction_receipt.json', receipt)
    print(receipt)
    if not receipt['saved_checks_pass']:
        sys.exit(1)


if __name__ == '__main__':
    main()
