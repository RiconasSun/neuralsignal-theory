"""Trusted approval issuer for C only. Cannot create or consume a D entitlement."""
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding,PublicFormat,PrivateFormat,NoEncryption
import study as r
from native import security
from release_control import canonical

def main():
    r.verify();a=security();snapshot_file='implementation_snapshot_v2.json';snapshot=r.load(r.HERE/snapshot_file)
    for name,h in snapshot['sha256'].items():
        if r.sha(r.ROOT/name)!=h:raise PermissionError('FROZEN_ENGINEERING_CODE_CHANGED')
    selection=r.load(r.HERE/'E3_evidence_selection.json')
    for name in selection.values():
        if not isinstance(name,str) or not name.startswith('results/') or '..' in name:raise PermissionError('E3_EVIDENCE_SCOPE')
    certificate=r.load(r.HERE/selection['state_result']);security_result=r.load(r.HERE/selection['security_result'])
    cert=certificate['certificate_receipt']
    if certificate['certificate_gate']['gate']!='PASS' or cert['exit_code']!=0 or not cert['role_proof_pass'] or cert['profile_cleanup_hresult']!='0x00000000':raise PermissionError('SYNTHETIC_STATE_CERTIFICATE_REQUIRED')
    if security_result['gate']!='PASS' or security_result['D_RELEASE_CONSUMED'] or security_result['D_EVALUATION_EXECUTED'] or security_result['injected_failures_counted_valid_releases']!=0:raise PermissionError('ENGINEERING_SECURITY_GATE_REQUIRED')
    evidence={name:r.sha(r.HERE/name) for name in selection.values()};evidence['E3_evidence_selection.json']=r.sha(r.HERE/'E3_evidence_selection.json')
    for role in ('controller','target'):
        receipt=security_result[role+'_receipt']
        if receipt['exit_code']!=0 or not receipt['role_proof_pass'] or receipt['profile_cleanup_hresult']!='0x00000000':raise PermissionError('FRESH_ACTUAL_ROLE_REQUIRED')
    reviews={}
    for role in ('engineering','scientific'):
        p=r.ROOT/f'ops/evidence/2026-10-14/p12-final-prerelease-controls-1/{role}_review.md'
        text=p.read_text(encoding='utf-8')
        if 'E0_E3_PASS_ALLOW_CONDITIONAL_C' not in text or r.sha(r.HERE/snapshot_file) not in text or evidence[selection['security_result']] not in text:raise PermissionError('EXACT_INDEPENDENT_FINAL_REVIEW_REQUIRED')
        reviews[p.relative_to(r.ROOT).as_posix()]=r.sha(p)
    body={'scope':'C_ONLY_CALIBRATION','mission':r.MISSION,'base':r.BASE,'snapshot_file':snapshot_file,'snapshot_sha256':r.sha(r.HERE/snapshot_file),'evidence_sha256':evidence,'review_sha256':reviews}
    directory=r.HERE/'.private/C_authorization';a.prepare(directory)
    key=Ed25519PrivateKey.generate()
    p=directory/'issuer.key'
    with p.open('xb') as f:f.write(key.private_bytes(Encoding.Raw,PrivateFormat.Raw,NoEncryption()))
    a.protect(p)
    r.save(directory/'authority.json',{'public':key.public_key().public_bytes(Encoding.Raw,PublicFormat.Raw).hex(),'scope':'C_ONLY_CALIBRATION'})
    r.save(directory/'approval.json',{'body':body,'signature':key.sign(canonical(body)).hex()})
    for p in directory.iterdir():a.protect(p)
    r.save(r.HERE/'results/C_authorization_receipt.json',{'scope':'C_ONLY_CALIBRATION','approval_body':body,'private_key_granted_to_analysis':False,'real_D_authorization_created':False,'D_RELEASE_CONSUMED':False,'D_EVALUATION_EXECUTED':False})
    print({'C_only_authorization':'ISSUED_AFTER_INDEPENDENT_E0_E3_APPROVAL','D_authorization':False})
if __name__=='__main__':main()
