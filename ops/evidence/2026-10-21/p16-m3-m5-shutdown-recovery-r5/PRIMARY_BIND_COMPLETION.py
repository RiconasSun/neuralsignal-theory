"""Bind already-completed native audit metadata; never rescan scientific states."""
import datetime
import hashlib
import json
import os
from pathlib import Path

R = Path(__file__).resolve().parents[4]
E = Path(__file__).resolve().parent
P = R/'paper16_development_r5'


def sha(path):
    with path.open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def load(path):
    return json.loads(path.read_bytes())


reg = load(E/'PRIMARY_AUDIT_V2_REGISTRATION.json')
result = load(P/'PRIMARY_AUDIT_V2_RESULT.json')
runtime = load(R/'paper16_development_r4/RUNTIME_IDENTITY.json')
assert result['primary_saved_audit']=='PASS'
assert result['optimizer_passed']==3992 and result['B0_passed']==216
assert sha(R/reg['script_path'])==reg['script_sha256']
assert sha(P/'PHASE_A_CLAIM.json')==reg['phase_claim_sha256']
assert sha(R/runtime['runtime_executable'])==runtime['python_launcher_sha256']
proof = {
    'mission': result['mission'],
    'recorded_UTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'actual_native_invocation': {
        'cwd':str(R),
        'executable':runtime['runtime_executable'],
        'arguments':['-u','-c',"import runpy,pathlib; runpy.run_path(str(pathlib.Path('ops/evidence/2026-10-21/p16-m3-m5-shutdown-recovery-r5/PRIMARY_SAVED_AUDIT_V2.py').resolve()),run_name='__main__')"],
        'stdout_stderr':'ops/evidence/2026-10-21/p16-m3-m5-shutdown-recovery-r5/PRIMARY_AUDIT_NATIVE_5_V2.log',
        'tool_session_id':39703,
        'observed_actual_exit_code':0,
        'exit_observation':'functions.write_stdin completed session 39703 with exit_code=0',
        'escalation_scope':'actual Windows CIM boot verification and saved-only frozen A audit'
    },
    'runtime':runtime,
    'registration_sha256':sha(E/'PRIMARY_AUDIT_V2_REGISTRATION.json'),
    'result_sha256':sha(P/'PRIMARY_AUDIT_V2_RESULT.json'),
    'result':result,
    'source_sha256':reg['script_sha256'],
    'native_log_sha256':sha(E/'PRIMARY_AUDIT_NATIVE_5_V2.log'),
    'incident_review_path':'ops/evidence/2026-10-21/p16-m3-m5-shutdown-recovery-r5/INDEPENDENT_R5_PRIMARY_HARNESS_INCIDENT_REVIEW.md',
    'incident_review_sha256':sha(E/'INDEPENDENT_R5_PRIMARY_HARNESS_INCIDENT_REVIEW.md'),
    'source_diff_sha256':sha(E/'PRIMARY_V2_SOURCE_DIFF.patch'),
    'original_registration_sha256':sha(E/'PRIMARY_AUDIT_REGISTRATION.json'),
    'all_original_attempt_logs_preserved':True,
    'no_scientific_state_rescan_after_complete':True,
    'independent_complete_admission_pending':True
}
with (E/'PRIMARY_NATIVE_COMPLETION_PROOF.json').open('x',encoding='utf8',newline='\n') as f:
    json.dump(proof,f,indent=2,allow_nan=False)
    f.write('\n');f.flush();os.fsync(f.fileno())
print(json.dumps({'native_completion_proof':'PASS','scientific_states_rescanned':0,'new_numerical_evaluations':0,'proof_sha256':sha(E/'PRIMARY_NATIVE_COMPLETION_PROOF.json')}))
