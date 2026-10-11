import sys
import unittest
from pathlib import Path
import numpy as np
import json
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import baseline_models as b


class BaselineTests(unittest.TestCase):
    def test_real_candidate_scope_and_no_silent_removal(self):
        paper = Path(__file__).resolve().parents[1]
        files = list((paper / 'results/M3/sessions').glob('*.json'))
        self.assertTrue(files, 'Real baseline execution must produce session artifacts')
        for path in files:
            result = json.loads(path.read_text())
            candidates = result['candidates']
            if len(candidates) < 21:
                self.assertEqual(result['failure'], 'REQUIRED_BASELINE_NONCONVERGED')
                self.assertFalse(candidates[-1]['convergence']['success'])
            else:
                self.assertEqual(len(candidates), 21)
                self.assertEqual({row['family'] for row in candidates}, set(b.FAMILIES))
                self.assertFalse(result['test_timestamp_values_decoded'])
                for row in candidates:
                    self.assertTrue(row['convergence']['success'])
                    self.assertFalse(set(row['train_trial_ids']) & set(row['validation_trial_ids']))
                    self.assertEqual(len(row['validation_trial_scores']), len(row['validation_trial_ids']))
                    fit = result['fits'][row['candidate']]
                    self.assertEqual(len(fit['coefficients']), result['train_shape'][2])
    def test_history_is_causal_and_resets(self):
        counts = np.zeros((2, 60, 1))
        counts[0, 59, 0] = 100
        counts[1, 1, 0] = 3
        x, names = b.design(counts, [1, 2], [8, 4], 50, 'history')
        self.assertTrue(np.all(x[1, 0, 0, 1:] == 0))
        self.assertEqual(x[1, 1, 0, names.index('past_count_lag1')], 0)
        self.assertEqual(x[1, 2, 0, names.index('past_count_lag1')], np.log1p(3))

    def test_task_load_unknown_during_fixation(self):
        counts = np.zeros((1, 60, 1))
        x, names = b.design(counts, [1], [8], 50, 'task')
        self.assertTrue(np.all(x[0, :10, 0, 1:] == 0))
        self.assertEqual(x[0, 10, 0, names.index('encoding_load8')], 1)

    def test_stationary_exact_and_unit_bin_metric(self):
        counts = np.ones((2, 60, 2))
        x, _ = b.design(counts, [1, 2], [4, 6], 50, 'stationary')
        fit = b.fit_poisson(x, counts, 0)
        self.assertTrue(fit['convergence']['success'])
        np.testing.assert_allclose(b.score(fit, x, counts), -1)
        self.assertEqual(fit['parameters'], 2)

    def test_selection_one_se_favors_simpler(self):
        candidates = [{'family': 'complex', 'alpha': 0.1, 'parameters': 20, 'validation_mean': -0.5, 'validation_se': 0.1},
                      {'family': 'simple', 'alpha': 1.0, 'parameters': 2, 'validation_mean': -0.55, 'validation_se': 0.01}]
        self.assertEqual(b.choose(candidates)['family'], 'simple')

    def test_validation_changes_cannot_change_train_scaling(self):
        counts = np.ones((2, 60, 1))
        x, _ = b.design(counts, [1, 2], [4, 6], 50, 'timing')
        fit = b.fit_poisson(x, counts, 1)
        original = fit['train_mean'].copy()
        b.score(fit, x + 0.1, counts)
        np.testing.assert_array_equal(fit['train_mean'], original)


if __name__ == '__main__':
    unittest.main()
