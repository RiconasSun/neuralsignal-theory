"""Public-key onboarding and readonly verification. No REAL signer or bootstrap API."""
from pathlib import Path
if __package__:
    from .common import *
else:
    from common import *

def require_real_authority(provisioning_root,registered_receipt_sha256,owner_designation_sha256):
    if not registered_receipt_sha256:raise PermissionError('AUTHORITY_PENDING')
    if __package__:
        from .owner_protocol import DESIGNATION,validate_receipt
        from .native_host import assert_private
    else:
        from owner_protocol import DESIGNATION,validate_receipt
        from native_host import assert_private
    if owner_designation_sha256!=DESIGNATION:raise PermissionError('REGISTERED_OWNER_DESIGNATION')
    root=Path(provisioning_root)
    for path in (root,root/'provisioning_receipt.json',root/'owner_challenge.json',root/'owner_proof.json',root/'owner_setup.json',root/'owner_confirmation.json'):assert_private(path)
    return validate_receipt(root,registered_receipt_sha256,'REAL_D')['public_key_hex']


def trusted_public(deployment):
    realm=deployment['realm']
    if realm=='REAL_D':
        return require_real_authority(deployment['authority_root'],deployment.get('authority_receipt_sha256'),deployment['owner_designation_sha256'])
    if realm!='SYNTHETIC_D' or deployment.get('synthetic') is not True:raise PermissionError('AUTHORITY_DOMAIN')
    root=Path(deployment['job_root']).resolve();authority=Path(deployment['authority_root']).resolve()
    if not root.name.startswith('synthetic_') or not authority.is_relative_to(root/'.private'):raise PermissionError('SYNTHETIC_AUTHORITY_ROOT')
    registered=read_json(authority/'synthetic_authority.json')
    if registered['realm']!='SYNTHETIC_D' or registered['mission']!=MISSION or registered['base']!=BASE or sha(authority/'synthetic_authority.json')!=deployment['authority_receipt_sha256']:raise PermissionError('SYNTHETIC_AUTHORITY_BINDING')
    if __package__:from .owner_protocol import POLICY,AMENDMENT,validate_receipt
    else:from owner_protocol import POLICY,AMENDMENT,validate_receipt
    if set(registered)!={'realm','mission','base','public_key_hex','policy','security_amendment_sha256','owner_onboarding_receipt_sha256'} or registered['policy']!=POLICY or registered['security_amendment_sha256']!=AMENDMENT:raise PermissionError('SYNTHETIC_SINGLE_OWNER_POLICY')
    owner=validate_receipt(authority,registered['owner_onboarding_receipt_sha256'],'SYNTHETIC_D')
    if owner['public_key_hex']!=registered['public_key_hex']:raise PermissionError('SYNTHETIC_OWNER_TRUST_ROOT')
    return registered['public_key_hex']
