"""Repository-module entry; individual auditors enforce actual saved-only gates."""
import hashlib
import json
from pathlib import Path
import sys

R=Path(__file__).resolve().parents[1]
E=R/'ops/evidence/2026-10-21/p16-m3-m5-reliability-gated-recovery-r6'

def exact_source(row,raw):
    if type(row.get('bytes')) is not int or row['bytes']!=len(raw) or row.get('sha256')!=hashlib.sha256(raw).hexdigest():
        raise RuntimeError('Exact frozen source bytes required before executing audit code')
    return raw

def main(role):
    names={'primary':'PRIMARY_REUSE_AUDIT_R6.py',
           'independent':'INDEPENDENT_REUSE_AUDIT_R6.py'}
    if role not in names:raise ValueError('One exact registered audit role required')
    if Path.cwd()!=R:raise RuntimeError('Audit must start at the registered repository root')
    freeze_bytes=(E/'REUSE_AUDIT_PREEXECUTION_FREEZE.json').read_bytes()
    freeze=json.loads(freeze_bytes)
    claim=(R/'paper16_development_r6/PHASE_A_CLAIM.json').read_bytes()
    approval=json.loads((E/'INDEPENDENT_REUSE_PREEXECUTION_REVIEW_BINDING.json').read_bytes())
    if (freeze['mission']!='P16-M3-M5-RELIABILITY-GATED-RECOVERY-R6'
        or freeze['base']!='e1aab9622a7e63b99335a529d8ad0107f611dc8c'
        or freeze['phase_claim_sha256']!=hashlib.sha256(claim).hexdigest()
        or approval['decision']!='ACCEPTED_SAVED_REUSE_AUDIT_EXECUTION_ONLY'
        or any(type(approval[k]) is not int or approval[k]!=0 for k in ['open_P0','open_P1'])
        or approval['freeze_sha256']!=hashlib.sha256(freeze_bytes).hexdigest()
        or approval['actual_host_gate_accepted'] is not True
        or approval['real_A_optimization_authorized'] is not False):
        raise RuntimeError('Actual independent saved-only approval of this exact freeze required')
    row=[v for v in freeze['bound_files'] if v['path']==Path(__file__).relative_to(R).as_posix()]
    if len(row)!=1:
        raise RuntimeError('Exact audit entry source must be prospectively frozen')
    exact_source(row[0],Path(__file__).read_bytes())
    target=E/names[role]
    selected=[v for v in freeze['bound_files'] if v['path']==target.relative_to(R).as_posix()]
    if len(selected)!=1:raise RuntimeError('Selected audit source must have one frozen identity')
    verified=exact_source(selected[0],target.read_bytes())
    # Execute these verified bytes; do not reopen a potentially changed source.
    exec(compile(verified,str(target),'exec'),{'__name__':'__main__','__file__':str(target),'__package__':None})

if __name__=='__main__':
    if len(sys.argv)!=2:raise SystemExit('Usage: python -B -m paper16_development_r6.audit_entry primary|independent')
    main(sys.argv[1])
