"""Metadata-only gate binding after saved-artifact re-audit; counts never changed."""
import study as r
import verified_atomic as a
from preflight import guard
from manifest_validation import validate_manifest


def main():
    guard()
    gate_path=r.HERE/'results/M2/gate_result.json';gate=r.load(gate_path)
    if gate['gate']!='PASS' or gate.get('completion_issuer_verified_count')!=26:raise RuntimeError('FULL_REAUDIT_PASS_REQUIRED')
    source=r.load(r.HERE/'results/M2/source_checkpoint_integrity.json')
    if source.get('expected_completed_new_sessions')!=18 or source.get('verified_completed_new_sessions')!=18:
        raise RuntimeError('FULL_SOURCE_DENOMINATOR_REQUIRED')
    root=r.HERE/'exports/development1';path=root/'manifest.json';manifest=r.load(path)
    issuer=r.HERE/'.private/development_export_issuer.json';prior=r.load(issuer)
    expected=dict(manifest_sha256=r.sha(path),M2_gate_sha256=manifest['M2_gate_sha256'],
        development_registration_sha256=manifest['development_registration_sha256'],method_decision_sha256=manifest['method_decision_sha256'])
    if prior!=expected:raise RuntimeError('PRIOR_EXPORT_ISSUER_CHANGED')
    for session in manifest['sessions']:
        if r.sha(root/session['file'])!=session['sha256']:raise RuntimeError('PRIOR_EXPORT_COUNTS_CHANGED')
    history=a.prepare(r.HERE/'.private/export_history_code2')
    a.durable_record(history/'manifest.json',manifest);a.durable_record(history/'issuer.json',prior)
    old=dict(manifest);manifest['M2_gate_sha256']=r.sha(gate_path)
    if {k:v for k,v in manifest.items() if k!='M2_gate_sha256'}!={k:v for k,v in old.items() if k!='M2_gate_sha256'}:
        raise RuntimeError('EXPORT_METADATA_SCOPE_CHANGED')
    animals=r.load(r.ROOT/'paper12_curated_v1/locks/animals.json')
    receipts={x['session_id']:r.load(r.HERE/'results/M2/sessions'/(x['session_id']+'.json')) for x in animals if x['group']=='development'}
    validate_manifest(manifest,animals,receipts,r.sha(gate_path),r.sha(r.OLD/'development_registration.json'))
    r.save(path,manifest);a.protect(path)
    r.save(issuer,dict(manifest_sha256=r.sha(path),M2_gate_sha256=manifest['M2_gate_sha256'],
        development_registration_sha256=manifest['development_registration_sha256'],method_decision_sha256=manifest['method_decision_sha256']));a.protect(issuer)
    r.save(r.HERE/'results/M3/export_metadata_binding_code2.json',dict(old_M2_gate_sha256=old['M2_gate_sha256'],
        new_M2_gate_sha256=manifest['M2_gate_sha256'],sessions=len(manifest['sessions']),
        all_export_count_hashes_unchanged=True,trial_and_unit_identities_unchanged=True,
        neural_contents_read=False,final_values_accessed=False,implementation_sha256=r.sha(r.HERE/'rebind_export_manifest.py')))
    print('EXPORT_GATE_METADATA_REBOUND; ALL_COUNTS_AND_IDENTITIES_UNCHANGED')


if __name__=='__main__':main()
