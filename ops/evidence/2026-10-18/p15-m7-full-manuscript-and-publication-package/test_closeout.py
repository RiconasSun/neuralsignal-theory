"""Synthetic document metadata gate tests; no Git mutation or neural execution."""
import copy,runpy,unittest
from unittest.mock import patch
from pathlib import Path
E=Path(__file__).resolve().parent
C=runpy.run_path(str(E/'closeout.py'))
F=C['valid_review'];G=F.__globals__

class ClosureMetadataTests(unittest.TestCase):
    def receipt(self):return dict(decision='ACCEPTED_RESULTS_LOCKED_PUBLICATION_PACKAGE',open_P0=0,open_P1=0,candidate_sha256='matched',baseline_sha256='matched',report_sha256='matched',report_path='synthetic-review.md')
    def check_receipt(self,r):
        with patch.dict(G,{'read':lambda p:r,'sha':lambda p:'matched'}):return F(Path('synthetic.json'))
    def test_matching_typed_receipt(self):self.assertEqual(self.check_receipt(self.receipt())['open_P1'],0)
    def test_boolean_zero_cannot_substitute_integer_review_count(self):
        r=self.receipt();r['open_P0']=False
        with self.assertRaises(AssertionError):self.check_receipt(r)
    def test_stale_candidate_rejected(self):
        r=self.receipt();r['candidate_sha256']='stale'
        with self.assertRaises(AssertionError):self.check_receipt(r)
    def test_rejected_review_not_promoted(self):
        r=self.receipt();r['decision']='REPAIR_REQUIRED'
        with self.assertRaises(AssertionError):self.check_receipt(r)
    def test_missing_current_readback_never_becomes_terminal(self):
        fn=C['matrix'];g=fn.__globals__
        fake_read=lambda p:{'source_sha256':'matched'} if Path(p).name=='baseline.json' else {'remote_readback_verified':False}
        with patch.dict(g,{'proof':lambda *a:True,'read':fake_read,'sha':lambda p:'matched'}):
            with self.assertRaises(AssertionError):fn(Path('s'),Path('n'),Path('r'),Path('g'),terminal=True)

if __name__=='__main__':unittest.main()
