"""Append-only QC execution evidence and saved-artifact sealing."""
import subprocess
import sys
from datetime import datetime, timezone

from register import HERE, OUT, ROOT, read, save, sha, verify


def register():
    verify()
    files = list(HERE.glob('*.py')) + list(HERE.glob('*.ps1'))
    save(OUT / 'QC_implementation_registration.json', {
        'registered_utc': datetime.now(timezone.utc).isoformat(),
        'before_QC_evaluation': True,
        'source_sha256': {p.relative_to(ROOT).as_posix(): sha(p) for p in files}})


def tests():
    result = subprocess.run([sys.executable, '-m', 'unittest', 'discover', '-s', str(HERE), '-p', 'test_*.py', '-v'],
                            capture_output=True, text=True, cwd=ROOT)
    with (OUT / 'tests.log').open('x', encoding='utf-8') as f:
        f.write(result.stdout + result.stderr)
    save(OUT / 'tests_result.json', {'utc': datetime.now(timezone.utc).isoformat(),
        'exit_code': result.returncode, 'tests_log_sha256': sha(OUT / 'tests.log'),
        'synthetic_tests_not_experimental_findings': True})
    print(result.stderr)
    if result.returncode:
        raise RuntimeError('Controlled tests failed')


def seal():
    verify()
    for name, digest in read(OUT / 'QC_implementation_registration.json')['source_sha256'].items():
        assert sha(ROOT / name) == digest, name
    excluded = {'artifact_lock.json', 'reproduction_receipt.json'}
    files = [p for p in OUT.rglob('*') if p.is_file() and p.name not in excluded]
    files += list(HERE.glob('*.py')) + list(HERE.glob('*.ps1')) + [HERE / 'protocol.json']
    save(OUT / 'artifact_lock.json', {p.relative_to(ROOT).as_posix(): sha(p) for p in files})
    print('Saved artifacts sealed; science unchanged.')


if __name__ == '__main__':
    {'register': register, 'tests': tests, 'seal': seal}[sys.argv[1]]()
