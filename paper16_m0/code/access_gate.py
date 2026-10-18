"""Ordinary fail-closed independent-review gate; no cryptographic custody claim."""
from pathlib import Path
from .core import read_json,sha256
E='ops/evidence/2026-10-18/p16-visual-cortex-data-first-m0'
REQUIRED={
 'paper16_m0/code/'+n for n in ['http_metadata.py','acquire_metadata.py','core.py','access_gate.py','pilot_reader.py','pilot_transfer.py','test_core.py','test_reader.py','test_integration.py','metadata_audit.py']
}|{'paper16_m0/'+n for n in ['FEASIBILITY_REGISTRATION.json','results/ROLE_ALLOCATION.json','results/PILOT_METADATA_SELECTION.json','results/PILOT_OBJECT_FREEZE.json','metadata/METADATA_ACTIVE_BINDING.json','metadata/sessions.body','metadata/probes.body','metadata/channels.body','metadata/source_unit_qc.body','metadata/sessions_sdk_definition.body']}

def verify_access_approval(root):
    root=Path(root); receipt=read_json(root/E/'PILOT_ACCESS_REVIEW_RECEIPT.json')
    if receipt.get('decision')!='ACCEPTED_BOUNDED_PILOT_ACCESS': raise ValueError('Review decision denies access')
    if receipt.get('approved_spike_GET_or_decode') is not True: raise ValueError('Explicit access approval absent')
    for k in ['open_P0','open_P1']:
        if type(receipt.get(k)) is not int or receipt[k]!=0: raise ValueError('Review defects or invalid types')
    hashes=receipt.get('reviewed_hashes')
    if not isinstance(hashes,dict) or not REQUIRED<=hashes.keys(): raise ValueError('Incomplete required review identities')
    for name,digest in hashes.items():
        path=(root/name).resolve()
        if not path.is_relative_to(root.resolve()) or sha256(path)!=digest: raise ValueError('Reviewed identity mismatch '+name)
    report=root/E/'PILOT_ACCESS_REVIEW.md'
    if receipt.get('report_sha256')!=sha256(report): raise ValueError('Independent report identity mismatch')
    return receipt
