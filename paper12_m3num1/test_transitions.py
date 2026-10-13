import unittest
from transitions import validate,verify_bindings


class Transitions(unittest.TestCase):
    def fixtures(self):
        return dict(gate='PASS',completed_fit_count=126,converged_fit_count=126),dict(exit_code=0,timed_out=False,
            role_proof_pass=True,profile_cleanup_hresult='0x00000000'),dict(pass_=True),dict(count=7,passed=True)

    def check(self,change=None):
        gate,receipt,_,tests=self.fixtures();proof={'pass':True,'is_appcontainer':True,'capability_count':0}
        if change:change(gate,receipt,proof,tests)
        validate(gate,receipt,proof,tests,126)

    def test_complete(self):self.check()
    def test_failed_child(self):
        with self.assertRaises(RuntimeError):self.check(lambda g,r,p,t:r.update(exit_code=2))
    def test_incomplete_roster(self):
        with self.assertRaises(RuntimeError):self.check(lambda g,r,p,t:g.update(converged_fit_count=125))
    def test_missing_role(self):
        with self.assertRaises(RuntimeError):self.check(lambda g,r,p,t:p.update(capability_count=1))
    def test_failed_cleanup(self):
        with self.assertRaises(RuntimeError):self.check(lambda g,r,p,t:r.update(profile_cleanup_hresult='0x80070005'))
    def test_evidence_bindings(self):
        keys=('diagnostic_summary_sha256','diagnostic_gate_sha256','training_input_receipt_sha256','diagnosis_implementation_sha256','runtime_provenance_sha256')
        record={k:'old' for k in keys};verify_bindings(record,dict(record))
        for key in keys:
            changed=dict(record);changed[key]='changed'
            with self.assertRaises(RuntimeError):verify_bindings(record,changed)
