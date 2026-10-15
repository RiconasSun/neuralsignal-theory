"""Ephemeral synthetic key fixtures only; no genuine owner key or provisioning."""
import copy
import inspect
from pathlib import Path
import tempfile
import unittest
import uuid
from unittest.mock import patch
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding,PublicFormat
from .common import *
from .owner_protocol import *
from .authority import require_real_authority
from .owner_onboarding import prepare,confirm

class OwnerTests(unittest.TestCase):
    def fixture(self,root,realm='SYNTHETIC_D'):
        key=Ed25519PrivateKey.generate();public=key.public_key().public_bytes(Encoding.Raw,PublicFormat.Raw).hex()
        setup=setup_record('P12_PROJECT_OWNER' if realm=='REAL_D' else 'SYNTHETIC_OWNER_ONLY',uuid.uuid4().hex,'SYNTHETIC TEST FIXTURE; NOT GENUINE OWNER SETUP',realm)
        challenge=make_challenge(public,setup,uuid.uuid4().hex);proof={'challenge_body':challenge,'signature':key.sign(canonical(challenge)).hex()};confirmation=confirmation_record(challenge,proof,setup,CONFIRM)
        for name,value in {'owner_setup.json':setup,'owner_challenge.json':challenge,'owner_proof.json':proof,'owner_confirmation.json':confirmation}.items():new(root/name,value)
        new(root/'provisioning_receipt.json',receipt_value(root,realm))
        return key,challenge,proof,setup

    def test_automatic_decoded_byte_fingerprint_and_format(self):
        value=public_identity('AB'*32);self.assertEqual(value['fingerprint_sha256'],digest(bytes.fromhex('ab'*32)));self.assertEqual(value['public_key_hex'],'ab'*32)
        self.assertNotEqual(value['fingerprint_sha256'],digest(('ab'*32).encode()))
        for bad in ('ab'*31,'ab'*33,'zz'*32,'ab '*32,' ab'+'ab'*31,''):
            with self.assertRaises(PermissionError):public_identity(bad)

    def test_synthetic_single_owner_receipt_and_no_second_human(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);self.fixture(root);p=validate_receipt(root,sha(root/'provisioning_receipt.json'),'SYNTHETIC_D')
            self.assertFalse(p['second_human_required']);self.assertFalse(p['manual_fingerprint_required']);self.assertFalse((root/'independent_check.json').exists())

    def test_exact_provisioning_pin_and_receipt_schema(self):
        for mutation in ('pin','fingerprint','key','owner','ceremony','amendment','version','extra','second_human'):
            with tempfile.TemporaryDirectory() as folder:
                root=Path(folder);self.fixture(root);p=read_json(root/'provisioning_receipt.json')
                if mutation=='pin':pin='0'*64
                else:
                    key={'fingerprint':'fingerprint_sha256','key':'public_key_hex','owner':'owner_identity','ceremony':'ceremony_id','amendment':'security_amendment_sha256','version':'version','extra':'unexpected','second_human':'second_human_required'}[mutation]
                    p[key]=True if mutation=='second_human' else 'ALTERED';(root/'provisioning_receipt.json').write_bytes(canonical(p)+b'\n');pin=sha(root/'provisioning_receipt.json')
                with self.assertRaises(PermissionError):validate_receipt(root,pin,'SYNTHETIC_D')

    def test_owner_proof_signature_wrong_key_and_realm_denial(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);key,c,p,s=self.fixture(root)
            wrong=Ed25519PrivateKey.generate();p['signature']=wrong.sign(canonical(c)).hex()
            with self.assertRaisesRegex(PermissionError,'OWNER_KEY_POSSESSION'):check_proof(c,p,s,'SYNTHETIC_D')
            with self.assertRaises(PermissionError):check_proof(c,read_json(root/'owner_proof.json'),s,'REAL_D')

    def test_challenge_owner_amendment_nonce_and_domain_tamper(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);key,c,p,s=self.fixture(root)
            for field in ('owner_identity','security_amendment_sha256','owner_designation_sha256','mission','base','purpose','challenge_nonce','no_real_release_approval'):
                bad=copy.deepcopy(c);bad[field]='ALTERED';proof={'challenge_body':bad,'signature':key.sign(canonical(bad)).hex()}
                with self.assertRaises(PermissionError):check_proof(bad,proof,s,'SYNTHETIC_D')

    def test_false_missing_or_changed_isolation_denied(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);key,c,p,s=self.fixture(root)
            for field,value in (('codex_or_worker_accessible',True),('owner_controls_signing_material',False),('private_material_exported',True),('mode','SHARED_DESKTOP'),('environment_reference','')):
                bad=dict(s,**{field:value})
                with self.assertRaises(PermissionError):check_proof(c,p,bad,'SYNTHETIC_D')
            with self.assertRaises(PermissionError):setup_record('ASSISTANT',uuid.uuid4().hex,'x','REAL_D')

    def test_local_confirmation_required_and_identity_bound(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);key,c,p,s=self.fixture(root)
            with self.assertRaises(PermissionError):confirmation_record(c,p,s,'yes')
            value=read_json(root/'owner_confirmation.json');value['owner_identity']='ASSISTANT';(root/'owner_confirmation.json').write_bytes(canonical(value)+b'\n')
            with self.assertRaises(PermissionError):validate_candidate(root,'SYNTHETIC_D')

    def test_onboarding_proof_cannot_be_release_approval(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);key,c,p,s=self.fixture(root)
            with self.assertRaisesRegex(PermissionError,'BINDING_SCHEMA'):verify_approval({'body':c,'signature':p['signature']},{},root)

    def test_missing_pending_authority_denies_before_path_access(self):
        with patch('paper12_singleowner1.authority.Path',side_effect=AssertionError('NO_AUTHORITY_PATH_OPEN')):
            with self.assertRaisesRegex(PermissionError,'AUTHORITY_PENDING'):require_real_authority('NEVER_OPEN',None,DESIGNATION)

    def test_replay_to_different_ceremony_or_setup_fails(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);key,c,p,s=self.fixture(root);other=dict(s,ceremony_id=uuid.uuid4().hex)
            with self.assertRaises(PermissionError):check_proof(c,p,other,'SYNTHETIC_D')

    def test_partial_missing_candidate_fails_closed(self):
        for name in ('owner_proof.json','owner_confirmation.json','owner_setup.json','owner_challenge.json'):
            with tempfile.TemporaryDirectory() as folder:
                root=Path(folder);self.fixture(root);(root/name).unlink()
                with self.assertRaises(FileNotFoundError):validate_candidate(root,'SYNTHETIC_D')

    def test_public_only_confirmation_workflow_and_append_only(self):
        # REAL-shaped public schema fixture; no actual owner/private environment claimed.
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);key=Ed25519PrivateKey.generate();pub=root/'PUBLIC.hex';pub.write_text(key.public_key().public_bytes(Encoding.Raw,PublicFormat.Raw).hex());ceremony=root/'public_candidate'
            c=prepare(pub,'SYNTHETIC TEST ONLY; not genuine owner setup',ceremony);proof=root/'proof.json';new(proof,{'challenge_body':c,'signature':key.sign(canonical(c)).hex()})
            answer=confirm(ceremony,proof,CONFIRM);self.assertFalse(answer['OWNER_AUTHORITY_READY']);self.assertFalse(answer['REAL_D_SIGNATURE_ISSUED']);self.assertEqual(answer['fingerprint_sha256'],c['fingerprint_sha256'])
            with self.assertRaises(FileExistsError):confirm(ceremony,proof,CONFIRM)

    def test_new_public_entrypoint_has_no_manual_fingerprint_or_second_verifier(self):
        from . import owner_onboarding as module
        source=inspect.getsource(module);self.assertNotIn('--owner-fingerprint',source);self.assertNotIn('--independent-fingerprint',source)
        self.assertNotIn('Ed25519PrivateKey',source);self.assertNotIn('.sign(',source)

if __name__=='__main__':unittest.main()
