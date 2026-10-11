import copy
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import validate_num3 as audit


class AuditTests(unittest.TestCase):
    def setUp(self):
        run = audit.run
        self.args = [run.load(run.OUTPUT/'qc_report.json'), run.load(run.OUTPUT/'gate_result.json'),
            run.load(run.OUTPUT/'output_validation.json'), run.load(run.OUTPUT/'progress.json'),
            run.load(run.LOCK), run.digest(run.LOCK)]

    def test_current_saved_negative_is_bound(self):
        self.assertEqual(audit.verify(*self.args)['recomputed_gate'], 'FAIL')

    def test_wrong_saved_source_rejected(self):
        self.args[0]['source_sha256'] = {'stale': 'hash'}
        with self.assertRaises(ValueError):
            audit.verify(*self.args)

    def test_wrong_saved_lock_rejected(self):
        self.args[1]['lock_sha256'] = 'stale'
        with self.assertRaises(ValueError):
            audit.verify(*self.args)

    def test_replica_tampering_rejected(self):
        self.args[0]['fixtures'][0]['evaluations'][-1]['scores'][0][0] += .1
        self.args[3]['fixtures'] = copy.deepcopy(self.args[0]['fixtures'])
        with self.assertRaises(ValueError):
            audit.verify(*self.args)

    def test_false_pass_rejected(self):
        self.args[1]['gate'] = 'PASS'
        with self.assertRaises(ValueError):
            audit.verify(*self.args)

    def test_missing_seed_rejected(self):
        self.args[0]['fixtures'][0]['evaluations'][-1]['diagnostics'].pop()
        self.args[3]['fixtures'] = copy.deepcopy(self.args[0]['fixtures'])
        with self.assertRaises(ValueError):
            audit.verify(*self.args)


if __name__ == '__main__':
    unittest.main()
