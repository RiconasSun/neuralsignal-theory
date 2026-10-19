"""Saved stop evidence only: no native source reopen, fitting or assessment."""
from pathlib import Path
import contextlib
import csv
import hashlib
import json
import os
import subprocess
import sys
import unittest
import urllib.request
import h5py
import numpy as np
import requests
from paper16_m1.code.verify import validate_manifest

R = Path(__file__).resolve().parents[1]
P = R / 'paper16_dev'
E = R / 'ops/evidence/2026-10-18/p16-m2-m5-native-qc-and-development'
BASE = '020388b6a8ed35d7fcba817e5f2bad4412b3dc02'
EXPECTED_PAYLOAD = ('paper16_dev/.gitignore', 'paper16_dev/A1_A10_CLAIM_AUDIT.md', 'paper16_dev/B1_SELECTION.json', 'paper16_dev/BUDGET_FORMULA_AUDIT.json', 'paper16_dev/CONTROL_STATUS.csv', 'paper16_dev/DEVELOPMENT_ADMISSION.csv', 'paper16_dev/DEVELOPMENT_STATUS.json', 'paper16_dev/E_REPORT.md', 'paper16_dev/FIT_LEDGER_SUMMARY.json', 'paper16_dev/M2_ACCESS_REGISTRATION.json', 'paper16_dev/M2_ACCESS_REPAIR_1.json', 'paper16_dev/m2_core.py', 'paper16_dev/M4_MAIN_PLANNED_TASKS.csv', 'paper16_dev/MISSION_SPEC.json', 'paper16_dev/NUMERICAL_CERTIFICATION_STATUS.json', 'paper16_dev/README.md', 'paper16_dev/READONLY_FINAL_HANDOFF.md', 'paper16_dev/reproduce.ps1', 'paper16_dev/requirements.txt', 'paper16_dev/results/M2_RUNNING_ATTEMPT.json', 'paper16_dev/results/M2_RUNNING_SUPERVISION.json', 'paper16_dev/results/running/750749662.attempt.json', 'paper16_dev/results/running/750749662.failure.json', 'paper16_dev/SENSITIVITY_PLANNED_TASKS.csv', 'paper16_dev/SOURCE_BEHAVIOR_REPORT.md', 'paper16_dev/source_running.py', 'paper16_dev/STOP_REPORT.md', 'paper16_dev/test_m2.py', 'paper16_dev/test_saved_stop.py', 'paper16_dev/TIMEBASE_OBSERVATION_CERTIFICATE.md', 'paper16_dev/verify_saved.py', 'ops/evidence/2026-10-18/p16-m2-m5-native-qc-and-development/OWNER_REQUEST.txt', 'ops/evidence/2026-10-18/p16-m2-m5-native-qc-and-development/baseline.json', 'ops/evidence/2026-10-18/p16-m2-m5-native-qc-and-development/M1_FREEZE_AUDIT.json', 'ops/evidence/2026-10-18/p16-m2-m5-native-qc-and-development/M2_ACCESS_REGISTRATION_INITIAL.json', 'ops/evidence/2026-10-18/p16-m2-m5-native-qc-and-development/M2_MASK_BOUND_CLARIFICATION.json', 'ops/evidence/2026-10-18/p16-m2-m5-native-qc-and-development/M2_RUNNING_ACCESS_REVIEW_1.md', 'ops/evidence/2026-10-18/p16-m2-m5-native-qc-and-development/M2_RUNNING_ACCESS_REVIEW_2.md', 'ops/evidence/2026-10-18/p16-m2-m5-native-qc-and-development/M2_RUNNING_ACCESS_REVIEW.md', 'ops/evidence/2026-10-18/p16-m2-m5-native-qc-and-development/M2_RUNNING_ACCESS_APPROVAL.json', 'ops/evidence/2026-10-18/p16-m2-m5-native-qc-and-development/M2_SAVED_STOP_DIAGNOSIS_REVIEW.md', 'ops/evidence/2026-10-18/p16-m2-m5-native-qc-and-development/REJECTED_M2_ACCESS_1_CANDIDATE.zip', 'ops/evidence/2026-10-18/p16-m2-m5-native-qc-and-development/REJECTED_M2_ACCESS_1_RECEIPT.json', 'ops/evidence/2026-10-18/p16-m2-m5-native-qc-and-development/M2_ACCESS_REPAIR_1.md', 'ops/evidence/2026-10-18/p16-m2-m5-native-qc-and-development/M2_SYNTHETIC_1.log', 'ops/evidence/2026-10-18/p16-m2-m5-native-qc-and-development/M2_SYNTHETIC_2.log', 'ops/evidence/2026-10-18/p16-m2-m5-native-qc-and-development/M2_SYNTHETIC_3.log', 'ops/evidence/2026-10-18/p16-m2-m5-native-qc-and-development/M2_SYNTHETIC_4.log', 'ops/evidence/2026-10-18/p16-m2-m5-native-qc-and-development/M2_RUNNING_EXECUTION_1.log', 'ops/evidence/2026-10-18/p16-m2-m5-native-qc-and-development/IMPLEMENTATION_TOOLING_RECEIPT.md', 'ops/evidence/2026-10-18/p16-m2-m5-native-qc-and-development/CODE_WRAPPER_DRY_RUN.log', 'ops/evidence/2026-10-18/p16-m2-m5-native-qc-and-development/CODE_WRAPPER_DRY_RUN_2.log', 'ops/evidence/2026-10-18/p16-m2-m5-native-qc-and-development/CODE_WRAPPER_EXECUTION_1.log', 'paper16_m1/M1_FREEZE_MANIFEST.json', 'paper16_m0/results/ROLE_ALLOCATION.json', 'ops/evidence/2026-10-18/p16-m2-m5-native-qc-and-development/SAVED_REPRODUCTION_1.log', 'ops/evidence/2026-10-18/p16-m2-m5-native-qc-and-development/REJECTED_SAVED_REPRO_1_CANDIDATE.zip', 'ops/evidence/2026-10-18/p16-m2-m5-native-qc-and-development/REJECTED_SAVED_REPRO_1_RECEIPT.json')


def read(path):
    return json.loads(Path(path).read_text(encoding='utf8'))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


@contextlib.contextmanager
def saved_scope():
    request, urlopen, file, load, popen = requests.Session.request, urllib.request.urlopen, h5py.File, np.load, subprocess.Popen
    def deny(*args, **kwargs):
        raise RuntimeError('Live source/neural access denied in saved stop reproduction')
    def synthetic(name, mode='r', **kwargs):
        if not isinstance(name, (str, os.PathLike)) or mode != 'w' or kwargs.get('driver') != 'core' or kwargs.get('backing_store') is not False:
            raise RuntimeError('Only nonpersistent synthetic HDF5 permitted')
        path = Path(name).resolve()
        path.relative_to((P/'work').resolve())
        if path.suffix != '.h5':
            raise RuntimeError('Native NWB access denied')
        return file(name, mode, **kwargs)
    class GuardedPopen(popen):
        def __init__(self, args, *a, **kw):
            if not isinstance(args, (list, tuple)):
                raise RuntimeError('Unstructured subprocess denied')
            readonly = args[0] == 'git' and len(args) > 1 and args[1] in ['ls-tree', 'show', 'diff', 'status', 'rev-parse']
            fixture = len(args) >= 3 and args[0] == sys.executable and args[1] == '-c' and args[2] in ['import time; time.sleep(60)', 'pass', 'raise SystemExit(2)']
            if not (readonly or fixture):
                raise RuntimeError('Only fixed synthetic subprocess/read-only local Git allowed')
            super().__init__(args, *a, **kw)
    requests.Session.request, urllib.request.urlopen, h5py.File, np.load, subprocess.Popen = deny, deny, synthetic, deny, GuardedPopen
    try:
        yield
    finally:
        requests.Session.request, urllib.request.urlopen, h5py.File, np.load, subprocess.Popen = request, urlopen, file, load, popen


def checks():
    assert sys.version.split()[0] == '3.11.15' and np.__version__ == '2.4.6' and h5py.__version__ == '3.16.0' and requests.__version__ == '2.32.5'
    validate_manifest(R, read(P/'STOP_FREEZE_MANIFEST.json')['files'], EXPECTED_PAYLOAD)
    upstream = read(R/'paper16_m1/M1_FREEZE_MANIFEST.json')
    for x in upstream['files']:
        assert sha(R/x['path']) == x['sha256'] and (R/x['path']).stat().st_size == x['bytes']
    reg = read(P/'M2_ACCESS_REGISTRATION.json')
    assert len(reg['objects']) == 28 and len(reg['denied_final_session_ids']) == 27
    assert len({x['mouse_id'] for x in reg['objects']}) == 28
    assert sum(x['protocol'] == 'brain_observatory_1.1' for x in reg['objects']) == 5
    assert sum(x['protocol'] == 'functional_connectivity' for x in reg['objects']) == 23
    attempts = list((P/'results/running').glob('*.attempt.json'))
    failures = list((P/'results/running').glob('*.failure.json'))
    assert len(attempts) == len(failures) == 1 and attempts[0].name == '750749662.attempt.json'
    failure = read(failures[0]); supervision = read(P/'results/M2_RUNNING_SUPERVISION.json')
    assert failure['error'] == 'ValueError: External/soft/noncanonical source link denied'
    assert failure['dataset_paths_read'] == ['/identifier', '/session_start_time', '/timestamps_reference_time']
    assert len(failure['ranges']) == 39 and sum(x['bytes'] for x in failure['ranges']) == failure['transport_bytes'] == 81912
    assert failure['reserved_bytes'] == 81951 and all(0 < x['bytes'] <= 1048576 and len(x['sha256']) == 64 for x in failure['ranges'])
    assert supervision['child_exit'] == 1 and supervision['valid_source_stage'] is False and supervision['child_killed'] is False
    assert supervision['completed'] < supervision['deadline'] and supervision['deadline'] - supervision['started'] == 14400
    assert not (P/'results/M2_RUNNING_GATE.json').exists() and not list((P/'results').rglob('*.npz'))
    approval = read(E/'M2_RUNNING_ACCESS_APPROVAL.json')
    assert approval['decision'] == 'ACCEPTED_M2_RUNNING_ONLY' and approval['report_sha256'] == sha(E/'M2_RUNNING_ACCESS_REVIEW.md')
    for path, digest in approval['reviewed_hashes'].items():
        assert sha(R/path) == digest
    status = read(P/'DEVELOPMENT_STATUS.json')
    assert status['FINAL_STATUS'] == 'STOP_SOURCE_OR_QC' and status['DEVELOPMENT_ATTEMPTS_USED'] == 0
    assert all(status[x] is False for x in ['M2_SOURCE_VALIDITY_PASS', 'M2_RUNNING_SEMANTICS_PASS', 'M2_PHYSIOLOGICAL_QC_PASS',
               'M3_PRODUCTION_NUMERICAL_PASS', 'M4_B1_SELECTION_COMPLETE', 'M4_ALL_MODEL_FITS_COMPLETE', 'M5_E_ASSESSMENT_COMPLETE',
               'FINAL_C_ACCESS', 'FINAL_D_ACCESS', 'PROMPT_4_READY'])
    assert all(status[x] is None for x in ['DEVELOPMENT_ADMITTED_MICE','DEVELOPMENT_ADMITTED_BO','DEVELOPMENT_ADMITTED_FC','FROZEN_LAMBDA','PRIMARY_DEVELOPMENT_EFFECT'])
    assert all(x is None for x in status['SECONDARY_DEVELOPMENT_EFFECTS'].values())
    cohorts = list(csv.DictReader((P/'DEVELOPMENT_ADMISSION.csv').open(encoding='utf8', newline='')))
    assert len(cohorts) == 28 and sum(x['source_running_status'] == 'SOURCE_LINK_CHECK_STOP' for x in cohorts) == 1
    assert {int(x['session_id']) for x in cohorts} == {x['session_id'] for x in reg['objects']}
    assert all(x['admitted'] == '' and x['selected_unit_ids'] == '' and x['exposure_seconds_A'] == '' for x in cohorts)
    for name, count in [('M4_MAIN_PLANNED_TASKS.csv',1736),('SENSITIVITY_PLANNED_TASKS.csv',6720)]:
        rows = list(csv.DictReader((P/name).open(encoding='utf8', newline='')))
        assert len(rows) == count and all(x['status'] == 'NOT_ATTEMPTED_PREREQUISITE_M2_FAILED' and x['activated'] == 'False' and x['selected_unit_id'] == 'NOT_SELECTED' for x in rows)
    budget = read(P/'BUDGET_FORMULA_AUDIT.json')
    assert budget['Development_all28_upper_bound'] == 8456 and budget['future_Final_all27_reserved_upper_bound'] == 7722 and budget['total'] == 16178
    controls = list(csv.DictReader((P/'CONTROL_STATUS.csv').open(encoding='utf8', newline='')))
    assert {x['id'] for x in controls} == {f'S{i:02}' for i in range(1,13)} | {f'N{i}' for i in range(1,5)}
    assert all(x['status'] == 'NOT_RUN_PREREQUISITE_M2_FAILED' and x['fit_or_reference_attempts'] == '0' for x in controls)
    changed = subprocess.check_output(['git', 'diff', '--name-only', BASE], cwd=R).decode().splitlines()
    originals = set(subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', BASE], cwd=R).decode().splitlines())
    assert not (set(changed) & originals - {'ops/daily-operations.md'})
    assert (R/'ops/daily-operations.md').read_bytes().endswith(subprocess.check_output(['git', 'show', BASE+':ops/daily-operations.md'], cwd=R))
    print(json.dumps({'FINAL_STATUS':'STOP_SOURCE_OR_QC','frozen_stop_payloads':len(EXPECTED_PAYLOAD),'M1_frozen_payloads':len(upstream['files']),
          'source_attempts':1,'source_failed':1,'source_unattempted':27,'payload_bytes':81912,'reserved_bytes':81951,
          'running_values_decoded':0,'new_neural_arrays':0,'real_model_fits':0,'Final_C_D':False,'planned_unactivated_fit_slots':8456}))


def main():
    with saved_scope():
        checks()
        suite = unittest.TestSuite(unittest.defaultTestLoader.loadTestsFromName(x) for x in ['paper16_dev.test_m2','paper16_dev.test_saved_stop'])
        result = unittest.TextTestRunner(verbosity=2).run(suite)
        if not result.wasSuccessful():
            raise SystemExit(1)


if __name__ == '__main__':
    main()
