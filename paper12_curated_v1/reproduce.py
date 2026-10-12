"""Offline audit replay, not neural-study reproduction."""
import json
import subprocess
import sys
from datetime import datetime, timezone
import register as r
import closeout


def verify_seal():
    record = r.load(r.HERE / 'seal.json')
    for path, value in record['sha256'].items():
        if r.sha(r.HERE / path) != value:
            raise RuntimeError('Stopped candidate drift: ' + path)
    return r.sha(r.HERE / 'seal.json')


def main():
    started = datetime.now(timezone.utc).isoformat()
    seal = verify_seal()
    reg = r.verify()
    output = r.HERE / 'replay'
    output.mkdir(exist_ok=True)
    closeout.main(output)
    parities = {}
    for name in ('mouse_evidence.csv', 'summary.json', 'gate_result.json'):
        old, fresh = r.sha(r.HERE / 'results/closeout' / name), r.sha(output / name)
        if old != fresh:
            raise RuntimeError('Saved output parity failed: ' + name)
        parities[name] = fresh
    command = [sys.executable, '-m', 'unittest', 'discover', '-s', str(r.HERE), '-p', 'test_*.py', '-v']
    run = subprocess.run(command, cwd=r.ROOT, capture_output=True, text=True)
    (output / 'tests.log').write_text(run.stdout + run.stderr, encoding='utf-8')
    print(run.stdout + run.stderr, flush=True)
    if run.returncode:
        raise RuntimeError('Regression tests failed')
    r.verify()
    if verify_seal() != seal:
        raise RuntimeError('Candidate edited during replay')
    receipt = {'mission': r.MISSION, 'started_utc': started, 'finished_utc': datetime.now(timezone.utc).isoformat(),
               'HEAD': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=r.ROOT).decode().strip(),
               'candidate_identity': 'seal SHA256 binds relevant source/input/results; HEAD may be precommit',
               'seal_sha256': seal, 'registration_sha256': r.sha(r.HERE / 'registration.json'),
               'python': sys.version, 'executable': sys.executable, 'test_command': command, 'tests_exit_code': run.returncode,
               'parities': parities, 'network_requests': 0, 'neural_values_decoded': 0, 'model_fits': 0,
               'final_evaluations': 0, 'prior_files_verified': len(reg['prior_sha256']),
               'reproduction_scope': 'Saved metadata/schema stopped-evidence audit only; M2neural QC and M3-M7 not executed'}
    r.save(output / 'reproduction_result.json', receipt)
    print(json.dumps(receipt), flush=True)


if __name__ == '__main__':
    main()
