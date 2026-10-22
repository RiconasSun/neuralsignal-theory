"""Focused synthetic parser/order proofs; never run real saved reproduction."""
import datetime
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
from unittest.mock import patch

E = Path(__file__).resolve().parent

def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def sha(path):
    with path.open('rb') as stream: return hashlib.file_digest(stream, 'sha256').hexdigest()

def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding='utf8')

reproducer = load_module('independent_saved_tool_review', E / 'reproduce_saved.py')
builder = load_module('independent_archive_tool_review', E / 'build_archive.py')
sources = {name: sha(E / name) for name in ['reproduce_saved.py', 'build_archive.py']}
proofs = []
temp_parent = E / 'INDEPENDENT_TOOLING_SYNTHETIC_TEMP'
temp_parent.mkdir(exist_ok=True)
with tempfile.TemporaryDirectory(prefix='review_', dir=temp_parent) as temporary:
    root = Path(temporary).resolve()
    assert root.parent == temp_parent.resolve() and root.name.startswith('review_')
    journal = root / 'unterminated.jsonl'
    journal.write_text('{"event":"COMPLETED"}', encoding='utf8')
    accepted = reproducer.lines(journal)
    assert accepted == [{'event': 'COMPLETED'}]
    proofs.append({'finding': 'P1-JOURNAL-TERMINATOR', 'scope': 'SYNTHETIC_ONLY',
                   'observed': 'Unterminated JSON journal row is accepted as a full row',
                   'original_bytes_have_terminal_LF': False, 'accepted_rows': len(accepted)})

    class FilesystemResolutionReached(RuntimeError): pass
    resolution_attempts = []
    def resolved(path, *args, **kwargs):
        resolution_attempts.append(str(path))
        raise FilesystemResolutionReached('Synthetic trap; no real filesystem resolution or network')
    with patch.object(Path, 'resolve', resolved):
        try:
            builder.relative(Path('//synthetic-host/share/not-local.json'))
        except FilesystemResolutionReached:
            pass
        else:
            raise AssertionError('Expected current builder to reach resolution before rejecting lexical path')
    assert len(resolution_attempts) == 1
    proofs.append({'finding': 'P1-ARCHIVE-BOUNDARY-ORDER', 'scope': 'SYNTHETIC_NO_NETWORK_TRAP',
                   'observed': 'Builder relative() invokes filesystem resolution before lexical local-path rejection',
                   'actual_network_access': False, 'resolution_calls_trapped': len(resolution_attempts)})

    p = root / 'synthetic_p5'
    stage = {'mission': reproducer.MISSION, 'phase': 'B_A_M4', 'no_reset': True,
             'start_UTC': '2020-01-01T00:00:00+00:00', 'deadline_UTC': '2020-01-03T00:00:00+00:00',
             'start_monotonic': 1., 'deadline_monotonic': 172801., 'windows_boot_UTC': 'SYNTHETIC_BOOT'}
    write(p / 'results/STAGE_CLAIM.json', stage)
    write(p / 'PHASE_A_CLAIM.json', {'windows_boot_UTC': 'SYNTHETIC_BOOT'})
    write(p / 'results/SUPERVISOR.json', {'stage_sha256': sha(p / 'results/STAGE_CLAIM.json'),
                                         'supervisor_pid': 'not-an-integer', 'job_name': 'INVALID_PRODUCER_JOB'})
    write(p / 'results/SUPERVISION.json', {'returncode': 0, 'killed_at_deadline': False,
                                         'completed_before_deadline': True, 'native_job_tree_enforced': True,
                                         'assigned_before_resume': True, 'job_name': 'INVALID_PRODUCER_JOB'})
    with patch.object(reproducer, 'P', p):
        _, accepted_native = reproducer.stage_and_native()
    assert accepted_native['returncode'] == 0
    proofs.append({'finding': 'P1-NATIVE-STOP-BINDING', 'scope': 'SYNTHETIC_NATIVE_METADATA_ONLY',
                   'observed': 'Reproducer native helper accepts producer-invalid Job naming and supervisor PID type',
                   'actual_native_process_or_scientific_state_used': False})

for name, expected in sources.items():
    assert sha(E / name) == expected
record = {'mission': reproducer.MISSION, 'reviewer': '/root/r4_interruption_review',
          'recorded_UTC': datetime.datetime.now(datetime.timezone.utc).isoformat(),
          'source_sha256': sources, 'proofs': proofs,
          'result': 'THREE_TOOLING_P1_FINDINGS_REPRODUCED_OR_STATICALLY_CONFIRMED',
          'full_real_reproduction_executed': False, 'real_saved_state_arrays_read': 0,
          'scientific_model_imports_or_calls': 0, 'objective_gradient_AD_FD_score_minimize_calls': 0,
          'network_access': False, 'running_observer_or_producer_modified': False}
target = E / 'INDEPENDENT_SAVED_TOOLING_REVIEW_CHECK_RESULT_1.json'
with target.open('x', encoding='utf8', newline='\n') as stream:
    json.dump(record, stream, indent=2, allow_nan=False); stream.write('\n')
print(json.dumps({'result_sha256': sha(target), 'proofs': len(proofs), 'actual_scientific_calls': 0}))
