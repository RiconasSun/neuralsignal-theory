"""Independent affine public-point oracle; all keys/vectors are synthetic/public."""
import copy
import hashlib
import random
from pathlib import Path
import tempfile
import unittest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey,Ed25519PublicKey
from cryptography.hazmat.primitives.serialization import Encoding,PublicFormat
from .ed25519_public import validate_public_point
from .owner_protocol import setup_record,make_challenge,confirmation_record,check_proof,validate_receipt,receipt_value,CONFIRM
from .common import canonical,new,sha,digest,read_json

# Separate affine formulas, representation and scalar routine; no production helpers.
FIELD=2**255-19
ORDER=2**252+27742317777372353535851937790883648493
CURVE=(-121665*pow(121666,FIELD-2,FIELD))%FIELD
IDENTITY=(0,1)
VECTOR_EVIDENCE=[]

def affine_add(a,b):
    x,y=a;u,v=b;t=CURVE*x*u*y*v%FIELD
    if (1+t)%FIELD==0 or (1-t)%FIELD==0:raise ArithmeticError('AFFINE_ORACLE_DENOMINATOR')
    return ((x*v+u*y)*pow((1+t)%FIELD,FIELD-2,FIELD)%FIELD,(y*v+x*u)*pow((1-t)%FIELD,FIELD-2,FIELD)%FIELD)

def affine_multiply(point,scalar):
    # Left-to-right ladder differs from production right-to-left extended arithmetic.
    result=IDENTITY
    for bit in bin(scalar)[2:]:
        result=affine_add(result,result)
        if bit=='1':result=affine_add(result,point)
    return result

def affine_decode(raw):
    if len(raw)!=32:return None
    value=int.from_bytes(raw,'little');sign=value>>255;y=value&((1<<255)-1)
    if y>=FIELD:return None
    denominator=(1+CURVE*y*y)%FIELD
    if not denominator:return None
    square=(y*y-1)*pow(denominator,FIELD-2,FIELD)%FIELD
    x=pow(square,(FIELD+3)//8,FIELD)
    if x*x%FIELD!=square:x=x*pow(2,(FIELD-1)//4,FIELD)%FIELD
    if x*x%FIELD!=square or (x==0 and sign):return None
    if x%2!=sign:x=FIELD-x
    if (-x*x+y*y-1-CURVE*x*x*y*y)%FIELD:return None
    return x,y

def affine_encode(point):
    return (point[1]|((point[0]&1)<<255)).to_bytes(32,'little')

def oracle_admits(raw):
    point=affine_decode(raw)
    return point is not None and point!=IDENTITY and affine_multiply(point,ORDER)==IDENTITY

class PublicPointTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.keys=[Ed25519PrivateKey.generate() for _ in range(16)]
        cls.strong=[k.public_key().public_bytes(Encoding.Raw,PublicFormat.Raw) for k in cls.keys]
        cls.rfc=[bytes.fromhex(v) for v in ('d75a980182b10ab7d54bfed3c964073a0ee172f3daa62325af021a68f707511a','3d4017c3e843895a92b70aa74d1b7ebc9c982ccf2ec4968cc0cd55f12af4660c','fc51cd8e6218a1a38da47ed00230f0580816ed13ba3303ac5deb911548908025')]
        generator=None
        for y in range(2,65):
            point=affine_decode(y.to_bytes(32,'little'))
            if point is None:continue
            candidate=affine_multiply(point,ORDER)
            if affine_multiply(candidate,4)!=IDENTITY and affine_multiply(candidate,8)==IDENTITY:generator=candidate;break
        if generator is None:raise RuntimeError('BOUNDED_ORDER8_ORACLE_FIXTURE')
        cls.torsion=[affine_multiply(generator,k) for k in range(8)]
        cls.mixed=[affine_add(affine_decode(cls.rfc[0]),t) for t in cls.torsion[1:]]

    def test_complete_torsion_and_mixed_order_rejection(self):
        self.assertEqual(len(set(self.torsion)),8)
        for point in self.torsion:
            self.assertEqual(affine_multiply(point,8),IDENTITY)
            with self.assertRaises(PermissionError):validate_public_point(affine_encode(point))
        for point in self.mixed:
            self.assertNotEqual(affine_multiply(point,ORDER),IDENTITY)
            with self.assertRaisesRegex(PermissionError,'NOT_PRIME_SUBGROUP'):validate_public_point(affine_encode(point))

    def test_independent_affine_full_vector_matrix(self):
        rng=random.Random(20261015)
        groups={'RFC_PUBLIC':self.rfc,'GENERATED_STRONG':self.strong,'TORSION':[affine_encode(p) for p in self.torsion],'MIXED_ORDER':[affine_encode(p) for p in self.mixed],'Y_0_THROUGH_63':[(y|(sign<<255)).to_bytes(32,'little') for y in range(64) for sign in (0,1)],'NONCANONICAL_Y':[(FIELD+i|(sign<<255)).to_bytes(32,'little') for i in range(19) for sign in (0,1)],'FORBIDDEN_ZERO_X_SIGN':[(y|(1<<255)).to_bytes(32,'little') for y in (1,FIELD-1)],'SEEDED_BYTES':[rng.randbytes(32) for _ in range(32)]}
        VECTOR_EVIDENCE.clear()
        for group,values in groups.items():
            for index,raw in enumerate(values):
                expected=oracle_admits(raw)
                try:validate_public_point(raw);actual=True;reason='ADMITTED_PRIME_SUBGROUP'
                except PermissionError as exc:actual=False;reason=str(exc)
                self.assertEqual(actual,expected,(group,index,raw.hex()))
                VECTOR_EVIDENCE.append({'group':group,'index':index,'public_hex':raw.hex(),'affine_oracle_admits':expected,'guard_admits':actual,'guard_reason':reason})
        self.assertEqual(len(VECTOR_EVIDENCE),234)

    def test_explicit_canonical_sign_and_length_errors(self):
        for y in (1,FIELD-1):
            with self.assertRaisesRegex(PermissionError,'NONCANONICAL_X_SIGN'):validate_public_point((y|(1<<255)).to_bytes(32,'little'))
        for raw in (b'',bytes(31),bytes(33)):
            with self.assertRaisesRegex(PermissionError,'PUBLIC_LENGTH'):validate_public_point(raw)
        with self.assertRaisesRegex(PermissionError,'NONCANONICAL_Y'):validate_public_point(FIELD.to_bytes(32,'little'))

    def test_generated_strong_keys_keep_normal_signature_verification(self):
        message=b'SYNTHETIC_PUBLIC_GUARD_POSITIVE_ONLY'
        for key,public in zip(self.keys,self.strong):
            self.assertEqual(validate_public_point(public),public)
            Ed25519PublicKey.from_public_bytes(public).verify(key.sign(message),message)

    def test_forged_identity_owner_possession_proof_rejected(self):
        setup=setup_record('SYNTHETIC_OWNER_ONLY','1'*32,'SYNTHETIC_ONLY','SYNTHETIC_D');good=make_challenge(self.rfc[0].hex(),setup,'2'*32)
        forged_public=bytes([1])+bytes(31);challenge=dict(good,public_key_hex=forged_public.hex(),fingerprint_sha256=hashlib.sha256(forged_public).hexdigest())
        proof={'challenge_body':challenge,'signature':(bytes([1])+bytes(63)).hex()}
        with self.assertRaisesRegex(PermissionError,'IDENTITY_PUBLIC_KEY'):check_proof(challenge,proof,setup,'SYNTHETIC_D')

    def test_self_consistent_forged_candidate_never_admitted(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);setup=setup_record('SYNTHETIC_OWNER_ONLY','3'*32,'SYNTHETIC_ONLY','SYNTHETIC_D');challenge=make_challenge(self.strong[0].hex(),setup,'4'*32);proof={'challenge_body':challenge,'signature':self.keys[0].sign(canonical(challenge)).hex()};confirmation=confirmation_record(challenge,proof,setup,CONFIRM)
            for name,value in {'owner_setup.json':setup,'owner_challenge.json':challenge,'owner_proof.json':proof,'owner_confirmation.json':confirmation}.items():new(root/name,value)
            receipt=receipt_value(root,'SYNTHETIC_D')
            bad=bytes([1])+bytes(31);challenge.update(public_key_hex=bad.hex(),fingerprint_sha256=digest(bad));proof={'challenge_body':challenge,'signature':(bytes([1])+bytes(63)).hex()};confirmation.update(public_key_hex=bad.hex(),fingerprint_sha256=digest(bad),challenge_sha256=digest(canonical(challenge)),proof_sha256=digest(canonical(proof)))
            for name,value in {'owner_challenge.json':challenge,'owner_proof.json':proof,'owner_confirmation.json':confirmation}.items():(root/name).write_bytes(canonical(value)+b'\n')
            receipt.update(public_key_hex=bad.hex(),fingerprint_sha256=digest(bad),artifacts={n:sha(root/n) for n in receipt['artifacts']});new(root/'provisioning_receipt.json',receipt)
            with self.assertRaisesRegex(PermissionError,'IDENTITY_PUBLIC_KEY'):validate_receipt(root,sha(root/'provisioning_receipt.json'),'SYNTHETIC_D')

if __name__=='__main__':unittest.main()
