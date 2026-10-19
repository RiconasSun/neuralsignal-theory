"""Reviewed, externally supervised A-only M2 source phases. No model/B/E path."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import h5py
import numpy as np
from .core import R, P, E, SourceStop, ResourceStop, load, sha, once, save_arrays, select_common, validate_item
from .transport import RangeReader, BudgetJournal, guard
from .neural_reader import read_a_source
from .windows_job import Job, require_job, resume_suspended
from .clock_bound import make_stage, verify_stage_environment, conservative_deadline

MISSION = 'P16-M2-M5-NEURAL-QC-AND-DEVELOPMENT-R3'
REVIEW_FILES = {'paper16_dev_r3/'+n for n in ['MISSION_SPEC.json', 'ACCESS_REGISTRATION.json', 'SOURCE_ACCESS_PLAN.md',
    'SOURCE_CANDIDATE_CERTIFICATES.json', 'core.py', 'neural_reader.py', 'transport.py', 'run_m2.py',
    'test_neural.py', 'test_transport.py', 'test_controller.py', 'test_integration.py', 'windows_job.py',
    'clock_bound.py', 'CLOCK_REPAIR_REGISTRATION.json']}
REVIEW_FILES |= {'ops/evidence/2026-10-19/p16-m2-m5-neural-qc-and-development-r3/'+n for n in
                 ['REQUIREMENT_BASELINE.json', 'goldenstandards.md', 'R2_REUSE_VERIFICATION.json', 'SYNTHETIC_PREACCESS_CLOCK_HOST.log']}


def phase_name(phase):
    if phase not in ['first', 'remaining']: raise SourceStop('Unknown phase denied before any source/claim')
    return phase


def verify_preaccess():
    reg = load(P/'ACCESS_REGISTRATION.json'); a = load(E/'PREACCESS_APPROVAL.json')
    if a.get('decision') != 'ACCEPTED_R3_A_ONLY_NEURAL_PREACCESS' or any(type(a.get(k)) is not int or a[k] != 0 for k in ['open_P0', 'open_P1']):
        raise SourceStop('Independent exact preaccess approval missing/failed')
    if not REVIEW_FILES <= set(a.get('reviewed_hashes', {})): raise SourceStop('Incomplete independently reviewed source/test/contract identities')
    for name, digest in a['reviewed_hashes'].items():
        path = (R/name).resolve(); path.relative_to(R)
        if sha(path) != digest: raise SourceStop('Preaccess reviewed identity changed: '+name)
    if sha(E/'PREACCESS_REVIEW.md') != a['report_sha256']: raise SourceStop('Preaccess review report identity')
    for name, digest in reg['old_pins'].items():
        if sha(R/name) != digest: raise SourceStop('Frozen prior source identity changed')
    if sha(P/'SOURCE_CANDIDATE_CERTIFICATES.json') != reg['source_candidates_manifest_sha256']:
        raise SourceStop('Frozen provider candidate metadata manifest mismatch')
    for manifest, count in [('paper16_m1/M1_FREEZE_MANIFEST.json', 334), ('paper16_dev/STOP_FREEZE_MANIFEST.json', 58),
                            ('paper16_linkdiag_r1/DIAGNOSTIC_FREEZE_MANIFEST.json', 100), ('paper16_running_r2/RUNNING_FREEZE_MANIFEST.json', 357)]:
        rows = load(R/manifest)['files']
        if len(rows) != count: raise SourceStop('Historical evidence denominator')
        for row in rows:
            path = R/row['path']
            if path.stat().st_size != row['bytes'] or sha(path) != row['sha256']: raise SourceStop('Historical source/evidence changed')
    return reg


def first_approval():
    a = load(E/'FIRST_SOURCE_APPROVAL.json')
    required = {'paper16_dev_r3/results/sources/750749662/'+n for n in ['ATTEMPT.json', 'RESULT.json', 'UNIT_QC.jsonl', 'VALUE_READS.json', 'NATIVE_LINK_AUDIT.json']}
    required |= {'paper16_dev_r3/results/'+n for n in ['STAGE_CLAIM.json', 'WORKER_first.json', 'SUPERVISION_first.json', 'BUDGET_FIRST.jsonl']}
    if a.get('decision') != 'ACCEPTED_R3_FIRST_A_SOURCE' or any(type(a.get(k)) is not int or a[k] != 0 for k in ['open_P0', 'open_P1']):
        raise SourceStop('Independent first actual source/A-only approval missing/failed')
    if not required <= set(a.get('reviewed_hashes', {})): raise SourceStop('Incomplete first actual source approval')
    if sha(E/'FIRST_SOURCE_REVIEW.md') != a['report_sha256']: raise SourceStop('First actual review identity')
    for name, value in a['reviewed_hashes'].items():
        path = (R/name).resolve(); path.relative_to(R)
        if sha(path) != value: raise SourceStop('First actual evidence identity changed')
    if not load(P/'results/SUPERVISION_first.json')['valid_completed_worker']: raise SourceStop('First external supervisor did not certify completion')
    if not load(P/'results/sources/750749662/RESULT.json')['source_pass']: raise SourceStop('First source mandatory failure')
    if not (P/'results/NEURAL_BUDGET.jsonl').read_bytes().startswith((P/'results/BUDGET_FIRST.jsonl').read_bytes()):
        raise SourceStop('First budget prefix changed')
    for line in (P/'results/sources/750749662/UNIT_QC.jsonl').read_text(encoding='utf8').splitlines():
        capture = json.loads(line)['private_A_capture']; path = (R/capture['private_path']).resolve()
        path.relative_to((P/'work/private/A/750749662').resolve())
        if sha(path) != capture['sha256']: raise SourceStop('Reviewed first private A state changed')


def source_inputs(item):
    # Explicit verified-package import; this function only reads frozen metadata, never invokes old acquisition.
    reg = load(P/'ACCESS_REGISTRATION.json')
    for name in ['paper16_running_r2/run_sources.py', 'paper16_running_r2/reader.py', 'paper16_running_r2/precision.py']:
        if sha(R/name) != reg['old_pins'][name]: raise SourceStop('Saved metadata utility version')
    from paper16_running_r2.run_sources import source_inputs as frozen_inputs
    header, starts, colors, valid, invalid, pins = frozen_inputs(item)
    path = R/pins['metadata_path']
    with np.load(path.with_suffix('.npz'), allow_pickle=False) as a:
        flashes = {name: a[name].copy() for name in ['start', 'stop', 'color', 'main_valid']}
    saved = P.parent/'paper16_running_r2/results'/str(item['session_id'])
    with np.load(saved/'DERIVED_RUNNING.npz', allow_pickle=False) as a:
        running = {name: a[name].copy() for name in a.files}
    original = load(saved/'RESULT.json')
    if original['status'] != 'SOURCE_RUNNING_PASS': raise SourceStop('R2 saved source not passed')
    # Exact keys/identities are inspected and tested before real access; no rounded event reconstruction.
    if not np.array_equal(starts.view('u8'), flashes['start'].view('u8')) or not np.array_equal(colors, flashes['color']) or not np.array_equal(valid, flashes['main_valid']):
        raise SourceStop('Frozen original native stimulus identity')
    return header, flashes, running, pins


def process_source(item, reg, stage, journal):
    validate_item(item, reg); guard(stage)
    folder = P/'results/sources'/str(item['session_id']); folder.mkdir(parents=True, exist_ok=True)
    once(folder/'ATTEMPT.json', {'mission': MISSION, 'status': 'STARTED', 'source': item,
         'time': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'phase': 'A_ONLY',
         'preaccess_approval_sha256': sha(E/'PREACCESS_APPROVAL.json'), 'registration_sha256': sha(P/'ACCESS_REGISTRATION.json')})
    header, flashes, running, pins = source_inputs(item)
    candidates = {(int(x['session_id']), int(x['unit_id'])): x for x in load(P/'SOURCE_CANDIDATE_CERTIFICATES.json')['candidates']}
    audit, reads = [], []; capture_paths = []
    private = P/'work/private/A'/str(item['session_id']); private.mkdir(parents=True, exist_ok=True)
    metrics = (folder/'UNIT_QC.jsonl').open('x', encoding='utf8', newline='\n')
    def persist(uid, arrays, record):
        guard(stage)
        path = private/(str(uid)+'.npz'); receipt = save_arrays(path, arrays)
        result = {'private_path': path.relative_to(R).as_posix(), **receipt}
        # This receipt contains only identities/aggregate QC, never raw neural array values.
        once(folder/f'A_CAPTURE_{uid}.json', {'unit_id': uid, 'A_only': True, **result})
        capture_paths.append(str(path.relative_to(R)))
        row = {**record, 'private_A_capture': result}
        metrics.write(json.dumps(row, allow_nan=False)+'\n'); metrics.flush(); os.fsync(metrics.fileno())
        return result
    reader = None
    try:
        with RangeReader(item, reg, stage, journal, P/'work/private/ranges') as reader:
            with h5py.File(reader, 'r') as file:
                result = read_a_source(file, item, reg, header, flashes, candidates, persist, audit, reads)
        guard(stage)
        selection = select_common(result['units'], flashes['color'], running['missing'], reg)
        guard(stage)
        once(folder/'VALUE_READS.json', reads); once(folder/'NATIVE_LINK_AUDIT.json', audit)
        final = {'mission': MISSION, 'source_pass': True, 'A_QC_complete': True, 'source': item,
                 'candidate_units_examined': len(result['units']), 'A_only_export': True, 'B_E_arrays_exported': False,
                 'native_objects': result['native_objects'], 'probe_metadata': result['probe_metadata'], 'selection': selection,
                 'source_metadata_pins': pins, 'UNIT_QC_sha256': sha(folder/'UNIT_QC.jsonl'),
                 'private_A_capture_count': len(capture_paths), 'source_requests_new': reader.calls,
                 'source_payload_bytes_new': reader.used, 'Final_C_access': False, 'Final_D_access': False,
                 'optimizer_attempts': 0, 'running_acquisition_calls': 0}
        once(folder/'RESULT.json', final)
        print(json.dumps({'session': item['session_id'], 'source_pass': True, 'A_admitted': selection['admitted'], 'candidates': len(result['units'])}), flush=True)
        return final
    except BaseException as exc:
        if not (folder/'VALUE_READS.json').exists(): once(folder/'VALUE_READS.json', reads)
        if not (folder/'NATIVE_LINK_AUDIT.json').exists(): once(folder/'NATIVE_LINK_AUDIT.json', audit)
        once(folder/'FAILURE.json', {'status': 'MANDATORY_SOURCE_OR_QC_STOP', 'error_type': type(exc).__name__,
             'message': str(exc), 'completed_private_A_captures': len(capture_paths),
             'source_requests_new': 0 if reader is None else reader.calls, 'source_payload_bytes_new': 0 if reader is None else reader.used,
             'no_retry': True, 'no_later_source_or_fit_authorized': True})
        raise
    finally: metrics.close()


def worker(phase):
    phase_name(phase)
    reg = verify_preaccess(); stage = load(P/'results/STAGE_CLAIM.json'); verify_stage_environment(stage)
    supervisor = load(P/'results'/f'SUPERVISOR_{phase}.claim.json')
    require_job(supervisor['job_name'])
    once(P/'results'/f'WORKER_{phase}.claim.json', {'worker_pid': os.getpid(), 'supervisor_pid': supervisor['supervisor_pid'],
         'immediate_parent_pid': os.getppid(), 'job_name': supervisor['job_name'], 'phase': phase})
    if phase == 'remaining': first_approval()
    objects = reg['objects'][:1] if phase == 'first' else reg['objects'][1:]
    journal = BudgetJournal(P/'results/NEURAL_BUDGET.jsonl', reg, append=phase == 'remaining')
    results = []
    try:
        for item in objects:
            guard(stage); results.append(process_source(item, reg, stage, journal))
        guard(stage)
        summary = {'phase': phase, 'completed_sources': len(results), 'all_sources_pass': True,
                   'new_neural_reserved_bytes_cumulative': journal.reserved, 'new_neural_payload_bytes_cumulative': journal.payload,
                   'requests_cumulative': sum(x['requests'] for x in journal.by_source.values()),
                   'per_source': journal.by_source, 'deadline_monotonic': stage['deadline_monotonic'],
                   'elapsed_seconds': time.monotonic()-stage['start_monotonic'], 'optimizer_attempts': 0}
        once(P/'results'/f'WORKER_{phase}.json', summary)
    finally: journal.close()


def supervise_child(command, deadline, log_path, job_name=None, stage=None):
    if stage is not None:
        verify_stage_environment(stage)
        deadline = min(deadline, conservative_deadline(stage))
    if time.monotonic() >= deadline: raise ResourceStop('External deadline expired before child launch')
    job_name = job_name or f'Local\\P16_R3_SYNTHETIC_{os.getpid()}_{time.time_ns()}'
    with Path(log_path).open('xb') as log:
        with Job(job_name) as job:
            process = subprocess.Popen(command, cwd=R, stdout=log, stderr=subprocess.STDOUT,
                                       creationflags=0x4)  # CREATE_SUSPENDED: assign before any descendant can exist.
            try:
                job.assign(process); resume_suspended(process)
                killed = False; clock_failure = None
                while process.poll() is None:
                    if stage is not None:
                        try: guard(stage)
                        except ResourceStop as exc:
                            clock_failure = str(exc); job.terminate(); killed = True; break
                    if time.monotonic() >= deadline:
                        job.terminate(); killed = True; break
                    time.sleep(min(.1, max(.001, deadline-time.monotonic())))
                code = process.wait()
            except BaseException:
                # If assignment failed the launcher is still suspended and has no descendants.
                if process.poll() is None: process.kill()
                process.wait(); raise
    if stage is not None:
        try: guard(stage)
        except ResourceStop as exc: clock_failure = str(exc)
    return {'returncode': code, 'killed_at_deadline': killed, 'completed_before_deadline': time.monotonic() < deadline and clock_failure is None,
            'clock_failure': clock_failure,
            'native_job_tree_enforced': True, 'assigned_before_resume': True, 'job_name': job_name}


def supervise(phase):
    phase_name(phase); reg = verify_preaccess()
    if phase == 'first':
        once(P/'results/STAGE_CLAIM.json', {'mission': MISSION,
             **make_stage(reg['resources']['development_wall_seconds_max']),
             'clock_repair_registration_sha256': sha(P/'CLOCK_REPAIR_REGISTRATION.json'),
             'registration_sha256': sha(P/'ACCESS_REGISTRATION.json')})
    else: first_approval()
    stage = load(P/'results/STAGE_CLAIM.json'); verify_stage_environment(stage)
    job_name = f'Local\\P16_R3_{phase}_{os.getpid()}_{time.time_ns()}'
    once(P/'results'/f'SUPERVISOR_{phase}.claim.json', {'phase': phase, 'supervisor_pid': os.getpid(), 'job_name': job_name, 'deadline_monotonic': stage['deadline_monotonic']})
    outcome = supervise_child([sys.executable, '-m', 'paper16_dev_r3.run_m2', 'worker', phase],
                              stage['deadline_monotonic'], E/f'NEURAL_{phase.upper()}_EXECUTION.log', job_name, stage)
    path = P/'results'/f'WORKER_{phase}.json'
    outcome['valid_completed_worker'] = bool(outcome['returncode'] == 0 and not outcome['killed_at_deadline'] and outcome['completed_before_deadline'] and path.exists())
    outcome['phase'] = phase; outcome['original_deadline_monotonic'] = stage['deadline_monotonic']
    outcome['log_sha256'] = sha(E/f'NEURAL_{phase.upper()}_EXECUTION.log')
    once(P/'results'/f'SUPERVISION_{phase}.json', outcome)
    if phase == 'first':
        journal_path = P/'results/NEURAL_BUDGET.jsonl'
        with (P/'results/BUDGET_FIRST.jsonl').open('xb') as target:
            target.write(journal_path.read_bytes() if journal_path.exists() else b''); target.flush(); os.fsync(target.fileno())
        once(P/'results/FIRST_JOURNAL_SNAPSHOT.json', {'journal_created': journal_path.exists(),
             'snapshot_sha256': sha(P/'results/BUDGET_FIRST.jsonl'), 'empty_does_not_certify_access_or_success': True})
    if not outcome['valid_completed_worker']: raise ResourceStop('Required source/supervision gate failed; stop/no retry')
    if phase == 'remaining':
        results = [load(P/'results/sources'/str(x['session_id'])/'RESULT.json') for x in reg['objects']]
        admitted = [x for x in results if x['selection']['admitted']]
        bo = sum(x['source']['protocol'] == 'brain_observatory_1.1' for x in admitted)
        fc = len(admitted)-bo
        gate = len(admitted) >= 14 and bo >= 3 and fc >= 10
        once(P/'results/M2_COHORT.json', {'source_pass': True, 'physiology_pass': gate, 'admitted_mice': len(admitted),
             'admitted_BO': bo, 'admitted_FC': fc, 'admitted': [{'mouse_id': x['source']['mouse_id'], 'session_id': x['source']['session_id'],
             'protocol': x['source']['protocol'], 'selected_unit_ids': x['selection']['selected_unit_ids']} for x in admitted],
             'source_results': [str((P/'results/sources'/str(x['session_id'])/'RESULT.json').relative_to(R)) for x in reg['objects']],
             'optimizer_attempts': 0, 'M3_authorized_to_begin': gate, 'Final_C_access': False, 'Final_D_access': False})
        if not gate: raise SourceStop('Original14/3/10 A-physiological admission failed; no predictive fitting')
    print(json.dumps(outcome), flush=True)


if __name__ == '__main__':
    if len(sys.argv) != 3 or sys.argv[1] not in ['supervise', 'worker']:
        raise SourceStop('Only exact registered source commands')
    phase_name(sys.argv[2])
    {'supervise': supervise, 'worker': worker}[sys.argv[1]](sys.argv[2])
