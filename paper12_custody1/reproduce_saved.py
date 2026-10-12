"""Saved-evidence verification only: no source access, keys, neural data or fitting."""
import json
from pathlib import Path
import subprocess
import sys
from datetime import datetime, timezone
import register as r


def main():
    manifest_path = r.HERE / 'final_source_manifest.json'
    if manifest_path.exists():
        manifest = r.load(manifest_path)
        for name, digest in manifest['sha256'].items():
            if r.sha(r.HERE / name) != digest:
                raise RuntimeError('SAVED_MISSION_EVIDENCE_CHANGED:' + name)
    output = r.HERE / 'replay'
    output.mkdir(exist_ok=True)
    commands = [
        [sys.executable, str(r.HERE / 'register.py'), '--verify'],
        [sys.executable, '-m', 'unittest', 'discover', '-s', str(r.HERE), '-p', 'test_*.py', '-v'],
        [sys.executable, str(r.HERE / 'aggregate4.py')],
    ]
    results = []
    for number, command in enumerate(commands):
        completed = subprocess.run(command, cwd=r.ROOT, capture_output=True, text=True)
        log = output / ('check_%02d.log' % number)
        log.write_text(completed.stdout + completed.stderr, encoding='utf-8')
        results.append(dict(command=command, exit_code=completed.returncode,
                            log=str(log.relative_to(r.HERE)), sha256=r.sha(log)))
        if completed.returncode != 0:
            break
    gate = r.load(r.HERE / 'results/M2/aggregate4/gate_result.json') if all(x['exit_code'] == 0 for x in results) else None
    receipt = dict(utc=datetime.now(timezone.utc).isoformat(), checks=results,
                   saved_checks_pass=len(results) == len(commands) and all(x['exit_code'] == 0 for x in results),
                   scope='Saved evidence hashes, fixture/regression tests and public QC aggregation only',
                   live_security_rerun=False, data_extraction_rerun=False, experiments_reproduced=False,
                   final_holdout_accessed=False, saved_M2_gate=gate['gate'] if gate else None)
    receipt['saved_manifest_verified'] = manifest_path.exists()
    r.save(output / 'reproduction_receipt.json', receipt)
    print(json.dumps(receipt, indent=2))
    if not receipt['saved_checks_pass']:
        sys.exit(1)


if __name__ == '__main__':
    main()
