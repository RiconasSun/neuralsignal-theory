"""Public-key onboarding and readonly verification. No REAL signer or bootstrap API."""
from pathlib import Path
if __package__:
    from .common import *
else:
    from common import *

def fingerprint(public_hex):
    try:raw=bytes.fromhex(public_hex)
    except ValueError:raise PermissionError('ED25519_PUBLIC_ENCODING')
    if len(raw)!=32:raise PermissionError('ED25519_PUBLIC_LENGTH')
    return digest(raw)

def inspect_public_key(public_hex,owner_fingerprint,independent_fingerprint):
    found=fingerprint(public_hex)
    if found!=owner_fingerprint or found!=independent_fingerprint:raise PermissionError('INDEPENDENT_FINGERPRINT_MISMATCH')
    return {'fingerprint_sha256':found,'fingerprint_match':True,'REAL_D_AUTHORITY_PROVISIONED':False,'status':'CANDIDATE_VERIFIED_NOT_ACTIVATED'}

def require_real_authority(provisioning_root,registered_receipt_sha256,owner_designation_sha256):
    # The root and receipt hash come from a separately reviewed deployment, never a request.
    if not registered_receipt_sha256:raise PermissionError('AUTHORITY_PENDING')
    if owner_designation_sha256!='3bf5ec38e3aa7938183452421f93134fa6763f4262400af8c551581ff32603ba':raise PermissionError('REGISTERED_OWNER_DESIGNATION')
    root=Path(provisioning_root)
    receipt_path=safe(root,root/'provisioning_receipt.json')
    if sha(receipt_path)!=registered_receipt_sha256:raise PermissionError('PROVISIONING_RECEIPT_HASH')
    p=read_json(receipt_path)
    if set(p)!={'version','realm','owner_designation_sha256','approver_identity','public_key_hex','fingerprint_sha256','owner_confirmation_sha256','independent_check_sha256','provisioning_id'} or p['version']!=1 or p['realm']!='REAL_D' or p['owner_designation_sha256']!=owner_designation_sha256 or not p['approver_identity'] or not p['provisioning_id']:raise PermissionError('REAL_AUTHORITY_PROVISIONING_SCHEMA')
    owner=read_json(safe(root,root/'owner_confirmation.json'));independent=read_json(safe(root,root/'independent_check.json'))
    if sha(root/'owner_confirmation.json')!=p['owner_confirmation_sha256'] or sha(root/'independent_check.json')!=p['independent_check_sha256']:raise PermissionError('AUTHORITY_CONFIRMATION_HASH')
    if owner.get('owner_designation_sha256')!=owner_designation_sha256 or owner.get('provisioning_id')!=p['provisioning_id'] or independent.get('provisioning_id')!=p['provisioning_id'] or not independent.get('verifier_identity') or not independent.get('out_of_band_method'):raise PermissionError('AUTHORITY_INDEPENDENT_PROVISIONING_REQUIRED')
    found=inspect_public_key(p['public_key_hex'],owner['fingerprint_sha256'],independent['fingerprint_sha256'])
    if found['fingerprint_sha256']!=p['fingerprint_sha256']:raise PermissionError('PINNED_FINGERPRINT_DRIFT')
    # Trusted local provisioning is protected against scientific/evaluation principals.
    if __package__:
        from .native_host import assert_private
    else:from native_host import assert_private
    for path in (root,receipt_path,root/'owner_confirmation.json',root/'independent_check.json'):assert_private(path)
    return p['public_key_hex']

def trusted_public(deployment):
    realm=deployment['realm']
    if realm=='REAL_D':
        return require_real_authority(deployment['authority_root'],deployment.get('authority_receipt_sha256'),deployment['owner_designation_sha256'])
    if realm!='SYNTHETIC_D' or deployment.get('synthetic') is not True:raise PermissionError('AUTHORITY_DOMAIN')
    root=Path(deployment['job_root']).resolve();authority=Path(deployment['authority_root']).resolve()
    if not root.name.startswith('synthetic_') or not authority.is_relative_to(root/'.private'):raise PermissionError('SYNTHETIC_AUTHORITY_ROOT')
    registered=read_json(authority/'synthetic_authority.json')
    if registered['realm']!='SYNTHETIC_D' or registered['mission']!=MISSION or registered['base']!=BASE or sha(authority/'synthetic_authority.json')!=deployment['authority_receipt_sha256']:raise PermissionError('SYNTHETIC_AUTHORITY_BINDING')
    fingerprint(registered['public_key_hex']);return registered['public_key_hex']
