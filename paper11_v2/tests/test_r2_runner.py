"""Access and all-seed failure-policy regressions; no experimental fitting."""
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import run_r2 as runner


class RunnerTests(unittest.TestCase):
    def test_exact_frozen_grid(self):
        b = runner.baseline_configs()
        f = runner.family_configs()
        self.assertEqual(len(b),21)
        self.assertEqual(len(f),36)
        self.assertEqual(1+20*3+36*3,169)
        self.assertEqual(runner.SEEDS,[11,23,37])
        self.assertEqual(runner.RIDGES,[.001,.01,.1,1.])

    def test_seed_resolution_training_only(self):
        rows = [{'seed':s,'converged':True,'loss':loss,'validation_nats_per_unit_bin':score,
                 'config':{'family':'continuous'}} for s,loss,score in [(11,3,999),(23,1,-999),(37,2,888)]]
        self.assertEqual(runner.resolved(rows)['seed'],23)
        rows[0]['converged']=False
        with self.assertRaises(RuntimeError):
            runner.resolved(rows)

    def test_missing_seed_not_silently_excluded(self):
        rows = [{'seed':11,'converged':True,'loss':0,'config':{'family':'discrete'}}]
        with self.assertRaises(RuntimeError):
            runner.resolved(rows)

    def test_no_external_accessor(self):
        self.assertFalse(hasattr(runner,'external_spikes'))
        self.assertFalse(hasattr(runner,'unlock_final'))

    def test_existing_execution_never_overwritten(self):
        with patch.object(runner,'verify'),patch.object(Path,'exists',return_value=True):
            with self.assertRaisesRegex(RuntimeError,'already started'):
                runner.execute()

    def test_constructor_failure_is_preserved_and_stops_first_seed(self):
        d = {'key':'sub-fixture/ses-01','subject':'sub-fixture','validation_ids':[1],
             'feature_sha256':'fixture','ytrain':np.zeros((1,2,1)),'yval':np.zeros((1,2,1))}
        c = {'family':'history','ridge':.001}
        with patch.object(runner,'make_pair',side_effect=ValueError('fixture construction failure')),\
             patch.object(runner.base,'save') as save:
            with self.assertRaises(runner.ScientificStop) as failure:
                runner.run_candidate(d,c,runner.OUT/'fixture_no_write')
        self.assertEqual(save.call_count,1)
        self.assertEqual(failure.exception.record['seed'],11)
        self.assertFalse(failure.exception.record['converged'])
        self.assertIn('fixture construction failure',failure.exception.record['error'])


if __name__=='__main__':
    unittest.main()
