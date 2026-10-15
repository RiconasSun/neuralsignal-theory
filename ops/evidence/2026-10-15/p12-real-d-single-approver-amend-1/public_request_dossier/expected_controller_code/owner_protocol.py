"""Single-owner public proof validation. Contains no private-key or release signer."""
import re
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
if __package__:
    from .common import *
    from .ed25519_public import validate_public_point,VALIDATION_POLICY
else:
    from common import *
    from ed25519_public import validate_public_point,VALIDATION_POLICY

POLICY='OWNER_CONTROLLED_SINGLE_APPROVER_V1'
KEY_AMENDMENT='cdffd327632ceac9dcb25c96ab26f0686ac742ff944c4c72c20b34d295ce46b6'
AMENDMENT='83d49d5aa2da9cbd0761421963322a898efe2ee0fccd1fd686c23bb4d529d2eb'
DESIGNATION='3bf5ec38e3aa7938183452421f93134fa6763f4262400af8c551581ff32603ba'
CONFIRM='I_CONFIRM_OWNER_CONTROL_AND_OFFLINE_SEPARATION'

def require(value,label):
    if not value:raise PermissionError(label)

def public_identity(value):
    require(isinstance(value,str) and re.fullmatch('[0-9a-fA-F]{64}',value) is not None,'ED25519_PUBLIC_FORMAT')
    raw=validate_public_point(bytes.fromhex(value))
    Ed25519PublicKey.from_public_bytes(raw)
    return {'public_key_hex':raw.hex(),'fingerprint_sha256':digest(raw)}

def setup_record(owner,ceremony,environment,realm):
    require(realm in ('REAL_D','SYNTHETIC_D'),'ONBOARDING_REALM')
    require(isinstance(owner,str) and owner.strip()==owner and 0<len(owner)<=200,'OWNER_IDENTITY')
    require(owner==('P12_PROJECT_OWNER' if realm=='REAL_D' else 'SYNTHETIC_OWNER_ONLY'),'DESIGNATED_OWNER_ROLE')
    require(re.fullmatch('[0-9a-f]{32}',ceremony or '') is not None,'CEREMONY_ID')
    require(isinstance(environment,str) and 0<len(environment.strip())<=500,'OWNER_ENVIRONMENT_REFERENCE')
    return {'version':1,'policy':POLICY,'realm':realm,'owner_identity':owner,'ceremony_id':ceremony,'environment_reference':environment,'mode':'SEPARATE_OFFLINE_OWNER_DEVICE' if realm=='REAL_D' else 'SYNTHETIC_ISOLATION_FIXTURE_ONLY','codex_or_worker_accessible':False,'owner_controls_signing_material':True,'private_material_exported':False,'owner_confirmed_physical_separation':realm=='REAL_D'}

def make_challenge(public,setup,nonce):
    identity=public_identity(public)
    require(re.fullmatch('[0-9a-f]{32}',nonce or '') is not None,'CHALLENGE_NONCE')
    validate_setup(setup,setup['realm'])
    return {'version':1,'purpose':'OWNER_KEY_ONBOARDING_ONLY','realm':setup['realm'],'mission':MISSION,'base':BASE,'policy':POLICY,'security_amendment_sha256':AMENDMENT,'public_key_validation_policy':VALIDATION_POLICY,'public_key_validation_amendment_sha256':KEY_AMENDMENT,'owner_designation_sha256':DESIGNATION,'owner_identity':setup['owner_identity'],'ceremony_id':setup['ceremony_id'],'challenge_nonce':nonce,'public_key_hex':identity['public_key_hex'],'fingerprint_sha256':identity['fingerprint_sha256'],'owner_setup_sha256':digest(canonical(setup)),'no_real_release_approval':True}

def validate_setup(value,realm):
    expected=setup_record(value.get('owner_identity'),value.get('ceremony_id'),value.get('environment_reference'),realm)
    require(value==expected,'OWNER_ISOLATION_SETUP_REQUIRED')
    return value

def check_proof(challenge,proof,setup,realm):
    validate_setup(setup,realm)
    expected=make_challenge(challenge.get('public_key_hex'),setup,challenge.get('challenge_nonce'))
    require(challenge==expected and challenge['realm']==realm,'OWNER_CHALLENGE_IDENTITY_AMENDMENT')
    require(set(proof)=={'challenge_body','signature'} and proof['challenge_body']==challenge,'OWNER_PROOF_EXACT_CHALLENGE')
    require(isinstance(proof['signature'],str) and re.fullmatch('[0-9a-f]{128}',proof['signature']) is not None,'OWNER_PROOF_SIGNATURE_ENCODING')
    try:Ed25519PublicKey.from_public_bytes(bytes.fromhex(challenge['public_key_hex'])).verify(bytes.fromhex(proof['signature']),canonical(challenge))
    except Exception as exc:raise PermissionError('OWNER_KEY_POSSESSION_SIGNATURE') from exc
    return public_identity(challenge['public_key_hex'])

def confirmation_record(challenge,proof,setup,local_confirmation):
    check_proof(challenge,proof,setup,challenge['realm'])
    require(local_confirmation==CONFIRM,'EXPLICIT_OWNER_LOCAL_CONFIRMATION_REQUIRED')
    return {'version':1,'policy':POLICY,'realm':challenge['realm'],'owner_identity':challenge['owner_identity'],'ceremony_id':challenge['ceremony_id'],'public_key_hex':challenge['public_key_hex'],'fingerprint_sha256':challenge['fingerprint_sha256'],'challenge_sha256':digest(canonical(challenge)),'proof_sha256':digest(canonical(proof)),'owner_setup_sha256':digest(canonical(setup)),'local_confirmation':CONFIRM,'second_human_required':False,'manual_fingerprint_required':False,'physical_isolation_proof_scope':'Owner-confirmed physical offline separation; signature verifies possession and statement, not remote physical attestation'}

def validate_candidate(root,realm):
    root=Path(root)
    names=('owner_challenge.json','owner_proof.json','owner_setup.json','owner_confirmation.json')
    values={name:read_json(safe(root,root/name)) for name in names}
    challenge,proof,setup,confirmation=(values[name] for name in names)
    check_proof(challenge,proof,setup,realm)
    require(confirmation==confirmation_record(challenge,proof,setup,CONFIRM),'OWNER_CONFIRMATION_IDENTITY')
    return challenge,{name:sha(root/name) for name in names}

def validate_receipt(root,pinned_sha256,realm):
    require(bool(pinned_sha256),'AUTHORITY_PENDING')
    root=Path(root);receipt=safe(root,root/'provisioning_receipt.json')
    require(sha(receipt)==pinned_sha256,'PROVISIONING_RECEIPT_HASH')
    p=read_json(receipt);challenge,artifacts=validate_candidate(root,realm)
    expected={'version':2,'policy':POLICY,'realm':realm,'mission':MISSION,'base':BASE,'security_amendment_sha256':AMENDMENT,'public_key_validation_policy':VALIDATION_POLICY,'public_key_validation_amendment_sha256':KEY_AMENDMENT,'owner_designation_sha256':DESIGNATION,'owner_identity':challenge['owner_identity'],'ceremony_id':challenge['ceremony_id'],'public_key_hex':challenge['public_key_hex'],'fingerprint_sha256':challenge['fingerprint_sha256'],'artifacts':artifacts,'second_human_required':False,'manual_fingerprint_required':False}
    require(p==expected,'SINGLE_OWNER_TRUST_ROOT_SCHEMA_IDENTITY')
    return p

def receipt_value(root,realm):
    challenge,artifacts=validate_candidate(root,realm)
    return {'version':2,'policy':POLICY,'realm':realm,'mission':MISSION,'base':BASE,'security_amendment_sha256':AMENDMENT,'public_key_validation_policy':VALIDATION_POLICY,'public_key_validation_amendment_sha256':KEY_AMENDMENT,'owner_designation_sha256':DESIGNATION,'owner_identity':challenge['owner_identity'],'ceremony_id':challenge['ceremony_id'],'public_key_hex':challenge['public_key_hex'],'fingerprint_sha256':challenge['fingerprint_sha256'],'artifacts':artifacts,'second_human_required':False,'manual_fingerprint_required':False}
