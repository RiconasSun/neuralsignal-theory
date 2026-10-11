"""Prospective R1 code/environment repair; preserve initial FAIL and all criteria."""
import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

import run_r1 as old

ORIGINAL_OUT = old.OUT
OUT = old.base.STUDY / 'results/R1_code1'
SUBPROCESS_RUN = old.subprocess.run
ADDED = ['scripts/predictive_models_code1.py', 'scripts/run_r1_code1.py',
         'tests/test_r1_code1.py', 'scripts/reproduce-r1-code1.ps1']


def register():
    old.OUT = ORIGINAL_OUT
    old.verify()
    for rel, sha in old.load(ORIGINAL_OUT / 'artifact_lock.json')['sha256'].items():
        if old.base.digest(old.base.ROOT / rel) != sha:
            raise RuntimeError(f'Original R1 failed artifact changed: {rel}')
    if (OUT / 'registration.json').exists():
        old.OUT = OUT
        old.verify()
        return
    obj = old.load(ORIGINAL_OUT / 'registration.json')
    obj['source_sha256'].update({f'paper11_v2/{rel}': old.base.digest(old.base.STUDY / rel) for rel in ADDED})
    obj['preceding_sha256'].update({str(p.relative_to(old.base.ROOT)).replace('\\', '/'): old.base.digest(p)
                                    for p in ORIGINAL_OUT.iterdir() if p.is_file()})
    obj.update({'registered_utc': datetime.now(timezone.utc).isoformat(),
                'code_repair': 'R1-CODE-1', 'original_failure_immutable': True,
                'before_repaired_tests_and_fits': True,
                'diagnosis': 'Original recurrent batch-size reset equality differed8.67361738e-19 due to batched arithmetic; sandbox temporary root denied nested directories. No score threshold exceeded was established, no controlled grid ran.',
                'change': 'Per-trial vector arithmetic gives identical recursion/readout independent of batch size. Unchanged original assertions/oracles run against new module; temporary fixtures use dedicated writable workspace directory.',
                'unchanged': 'All17original test methods/assertions, model targets, gradients, seeds, ridge grids, bounds, budgets and score accuracy1e-10 preserved. Extra batch-permutation regression added. No real cohort or holdout access.'})
    old.base.save(OUT / 'registration.json', obj, immutable=True)
    print('Registered R1-CODE-1 before rerun; original FAIL and sources preserved.')


def activate():
    old.OUT = OUT
    old.verify()
    import predictive_models_code1 as repaired
    sys.path.insert(0, str(old.base.STUDY / 'tests'))
    import test_r1_models as audit
    repaired.original.RecurrentPoisson = repaired.RecurrentPoisson
    audit.models = repaired.original
    def registered_tests(command, *args, **kwargs):
        command = list(command)
        if 'test_r1*.py' in command:
            command[command.index('test_r1*.py')] = 'test_r1_code1.py'
        return SUBPROCESS_RUN(command, *args, **kwargs)
    old.subprocess.run = registered_tests


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['register','execute','verify','replay'])
    action = parser.parse_args().action
    OUT.mkdir(parents=True, exist_ok=True)
    if action == 'register':
        register()
    else:
        activate()
        if action == 'verify':
            print('R1-CODE-1 and all original failed artifacts verified.')
        else:
            sys.exit(old.execute() if action == 'execute' else old.replay())
