"""Trusted completion issuer audit; hashes only, no neural compartment decryption."""
import study as r
import verified_atomic as a


def check(receipt,reg):
    sid=receipt['session_id'];ns=receipt['custody_artifact_namespace']
    expected=dict(receipt);expected.pop('registration_sha256',None)
    if receipt['artifact_study']=='paper12_custody1':
        if sid not in reg['reuse']:raise RuntimeError('UNAUTHORIZED_OLD_RECEIPT_ROUTE')
        issuer=r.OLD/'.private/transport_recovery1/reuse_issuer.json'
        record=r.load(issuer)[sid]
        if ns!=record['namespace']:raise RuntimeError('ORIGINAL_NAMESPACE_CHANGED')
        root=r.OLD/'.private'/ns/sid
        hashes=record['fingerprints']
    elif receipt['artifact_study']=='paper12_resume1':
        if sid in reg['reuse'] or not ns.startswith('sessions/run_') or '/' in ns[len('sessions/run_'):]:
            raise RuntimeError('NEW_NAMESPACE_INVALID')
        root=a.check_path(r.HERE/'.private'/ns/sid)
        issuer=a.check_path(r.HERE/'.private/issuers'/(sid+'.json'))
        a.check_acl(issuer)
        record=r.load(issuer)
        if record['receipt']!=expected:raise RuntimeError('NEW_ISSUER_RECEIPT_CHANGED')
        hashes=record['artifact_sha256']
    else:raise RuntimeError('UNKNOWN_ARTIFACT_STUDY')
    required={'private_provenance.json'}|{part+ext for part in receipt['ciphertext_receipts'] for ext in ('.gcm','.key')}
    if set(hashes)!=required:raise RuntimeError('ISSUER_ARTIFACT_DENOMINATOR_INVALID')
    for name,digest in hashes.items():
        if r.sha(root/name)!=digest:raise RuntimeError('COMPLETION_ARTIFACT_CHANGED')
    return root


def main():
    from preflight import guard,verify_reuse
    reg=guard();verify_reuse();rows=[]
    for path in sorted((r.HERE/'results/M2/sessions').glob('*.json')):
        receipt=r.load(path);check(receipt,reg)
        rows.append(dict(session_id=receipt['session_id'],receipt_sha256=r.sha(path),issuer_and_all_artifacts_verified=True,decrypted=False))
    r.save(r.HERE/'results/M2/completion_integrity.json',dict(rows=rows,verified_sessions=len(rows),
        code_sha256=r.sha(r.HERE/'fingerprints.py'),final_neural_contents_read=False))
    print(dict(completion_artifacts_verified=len(rows),decrypted=False))


if __name__=='__main__':main()
