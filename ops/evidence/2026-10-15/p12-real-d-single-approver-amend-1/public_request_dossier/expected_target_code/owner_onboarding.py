"""Public-only owner ceremony. Never opens private material or signs any message."""
import argparse
import sys
import uuid
from pathlib import Path
from .common import *
from .owner_protocol import *

PUBLIC_FILES=('owner_challenge.json','owner_proof.json','owner_setup.json','owner_confirmation.json','provisioning_receipt.json')

def prepare(public_key_file,environment_reference,output):
    public=Path(public_key_file).read_text(encoding='ascii').strip()
    public_identity(public)
    output=Path(output);output.mkdir(parents=True,exist_ok=False)
    setup=setup_record('P12_PROJECT_OWNER',uuid.uuid4().hex,environment_reference,'REAL_D')
    challenge=make_challenge(public,setup,uuid.uuid4().hex)
    new(output/'owner_setup.json',setup);new(output/'owner_challenge.json',challenge)
    with (output/'key-possession-message.bin').open('xb') as f:f.write(canonical(challenge))
    return challenge

def confirm(directory,signature_file,local_confirmation):
    root=Path(directory);setup=read_json(root/'owner_setup.json');challenge=read_json(root/'owner_challenge.json');signature=Path(signature_file).read_text(encoding='ascii').strip();proof={'challenge_body':challenge,'signature':signature}
    check_proof(challenge,proof,setup,'REAL_D')
    value=confirmation_record(challenge,proof,setup,local_confirmation)
    # Append-only: repeated confirmation is refused; no release or entitlement exists.
    new(root/'owner_proof.json',proof);new(root/'owner_confirmation.json',value)
    new(root/'provisioning_receipt.json',receipt_value(root,'REAL_D'))
    return {'candidate_receipt_sha256':sha(root/'provisioning_receipt.json'),'fingerprint_sha256':challenge['fingerprint_sha256'],'status':'PUBLIC_OWNER_CANDIDATE_VERIFIED_PENDING_PROTECTED_IMPORT','OWNER_AUTHORITY_READY':False,'REAL_D_SIGNATURE_ISSUED':False,'D_RELEASE_CONSUMED':False,'D_EVALUATION_EXECUTED':False}

def install_public_bundle(candidate_root,registered_candidate_receipt_sha256,target_root):
    # Trusted Host continuation only, after genuine owner evidence is supplied.
    from .native_host import assert_private,protect
    require(bool(registered_candidate_receipt_sha256),'AUTHORITY_PENDING')
    candidate_root=Path(candidate_root);target_root=Path(target_root)
    value=validate_receipt(candidate_root,registered_candidate_receipt_sha256,'REAL_D')
    assert_private(target_root.parent)
    target_root.mkdir(exist_ok=False);protect(target_root)
    for name in PUBLIC_FILES:
        new(target_root/name,read_json(candidate_root/name));protect(target_root/name)
    require(sha(target_root/'provisioning_receipt.json')==registered_candidate_receipt_sha256,'PUBLIC_IMPORT_BYTE_IDENTITY')
    validate_receipt(target_root,registered_candidate_receipt_sha256,'REAL_D')
    return {'realm':'REAL_D','owner_identity':value['owner_identity'],'fingerprint_sha256':value['fingerprint_sha256'],'authority_receipt_sha256':registered_candidate_receipt_sha256,'trust_root_requires_reviewed_deployment_pin':True,'REAL_D_SIGNATURE_ISSUED':False,'D_RELEASE_CONSUMED':False,'D_EVALUATION_EXECUTED':False}

def main():
    parser=argparse.ArgumentParser(description='Public-key-only single-owner onboarding; no signer, private keys, second verifier or manual fingerprint.')
    sub=parser.add_subparsers(dest='command',required=True)
    p=sub.add_parser('prepare');p.add_argument('--public-key-file',required=True);p.add_argument('--environment-reference',required=True);p.add_argument('--output',required=True)
    p=sub.add_parser('confirm');p.add_argument('--ceremony-directory',required=True);p.add_argument('--signature-file',required=True)
    args=parser.parse_args()
    if args.command=='prepare':
        value=prepare(args.public_key_file,args.environment_reference,args.output)
        print('Automatic public fingerprint: '+value['fingerprint_sha256'])
        print('Use your separately controlled offline signer to sign ONLY key-possession-message.bin. Return only the detached signature as128 lowercase hexadecimal characters in a PUBLIC signature file. Software binds the exact challenge automatically. Do not provide a private key. This is not REAL_D approval.')
    else:
        require(sys.stdin.isatty(),'OWNER_LOCAL_INTERACTIVE_CONFIRMATION_REQUIRED')
        root=Path(args.ceremony_directory);challenge=read_json(root/'owner_challenge.json')
        print('Confirm that you are the designated P12 owner and the key remains on your separate offline device, inaccessible to Codex/workers. No REAL_D approval, release or evaluation is granted.')
        require(input('Type CONFIRM OWNER '+challenge['ceremony_id']+': ').strip()=='CONFIRM OWNER '+challenge['ceremony_id'],'OWNER_CONFIRMATION_DECLINED')
        print(json.dumps(confirm(root,args.signature_file,CONFIRM),sort_keys=True))

if __name__=='__main__':main()
