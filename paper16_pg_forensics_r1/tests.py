"""Synthetic arithmetic/parser guards and saved-report contracts; no fitting."""
import ast
import hashlib
import json
import sys
import unittest
from unittest.mock import patch
import numpy as np
from . import audit as a


class SavedForensicsTests(unittest.TestCase):
    def test_outward_signs_and_interior(self):
        x = np.array([-1., -1., 1., 1., 0.])
        np.testing.assert_array_equal(a.outward(x, [3., -3., -4., 4., 5.], [-1.]*5, [1.]*5), [0., -3., 0., 4., 5.])

    def test_bound_epsilon_and_not_clipped_gradient(self):
        np.testing.assert_array_equal(a.outward([-1.+5e-13, -1.+2e-12], [7., 8.], [-1., -1.], [1., 1.]), [0., 8.])

    def test_nonfinite_shape_and_bounds_fail_closed(self):
        for x, g, lo, hi in [([0.], [float('nan')], [-1.], [1.]), ([0.], [1., 2.], [-1.], [1.]), ([2.], [1.], [-1.], [1.])]:
            with self.assertRaises(RuntimeError):a.outward(x, g, lo, hi)

    def test_scientific_gate_not_success(self):
        result = a.load(a.OLD/'NUMERICAL_FAILURE_SUMMARY.json')
        self.assertTrue(result['optimizer_success'])
        self.assertGreater(result['PG'], result['original_PG_threshold'])
        self.assertEqual(result['scientific_verdict'], 'STOP_NUMERICAL_REQUIRED_GATE')

    def test_no_production_or_optimizer_import(self):
        tree = ast.parse((a.P/'audit.py').read_text(encoding='utf8'))
        imported = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):imported += [x.name for x in node.names]
            if isinstance(node, ast.ImportFrom):imported += [node.module]
        self.assertTrue(set(imported) <= {'argparse', 'csv', 'hashlib', 'io', 'json', 'math', 'collections', 'pathlib', 'numpy'})
        self.assertFalse(any(n in sys.modules for n in ['paper16_development_r3.models', 'paper16_m1.code.spec', 'scipy.optimize']))

    def test_raw_member_denial_before_npz_decode(self):
        rel = 'paper16_development_r3/work/prepared/733457989/S02/state.npz'
        with patch.object(a.np, 'load', side_effect=AssertionError('NPZ must not be decoded')):
            with self.assertRaisesRegex(RuntimeError, 'Forbidden'):a.read_members(a.R/rel, ['raw'], {rel: a.sha(a.R/rel)})

    def test_hash_tamper_denial_before_decode(self):
        rel = a.load(a.OLD/'NUMERICAL_FAILURE_SUMMARY.json')['folder']+'/initial.npz'
        with patch.object(a.np, 'load', side_effect=AssertionError('NPZ must not be decoded')):
            with self.assertRaisesRegex(RuntimeError, 'changed NPZ'):a.read_members(a.R/rel, ['x0'], {rel: '0'*64})

    def test_other_prepared_or_B_npz_denied(self):
        rel = 'paper16_development_r3/work/prepared/726162197/MAIN/state.npz'
        with patch.object(a.np, 'load', side_effect=AssertionError('NPZ must not be decoded')):
            with self.assertRaisesRegex(RuntimeError, 'Only registered A'):a.read_members(a.R/rel, ['unit_ids'], {rel: a.sha(a.R/rel)})

    def test_missing_member_fail_closed(self):
        rel = a.load(a.OLD/'NUMERICAL_FAILURE_SUMMARY.json')['folder']+'/initial.npz'
        class Missing:
            files = []
            def __enter__(self):return self
            def __exit__(self, *args):pass
            def __getitem__(self, key):raise AssertionError('Must reject before decode')
        with patch.object(a.np, 'load', return_value=Missing()):
            with self.assertRaisesRegex(RuntimeError, 'Missing saved'):a.read_members(a.R/rel, ['x0'], {rel: a.sha(a.R/rel)})

    def test_metadata_lazy_allowlist(self):
        rel = 'paper16_development_r3/work/prepared/733457989/S02/state.npz'
        read = []
        class Metadata:
            files = ['raw', 'y', 'unit_ids', 'active', 'mean', 'scale']
            def __enter__(self):return self
            def __exit__(self, *args):pass
            def __getitem__(self, key):
                read.append(key)
                if key not in ['unit_ids', 'active', 'mean', 'scale']:raise AssertionError('Neural decode')
                return np.ones(1)
        with patch.object(a.np, 'load', return_value=Metadata()):
            a.read_members(a.R/rel, ['unit_ids', 'active', 'mean', 'scale'], {rel: a.sha(a.R/rel)})
        self.assertEqual(set(read), {'unit_ids', 'active', 'mean', 'scale'})

    def test_fd_fixed_step_and_coordinate_identity(self):
        import csv
        with (a.P/'FAILED_COORDINATE_ANALYSIS.csv').open(encoding='utf8') as stream:
            rows = list(csv.DictReader(stream))
        self.assertEqual(len(rows), 37)
        for i, row in enumerate(rows):self.assertEqual(int(row['packed_index']), i)
        self.assertEqual(rows[26]['feature'], 'color_times_order')
        self.assertEqual(rows[26]['original_feature_index'], '27')
        self.assertEqual(rows[26]['bound_status'], 'INTERIOR')
        self.assertGreater(float(rows[26]['outward_PG_component']), 1e-5)
        self.assertEqual([r['bound_status'] for r in rows].count('LOWER'), 2)
        self.assertTrue(all('FD_1e-05' in r for r in rows))

    def test_history_line_search_not_all_accepted(self):
        calls = [
            {'event': 'RESERVED_BEFORE_EVALUATION', 'call': 1, 'iterations': 0},
            {'event': 'COMPLETED', 'call': 1, 'objective': 10., 'gradient_inf': 2.},
            {'event': 'RESERVED_BEFORE_EVALUATION', 'call': 2, 'iterations': 0},
            {'event': 'COMPLETED', 'call': 2, 'objective': 11., 'gradient_inf': 3.},
            {'event': 'RESERVED_BEFORE_EVALUATION', 'call': 3, 'iterations': 0},
            {'event': 'COMPLETED', 'call': 3, 'objective': 9., 'gradient_inf': 1.}]
        fg, accepted = a.align_history(calls, [{'iteration': 1}], {0: 10., 1: 9.})
        self.assertEqual(len(fg), 3);self.assertEqual(accepted[0]['call'], 3)
        calls[-1]['call'] = 4
        with self.assertRaises(RuntimeError):a.align_history(calls, [{'iteration': 1}], {})

    def test_saved_trajectory_contract(self):
        t = a.load(a.P/'SAVED_TRAJECTORY_ANALYSIS.json')
        self.assertEqual(len(t['saved_FG_calls']), 275)
        self.assertEqual(len(t['accepted_vectors']), 254)
        self.assertEqual(t['accepted_objective_increase_count_protocol_derived'], 0)
        self.assertLessEqual(t['last_accepted_relative_reduction'], 1e-12)
        self.assertGreater(t['saved_endpoint_PG'], 1e-5)
        self.assertEqual(t['inactive_features'], [{'original_index': 23, 'name': 'running_missing'}])

    def test_all952_censored_comparison(self):
        c = a.load(a.P/'ACCEPTED_FIT_COMPARISON.json')
        self.assertEqual(c['strata']['all']['n'], 952)
        self.assertEqual(c['strata']['all']['termination'], {'CONVERGENCE: NORM OF PROJECTED GRADIENT <= PGTOL': 952})
        self.assertLess(c['strata']['all']['PG']['max'], 2e-6)
        self.assertEqual(sum(v['n'] for k, v in c['strata'].items() if k.startswith('model_')), 952)


if __name__ == '__main__':
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(SavedForensicsTests)
    run = unittest.TextTestRunner(stream=sys.stdout, verbosity=2).run(suite)
    raise SystemExit(not run.wasSuccessful())
