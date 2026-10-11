"""Audit the stopped candidate without reading neural timestamps."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PAPER = ROOT / 'paper11'
EVIDENCE = ROOT / 'ops/evidence/2026-10-10/paper11-autonomous'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    gates = {f'M{i}': json.loads((PAPER / f'results/M{i}/gate_result.json').read_text()) for i in range(5)}
    assert all(gates[f'M{i}']['gate'] == 'PASS' for i in range(4))
    assert gates['M4']['gate'] == 'FAIL' and not gates['M4']['final_test_count_access']
    assert not any((PAPER / f'results/M{i}/gate_result.json').exists() for i in range(5, 8))
    accuracy = json.loads((PAPER / 'results/M4/accuracy/sub-01_ses-01/continuous_k1_d1_seed71.json').read_text())
    assert accuracy['gate'] == 'FAIL'
    assert [item['particles'] for item in accuracy['comparisons']] == [64, 256, 1024]
    assert all(item['conservative_discrepancy'] > .001 for item in accuracy['comparisons'])
    for rel, digest in gates['M4']['source_sha256'].items():
        if rel != 'tests/test_m4.py':
            assert sha(PAPER / rel) == digest, rel
    report = (EVIDENCE / 'regression-tests.txt').read_text(encoding='utf-8-sig')
    assert 'Ran 70 tests' in report and report.rstrip().endswith('OK')
    changed = subprocess.check_output(['git', 'diff', '--name-only', '9145c407cf383226f111752d6299c4b5c0a98303'], cwd=ROOT, text=True).splitlines()
    assert all(path == 'ops/daily-operations.md' or path.startswith(('paper11/', 'ops/evidence/2026-10-10/paper11-autonomous/')) for path in changed), changed
    previous = subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', '9145c407cf383226f111752d6299c4b5c0a98303', '--', 'paper11'], cwd=ROOT, text=True).splitlines()
    for rel in previous:
        if rel == 'paper11/MILESTONE_STATUS.md':
            continue
        original = subprocess.check_output(['git', 'show', f'9145c407cf383226f111752d6299c4b5c0a98303:{rel}'], cwd=ROOT)
        assert (ROOT / rel).read_bytes() == original, rel
    tracked = subprocess.check_output(['git', 'ls-files'], cwd=ROOT, text=True).splitlines()
    assert not any(path.startswith('paper11/raw/') for path in tracked)
    files = [path for folder in ('paper11', 'ops/evidence/2026-10-10/paper11-autonomous')
             for path in (ROOT / folder).rglob('*') if path.is_file()
             and 'raw' not in path.relative_to(ROOT).parts
             and '__pycache__' not in path.parts and 'test-temp' not in path.parts
             and path.name != 'closing-audit.json']
    result = {'audit': 'PASS', 'scientific_gate': 'FAIL', 'scientific_verdict': 'INCONCLUSIVE',
              'regression_tests': 70, 'final_test_count_access': False,
              'source_hash_exception': 'Historical M4 tests; final ten-test suite separately verified',
              'files_sha256': {path.relative_to(ROOT).as_posix(): sha(path) for path in sorted(files)}}
    (EVIDENCE / 'closing-audit.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({key: value for key, value in result.items() if key != 'files_sha256'}, indent=2))


if __name__ == '__main__':
    main()
