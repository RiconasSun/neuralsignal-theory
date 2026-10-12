"""Preserve exact new diagnostic privately; publish no private block offsets."""
import hashlib
import common as r
import custodian as c


def main():
    r.verify();c.require_custodian()
    path=r.HERE/'results/M2/failures/779839471.json';original=path.read_bytes();receipt=r.load(path)
    if receipt['error_type']!='PermissionError' or '[WinError 5]' not in receipt['error_code']:
        raise RuntimeError('UNEXPECTED_DIAGNOSTIC_REDACTION_SCOPE')
    private=r.OLD/'.private/transport_recovery1/diagnostics'
    private.mkdir(exist_ok=True);c.protect(private)
    target=private/'779839471.original.json'
    with target.open('xb') as stream:stream.write(original)
    c.protect(target)
    digest=hashlib.sha256(original).hexdigest()
    if r.sha(target)!=digest:raise RuntimeError('DIAGNOSTIC_PRESERVATION_FAILED')
    receipt.update(error_code='TRANSPORT_CHECKPOINT_COMMIT_PERMISSION_DENIED',winerror=5,
        original_diagnostic_sha256=digest,diagnostic_detail_access='PRIVATE_CUSTODY_ONLY',
        redaction_reason='Independent review: do not export private source-block offsets')
    r.save(path,receipt)
    r.save(r.HERE/'results/diagnostic_redaction.json',dict(original_sha256=digest,
        sanitized_public_sha256=r.sha(path),original_exact_diagnostic_preserved_privately=True,
        original_prior_mission_failure_changed=False,source_requests_added=0))
    print('EXACT_NEW_DIAGNOSTIC_PRESERVED_PRIVATELY;PUBLIC_OFFSET_REDACTED;NO_SOURCE_REQUEST')


if __name__=='__main__':main()
