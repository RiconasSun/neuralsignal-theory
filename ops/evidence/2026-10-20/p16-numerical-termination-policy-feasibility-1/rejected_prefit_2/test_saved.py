"""Pure saved-evidence interruption regressions; zero optimizer/math evaluations."""
import json,tempfile,unittest,sys
from pathlib import Path
from . import reproduce as r

class SavedStopTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(dir=r.P/'work');self.folder=Path(self.tmp.name);(self.folder/'fit').mkdir()
        self.summary={'REAL_A_DIAGNOSTIC_ATTEMPTS':1,'REAL_A_NUMERICAL_PASS':None,'DIAGNOSTIC_VERDICT':'INCONCLUSIVE / STOP'}
        (self.folder/'STOP.json').write_text(json.dumps({'reason':'injected process interruption','no_retry':True}),encoding='utf8')
    def tearDown(self):self.tmp.cleanup()
    def test_partial_reserved_FG_keeps_consumed_attempt(self):
        (self.folder/'fit/CALLS.jsonl').write_text(json.dumps({'event':'RESERVED_BEFORE_EVALUATION','call':1,'iterations':0})+'\n',encoding='utf8')
        out=r.check_incomplete(self.folder,self.summary)
        self.assertEqual((out['attempts_preserved'],out['reserved_FG'],out['completed_FG']),(1,1,0))
        self.assertFalse((self.folder/'fit/RESULT.json').exists());self.assertTrue(out['missing_endpoint_not_reconstructed'])
    def test_zero_FG_interruption_not_fake_result(self):
        out=r.check_incomplete(self.folder,self.summary);self.assertEqual(out['reserved_FG'],0)
    def test_hiding_consumed_attempt_denied(self):
        with self.assertRaises(RuntimeError):r.check_incomplete(self.folder,{**self.summary,'REAL_A_DIAGNOSTIC_ATTEMPTS':0})
    def test_incomplete_cannot_claim_numerical_pass(self):
        with self.assertRaises(RuntimeError):r.check_incomplete(self.folder,{**self.summary,'REAL_A_NUMERICAL_PASS':True})
    def test_missing_interruption_proof_denied(self):
        (self.folder/'STOP.json').unlink()
        with self.assertRaises(RuntimeError):r.check_incomplete(self.folder,self.summary)
    def test_excess_budget_denied(self):
        file=self.folder/'fit/DIAGNOSTIC_CALLS.jsonl';file.write_text(''.join(json.dumps({'kind':'AD_RESERVED'})+'\n' for _ in range(4)),encoding='utf8')
        with self.assertRaises(RuntimeError):r.check_incomplete(self.folder,self.summary)
    def test_broken_completion_sequence_denied(self):
        (self.folder/'fit/CALLS.jsonl').write_text(json.dumps({'event':'COMPLETED','call':2})+'\n',encoding='utf8')
        with self.assertRaises(RuntimeError):r.check_incomplete(self.folder,self.summary)

if __name__=='__main__':
    out=unittest.TextTestRunner(stream=sys.stdout,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(SavedStopTests))
    raise SystemExit(not out.wasSuccessful())
