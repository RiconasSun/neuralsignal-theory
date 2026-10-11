"""Combined R0 gate: source integrity, metadata lock, and usable development cohort."""
import argparse
import json
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import run_r0 as base
import run_r0_schema as schema

OUT = base.STUDY / 'results/R0_final'


def usable_coverage(sessions, minimum_trials=40):
    rows = []
    for key, session in sorted(sessions.items()):
        parts = session['partitions']
        train, validation, forbidden = map(set, (parts['train'], parts['validation'], parts['test']))
        if train & validation or (train | validation) & forbidden:
            raise RuntimeError(f'Partition overlap: {key}')
        rows.append({'session': key, 'subject': key.split('/')[0], 'train': len(train),
                     'validation': len(validation), 'forbidden_test': len(forbidden),
                     'usable_trials': len(train | validation),
                     'meets_trial_requirement': len(train | validation) >= minimum_trials})
    upper = sorted({r['subject'] for r in rows if r['meets_trial_requirement']})
    return rows, upper


def registration():
    target = OUT / 'registration.json'
    paths = [Path(__file__), base.STUDY / 'tests/test_r0_preflight.py',
             base.STUDY / 'scripts/reproduce.ps1']
    if target.exists():
        obj = json.loads(target.read_text())
        for rel, sha in obj['input_sha256'].items():
            if base.digest(base.ROOT / rel) != sha:
                raise RuntimeError(f'Combined-gate source changed: {rel}')
        return obj
    schema.verify()
    obj = {'study': 'P11-v2', 'milestone': 'R0', 'registered_utc': datetime.now(timezone.utc).isoformat(),
           'purpose': 'Evaluate all R0 conditions, not only external candidate coverage',
           'before_model_or_spike_access': True,
           'prior_metadata_exposure': 'Primary split lengths already inspected. No new model/count outcome access. This audit applies existing registered minimums rather than optimizing an eligibility threshold.',
           'criterion': 'At least8 development patients, each with one eligible session with at least40 usable train+validation trials. Old forbidden test cannot supply trial coverage for the v2 study. Unit/rate QC can only reduce this upper bound.',
           'denominator_limit': 'Original protocol did not explicitly distinguish total recorded vs usable trials. Conservatively apply usable trials; do not reinterpret to pass. A change requires a prospective human-approved amendment before model/count access.',
           'source_support': 'Descriptor https://www.nature.com/articles/s41597-020-0415-9 describes continuously acquired recordings and stable isolated units during the task. Eligible external1s windows fall within >=2.502144s stimulus presentations. No unit obs_intervals in any87 NWB files; no dropout-mask verification claimed. R2 must resolve source-supported observation coverage before any counts and must never infer it from first/last spikes.',
           'input_sha256': {str(p.relative_to(base.ROOT)).replace('\\', '/'): base.digest(p) for p in paths}}
    base.save(target, obj, immutable=True)
    return obj


def run():
    registration()
    schema.verify()
    protocol = json.loads((base.STUDY / 'protocol/protocol.json').read_text())
    splits = json.loads((base.ROOT / 'paper11/data_manifest/M1/trial_splits.json').read_text())
    rows, patients = usable_coverage(splits['sessions'], protocol['eligibility']['minimum_valid_trials_session'])
    ext = json.loads((schema.OUT / 'gate_result.json').read_text())
    unit_gate_upper_pass = len(patients) >= protocol['eligibility']['minimum_subjects_development']
    target = OUT / 'artifact_lock.json'
    artifacts = {str(p.relative_to(base.ROOT)).replace('\\', '/'): base.digest(p)
                 for folder in [base.OUT, schema.OUT] for p in sorted(folder.rglob('*.json'))}
    if target.exists():
        if json.loads(target.read_text())['sha256'] != artifacts:
            raise RuntimeError('Saved metadata/provenance artifacts changed')
    else:
        base.save(target, {'sha256': artifacts}, immutable=True)
    tests = subprocess.run([sys.executable, '-m', 'unittest', 'discover', '-s', str(base.STUDY / 'tests'), '-p', 'test_r0*.py', '-v'], capture_output=True, text=True)
    (OUT / 'tests.txt').write_text(tests.stdout + tests.stderr, encoding='utf-8')
    result = {'study': 'P11-v2', 'milestone': 'R0',
              'gate_verdict': 'PASS' if unit_gate_upper_pass and ext['gate_verdict'] == 'PASS' and tests.returncode == 0 else 'FAIL',
              'scientific_verdict': 'NOT_EVALUATED' if unit_gate_upper_pass else 'DATA_INSUFFICIENT',
              'execution_exit_class': 'WAIT_FOR_HUMAN_INPUT' if not unit_gate_upper_pass else 'CONTINUE_EXECUTION',
              'reason': 'Only2 development subjects can meet the registered40 usable trials/session; minimum8. External metadata adequacy cannot compensate.',
              'development_candidate_upper_bound': len(patients), 'development_candidate_subjects': patients,
              'minimum_development_subjects': protocol['eligibility']['minimum_subjects_development'],
              'minimum_usable_trials_per_session': protocol['eligibility']['minimum_valid_trials_session'],
              'development_session_metadata': rows, 'external_metadata_subgate': ext['gate_verdict'],
              'external_candidate_subjects': ext['candidate_subject_count'],
              'external_candidate_sessions': ext['eligible_session_count'],
              'tests_exit_code': tests.returncode, 'archived_v1_unchanged': True,
              'new_neural_values_accessed': False, 'external_final_locked': True, 'old_final_test_locked': True,
              'R1_R2_R3_executed': False, 'source_identity': registration()['input_sha256'],
              'artifact_lock_sha256': base.digest(target), 'finished_utc': datetime.now(timezone.utc).isoformat(),
              'next_action': 'Human decision: retain registered40 usable-trial minimum and stop, or authorize a prospective eligibility amendment for this distinct v2 study. Never reclassify v1 gates or use old final test.'}
    base.save(OUT / 'gate_result.json', result)
    base.save(OUT / 'QC.json', result)
    import numpy, scipy, h5py, requests
    base.save(OUT / 'environment.json', {'python': sys.version, 'executable': sys.executable,
             'platform': platform.platform(), 'numpy': numpy.__version__, 'scipy': scipy.__version__,
             'h5py': h5py.__version__, 'requests': requests.__version__})
    print(json.dumps({k: v for k, v in result.items() if k != 'development_session_metadata'}, indent=2))
    return 0 if result['gate_verdict'] == 'PASS' else 2


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['register', 'run'])
    args = parser.parse_args()
    if args.action == 'register':
        registration()
        print('Combined R0 gate registered, unchanged thresholds and no model/count access.')
        sys.exit(0)
    sys.exit(run())
