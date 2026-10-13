import unittest
import hashlib
from closure_verify import admission,prefix_ok,native_complete


class ClosureTests(unittest.TestCase):
    def test_completed_native_failure_not_early_gate(self):
        receipt=dict(exit_code=2,timed_out=False,role_proof_pass=True,profile_cleanup_hresult='0x00000000')
        proof=dict(pass_=True,is_appcontainer=True,capability_count=0);proof['pass']=proof.pop('pass_')
        native_complete(receipt,proof)
        for field,value in (('exit_code',0),('timed_out',True),('role_proof_pass',False),('profile_cleanup_hresult','0x80070005')):
            changed=dict(receipt);changed[field]=value
            with self.assertRaises(RuntimeError):native_complete(changed,proof)

    def test_exact_mandatory_registration(self):
        admission({'failed_gate':'results/M4/native/gate_result.json'})
        for row in (None,{},dict(failed_gate='../old/gate_result.json')):
            with self.assertRaises(RuntimeError):admission(row)

    def test_historical_suffix_is_byte_identical(self):
        old=b'OLD FAIL\r\n';prefix=b'NEW STATUS\n';current=prefix+old
        a=hashlib.sha256(old).hexdigest();b=hashlib.sha256(current).hexdigest()
        self.assertTrue(prefix_ok(old,current,prefix,a,b))
        self.assertFalse(prefix_ok(old,current+b'x',prefix,a,b))
        self.assertFalse(prefix_ok(old,current.replace(b'FAIL',b'PASS'),prefix,a,b))
