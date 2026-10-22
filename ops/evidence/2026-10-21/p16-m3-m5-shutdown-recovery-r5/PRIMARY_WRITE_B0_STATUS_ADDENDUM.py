"""Append metadata clarification only; no neural/fit arrays or certificate arithmetic."""
import datetime
import hashlib
import json
import os
from pathlib import Path

R=Path(__file__).resolve().parents[4]
E=Path(__file__).resolve().parent
P=R/'paper16_development_r5'


def load(path):
    return json.loads(path.read_bytes())


def sha(path):
    with path.open('rb') as f:
        return hashlib.file_digest(f,'sha256').hexdigest()


result=load(P/'PRIMARY_AUDIT_V2_RESULT.json')
proof=load(E/'PRIMARY_NATIVE_COMPLETION_PROOF.json')
assert result['B0_attempted']==result['B0_passed']==216
assert proof['result_sha256']==sha(P/'PRIMARY_AUDIT_V2_RESULT.json')
assert proof['result']['B0_matrix_sha256']==result['B0_matrix_sha256']
value={
    'mission':result['mission'],
    'recorded_UTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'scope':'APPEND_ONLY_METADATA_FIELD_SEMANTICS_NO_AUDIT_RERUN',
    'original_matrix':{
        'path':'paper16_development_r5/PRIMARY_B0_V2_MATRIX.json',
        'sha256':result['B0_matrix_sha256'],
        'not_overwritten':True
    },
    'primary_result':{
        'path':'paper16_development_r5/PRIMARY_AUDIT_V2_RESULT.json',
        'sha256':proof['result_sha256']
    },
    'native_completion_proof':{
        'path':'ops/evidence/2026-10-21/p16-m3-m5-shutdown-recovery-r5/PRIMARY_NATIVE_COMPLETION_PROOF.json',
        'sha256':sha(E/'PRIMARY_NATIVE_COMPLETION_PROOF.json'),
        'actual_exit_code':proof['actual_native_invocation']['observed_actual_exit_code']
    },
    'inherited_target_snapshot':{
        'source':'paper16_shutdown_recovery_r5_protocol/REUSE_TARGETS.json',
        'R5_audit':'NOT_EXECUTED',
        'R5_admitted':False,
        'meaning':'These original target fields were copied into each matrix row as the prospective registration snapshot. R5_audit is not the current primary execution status.'
    },
    'actual_primary_execution':{
        'authoritative_matrix_field':'status',
        'status':'PASS',
        'B0_attempted':216,
        'B0_passed':216,
        'all_216_effective_primary_audit_status':'EXECUTED_PASS',
        'qualification':'This clarifies the already-completed original primary pass; it creates no new numerical result.'
    },
    'independent_qualification':{
        'complete':True,
        'basis':'Parent reports completed independent full-matrix comparison and requested this metadata-only clarification.',
        'R5_admission':'SEPARATE_FINAL_GATE',
        'no_final_admission_issued_by_this_addendum':True
    },
    'preservation':{
        'original_matrix_result_native_proof_unchanged':True,
        'audit_rerun':False,
        'numerical_state_reads':0,
        'numerical_recalculations':0,
        'scientific_threshold_changes':False
    }
}
path=E/'PRIMARY_B0_STATUS_FIELD_ADDENDUM.json'
with path.open('x',encoding='utf8',newline='\n') as f:
    json.dump(value,f,indent=2,allow_nan=False)
    f.write('\n');f.flush();os.fsync(f.fileno())
print(json.dumps({'path':path.relative_to(R).as_posix(),'sha256':sha(path),'numerical_reads':0,'audit_reruns':0}))
