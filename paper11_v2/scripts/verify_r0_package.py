"""Verify a negative R0 result without converting it into scientific success."""
import json
import subprocess
import sys
from pathlib import Path

import run_r0 as base
import run_r0_schema as schema

OUT = base.STUDY / 'results/R0_final'


def main():
    command = ['powershell.exe', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File',
               str(base.STUDY / 'scripts/reproduce.ps1'), '-Python', sys.executable]
    run = subprocess.run(command, cwd=base.ROOT, capture_output=True, text=True)
    (OUT / 'reproduction.txt').write_text(run.stdout + run.stderr, encoding='utf-8')
    gate = json.loads((OUT / 'gate_result.json').read_text())
    base.verify_registration()
    schema.verify()
    archive = json.loads((base.OUT / 'registration.json').read_text())['archive_sha256']
    assert archive == base.archive_inventory(), 'Archive bytes changed'
    assert run.returncode == 2, f'Expected scientific-stop code2, observed {run.returncode}'
    assert gate['gate_verdict'] == 'FAIL'
    assert gate['scientific_verdict'] == 'DATA_INSUFFICIENT'
    assert gate['development_candidate_upper_bound'] == 2
    assert gate['external_candidate_subjects'] == 36
    assert gate['external_candidate_sessions'] == 52
    assert gate['tests_exit_code'] == 0
    assert gate['new_neural_values_accessed'] is False
    assert gate['R1_R2_R3_executed'] is False
    assert 'Ran 20 tests' in (OUT / 'tests.txt').read_text()
    result = {'artifact_verification': 'PASS', 'scientific_gate': 'FAIL',
              'scientific_verdict': 'DATA_INSUFFICIENT', 'actual_powershell_exit_code': run.returncode,
              'expected_stop_reproduced': True, 'tests_passed': 20, 'tests_failed': 0,
              'archived_files_unchanged': len(archive), 'archived_v1_unchanged': True,
              'final_holdouts_locked': True, 'command': command,
              'gate_sha256': base.digest(OUT / 'gate_result.json'),
              'tests_sha256': base.digest(OUT / 'tests.txt'),
              'reproduction_log_sha256': base.digest(OUT / 'reproduction.txt')}
    base.save(OUT / 'reproduction.json', result)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == '__main__':
    sys.exit(main())
