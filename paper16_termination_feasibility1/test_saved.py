"""Pure saved-evidence interruption regressions; zero optimizer/math evaluations."""
import json,tempfile,unittest,sys
from pathlib import Path
from . import reproduce as r

class SavedStopTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(dir=r.P/'work');self.folder=Path(self.tmp.name);(self.folder/'fit').mkdir()
        self.summary={'REAL_A_DIAGNOSTIC_ATTEMPTS':1,'REAL_A_NUMERICAL_PASS':None,'DIAGNOSTIC_VERDICT':'INCONCLUSIVE / STOP'}
        self.stage={'start_monotonic':100.,'deadline_monotonic':110.,'start_UTC':'2026-10-20T15:00:00+00:00','deadline_UTC':'2026-10-20T15:00:10+00:00','windows_boot_UTC':'2026-10-15T00:00:00+00:00','no_reset':True}
        self.claim={'stage':self.stage,'no_retry':True,'attempt_limit':1}
        (self.folder/'STAGE.json').write_text(json.dumps(self.stage),encoding='utf8')
        (self.folder/'STOP.json').write_text(json.dumps({'type':'InjectedProcessInterruption','message':'synthetic saved interruption','no_retry':True}),encoding='utf8')
    def tearDown(self):self.tmp.cleanup()
    def test_partial_reserved_FG_keeps_consumed_attempt(self):
        (self.folder/'fit/CALLS.jsonl').write_text(json.dumps({'event':'RESERVED_BEFORE_EVALUATION','call':1,'iterations':0,'x':[0.]*37})+'\n',encoding='utf8')
        out=r.check_incomplete(self.folder,self.summary,self.claim)
        self.assertEqual((out['attempts_preserved'],out['reserved_FG'],out['completed_FG']),(1,1,0))
        self.assertFalse((self.folder/'fit/RESULT.json').exists());self.assertTrue(out['missing_endpoint_not_reconstructed'])
    def test_zero_FG_interruption_not_fake_result(self):
        out=r.check_incomplete(self.folder,self.summary,self.claim);self.assertEqual(out['reserved_FG'],0)
    def test_hiding_consumed_attempt_denied(self):
        with self.assertRaises(RuntimeError):r.check_incomplete(self.folder,{**self.summary,'REAL_A_DIAGNOSTIC_ATTEMPTS':0},self.claim)
    def test_incomplete_cannot_claim_numerical_pass(self):
        with self.assertRaises(RuntimeError):r.check_incomplete(self.folder,{**self.summary,'REAL_A_NUMERICAL_PASS':True},self.claim)
    def test_missing_interruption_proof_denied(self):
        (self.folder/'STOP.json').unlink()
        with self.assertRaises(RuntimeError):r.check_incomplete(self.folder,self.summary,self.claim)
    def test_excess_budget_denied(self):
        file=self.folder/'fit/DIAGNOSTIC_CALLS.jsonl';file.write_text(''.join(json.dumps({'kind':'AD_RESERVED'})+'\n' for _ in range(4)),encoding='utf8')
        with self.assertRaises(RuntimeError):r.check_incomplete(self.folder,self.summary,self.claim)
    def test_broken_completion_sequence_denied(self):
        (self.folder/'fit/CALLS.jsonl').write_text(json.dumps({'event':'COMPLETED','call':2})+'\n',encoding='utf8')
        with self.assertRaises(RuntimeError):r.check_incomplete(self.folder,self.summary,self.claim)
    def test_empty_STOP_denied(self):
        (self.folder/'STOP.json').write_text('{}',encoding='utf8')
        with self.assertRaises(RuntimeError):r.check_incomplete(self.folder,self.summary,self.claim)
    def test_normal_supervision_cannot_prove_interruption(self):
        (self.folder/'STOP.json').unlink()
        (self.folder/'SUPERVISION.json').write_text(json.dumps({'returncode':0,'killed_at_deadline':False,'completed_before_deadline':True,'clock_failure':None}),encoding='utf8')
        with self.assertRaises(RuntimeError):r.check_incomplete(self.folder,self.summary,self.claim)
    def test_abnormal_supervision_proves_interruption(self):
        (self.folder/'STOP.json').unlink()
        (self.folder/'SUPERVISION.json').write_text(json.dumps({'returncode':124,'killed_at_deadline':True,'completed_before_deadline':False,'clock_failure':'deadline'}),encoding='utf8')
        self.assertEqual(r.check_incomplete(self.folder,self.summary,self.claim)['attempts_preserved'],1)
    def test_unknown_FG_event_denied(self):
        (self.folder/'fit/CALLS.jsonl').write_text(json.dumps({'event':'UNKNOWN','call':77})+'\n',encoding='utf8')
        with self.assertRaises(RuntimeError):r.check_incomplete(self.folder,self.summary,self.claim)
    def test_completion_before_reservation_denied(self):
        rows=[{'event':'COMPLETED','call':1,'objective':0.,'gradient':[0.]*37,'gradient_inf':0.},{'event':'RESERVED_BEFORE_EVALUATION','call':1,'iterations':0,'x':[0.]*37}]
        (self.folder/'fit/CALLS.jsonl').write_text(''.join(json.dumps(v)+'\n' for v in rows),encoding='utf8')
        with self.assertRaises(RuntimeError):r.check_incomplete(self.folder,self.summary,self.claim)
    def test_claim_stage_mismatch_denied(self):
        bad={**self.claim,'stage':{**self.stage,'deadline_monotonic':111.}}
        with self.assertRaises(RuntimeError):r.check_incomplete(self.folder,self.summary,bad)
    def test_wrong_diagnostic_event_denied(self):
        (self.folder/'fit/DIAGNOSTIC_CALLS.jsonl').write_text(json.dumps({'kind':'UNKNOWN','checkpoint':'initial','index':1})+'\n',encoding='utf8')
        with self.assertRaises(RuntimeError):r.check_incomplete(self.folder,self.summary,self.claim)
    def test_missing_stage_explicitly_reported(self):
        (self.folder/'STAGE.json').unlink()
        with self.assertRaises(RuntimeError):r.check_incomplete(self.folder,self.summary,self.claim)
        out=r.check_incomplete(self.folder,{**self.summary,'MISSING_SAVED_STAGE':True},self.claim)
        self.assertTrue(out['missing_saved_stage'])

if __name__=='__main__':
    out=unittest.TextTestRunner(stream=sys.stdout,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(SavedStopTests))
    raise SystemExit(not out.wasSuccessful())
