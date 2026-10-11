import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import numpy as np
from scipy.special import gammaln

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
import oracle_m4_num2 as old
import rqmc_poisson_filter as rqmc
import deterministic_poisson_oracle as deterministic
import run_m4_num3 as run


class NumericalTests(unittest.TestCase):
    def test_uniform_reproducibility_independence_and_balance(self):
        a = rqmc.uniforms(256, 5, 1103, 0, 'rqmc')
        np.testing.assert_array_equal(a, rqmc.uniforms(256, 5, 1103, 0, 'rqmc'))
        self.assertFalse(np.array_equal(a, rqmc.uniforms(256, 5, 1103, 1, 'rqmc')))
        self.assertTrue(np.all((a > 0) & (a < 1)))
        for column in a.T:
            np.testing.assert_array_equal(np.sort((column*256).astype(int)), np.arange(256))

    def test_budget_and_method_rejection(self):
        for count in (0, 3, 300):
            with self.assertRaises(ValueError):
                rqmc.uniforms(count, 4, 1, 0, 'rqmc')
        with self.assertRaises(ValueError):
            rqmc.uniforms(256, 4, 1, 0, 'unknown')

    def test_inverse_cdf_normalization_and_support(self):
        np.testing.assert_array_equal(rqmc.inverse_cdf([.1, 0., .9], np.array([.05, .1, .999])), [0, 2, 2])
        with self.assertRaises(ValueError):
            rqmc.inverse_cdf([-.1, 1.1], np.array([.4]))
        with self.assertRaises(ValueError):
            rqmc.inverse_cdf([.1, .8], np.array([.4]))

    def test_searchsorted_equals_dense_map(self):
        weights = np.arange(1, 258, dtype=float)
        weights /= weights.sum()
        values = np.linspace(0., .9999, 4096)
        target = (values[:, None] >= np.cumsum(weights)).sum(axis=1)
        np.testing.assert_array_equal(rqmc.inverse_cdf(weights, values), target)

    def test_final_identity_drift_rejected(self):
        with patch.object(run, 'load', return_value={'sha256': {'old': 'hash'}}), patch.object(run, 'identity', return_value={'new': 'hash'}):
            with self.assertRaises(ValueError):
                run.assert_frozen()

    def test_zero_loading_exact_continuous(self):
        model = old.fixture(1)
        model['loadings'] *= 0
        y = np.array([[0, 1, 2, 0], [1, 0, 0, 1]])
        offsets = np.full(y.shape, -1.)
        target = np.sum(y*offsets-np.exp(offsets)-gammaln(y+1), axis=1)
        for method in ('mc', 'rqmc'):
            scores, diagnostics = rqmc.particle(model, y, offsets, 256, 3, method)
            np.testing.assert_allclose(scores, target, atol=1e-13)
            self.assertAlmostEqual(diagnostics['minimum_ess_fraction'], 1)

    def test_future_observation_cannot_change_past(self):
        model = old.fixture(2)
        y = np.zeros((3, 4), dtype=int)
        offset = np.full(y.shape, -1.)
        first, _ = rqmc.particle(model, y, offset, 256, 12)
        y[-1] = 8
        second, _ = rqmc.particle(model, y, offset, 256, 12)
        np.testing.assert_array_equal(first[:-1], second[:-1])

    def test_independent_oracle_zero_loading(self):
        model = old.fixture(1)
        model['loadings'] *= 0
        y = np.array([[0, 1, 2, 0], [1, 0, 0, 1]])
        offsets = np.full(y.shape, -1.)
        actual = deterministic.scores(model, y, offsets, 48, 8)
        target = np.sum(y*offsets-np.exp(offsets)-gammaln(y+1), axis=1)
        np.testing.assert_allclose(actual, target, atol=1e-10)

    def test_independent_oracle_initial_ignores_dynamics(self):
        model = old.fixture(2)
        y = np.zeros((1, 4), dtype=int)
        offsets = np.full(y.shape, -1.)
        first = deterministic.scores(model, y, offsets, 32, 8)
        model['dynamics'] *= 7
        np.testing.assert_array_equal(first, deterministic.scores(model, y, offsets, 32, 8))

    def test_tail_requires_stability(self):
        model = old.fixture(1)
        model['dynamics'] *= 9
        with self.assertRaises(ValueError):
            deterministic.tail_log_sensitivity(model, np.array([-4.]), 12)

    def test_summary_reports_spread_not_ensemble_se(self):
        values = np.array([[0., .004], [0., -.004]])
        result = run.summary(values, np.zeros(2), np.zeros(2), 4)
        self.assertGreater(result['maximum_bin_discrepancy'], .001)
        self.assertTrue(all(x >= 0 for x in result['prefix_jensen_gap_nats_unit']))

    def test_oracle_failure_blocks_particles_and_remaining_fixtures(self):
        spec = run.load(run.SPEC)
        with tempfile.TemporaryDirectory() as directory, patch.object(run, 'oracle', return_value={'gate': 'FAIL'}), patch.object(rqmc, 'particle') as particle:
            rows, errors = run.evaluate(spec, Path(directory))
        self.assertEqual(len(rows), 1)
        self.assertEqual(len(errors), 1)
        particle.assert_not_called()

    def test_failed_accuracy_stops_after_registered_repetitions(self):
        spec = dict(run.load(run.SPEC), seeds=[1, 2], candidate_particles=[256], mc_comparator_budget=256)
        diagnostic = {'laplace_nonconverged_guides': 0, 'overflow_rates': 0}
        ref = {'gate': 'PASS', 'scores': [0., 0., 0.], 'sensitivity_nats_unit_bin': [0., 0., 0.]}
        with tempfile.TemporaryDirectory() as directory, patch.object(run, 'oracle', return_value=ref), patch.object(rqmc, 'particle', return_value=(np.ones(3), diagnostic)) as particle:
            rows, errors = run.evaluate(spec, Path(directory))
        self.assertEqual(len(rows), 1)
        self.assertEqual(particle.call_count, 4)
        self.assertEqual(len(errors), 1)

    def test_registration_rejects_source_drift(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(run, 'LOCK', Path(directory)/'lock.json'):
            first = run.register()
            self.assertTrue(first['before_new_tests'])
            with patch.object(run, 'identity', return_value={'changed': 'hash'}):
                with self.assertRaises(ValueError):
                    run.register()


if __name__ == '__main__':
    unittest.main()
