import copy
import unittest
import study as r
from roster import validate

class Guards(unittest.TestCase):
    def setUp(self):self.rows=r.load(r.HERE/'original_training_diagnostics.json')['rows']
    def test_exact_roster(self):self.assertTrue(validate(self.rows))
    def test_missing_duplicate_identity_rejected(self):
        with self.assertRaises(RuntimeError):validate(self.rows[:-1])
        altered=copy.deepcopy(self.rows);altered[-1]=altered[0]
        with self.assertRaises(RuntimeError):validate(altered)
    def test_validation_fields_denied(self):
        altered=copy.deepcopy(self.rows);altered[0]['validation_LL_nats_per_unit_bin']=0
        with self.assertRaises(RuntimeError):validate(altered)
    def test_other_mouse_denied(self):
        altered=copy.deepcopy(self.rows);altered[0]['mouse_id']='different'
        with self.assertRaises(RuntimeError):validate(altered)
    def test_registered_source_and_reference_hashes(self):
        reg=r.load(r.HERE/'implementation_registration3.json')
        for name,digest in reg['sha256'].items():self.assertEqual(r.sha(r.HERE/name),digest,name)
        self.assertEqual(r.load(r.HERE/'original_training_diagnostics.json')['source_sha256'],r.load(r.HERE/'registration.json')['prior_sha256']['paper12_m4offset1/results/M4/native/comparison_rows.json'])
    def test_initial_and_terminal_stop_order(self):
        text=(r.HERE/'worker.py').read_text()
        self.assertLess(text.index("if not initial_check['passed']:stop"),text.index('fit=minimize'))
        self.assertIn("if not terminal_check['passed']:stop",text)
        self.assertNotIn('validation_LL',text)

if __name__=='__main__':unittest.main(verbosity=2)
