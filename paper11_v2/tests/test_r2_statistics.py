"""Independent synthetic/analytic sidecar checks; no experimental fixtures.

Do not execute until the parent prospectively registers this source and the
statistics source hashes. These tests never read data, outcomes or old tests.
"""

import hashlib
import itertools
from pathlib import Path
import sys
import unittest

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import r2_statistics as stats


def record(subject, session, scores):
    return {"subject": subject, "session": session, "trial_scores": scores}


class StatisticsTests(unittest.TestCase):
    def test_equal_session_then_patient_not_pooled_trials(self):
        rows = [record("A", "1", [0, 0, 0]), record("A", "2", [4]),
                record("B", "1", [10, 10])]
        result = stats.aggregate(rows)
        self.assertEqual(result["patient_means"], {"A": 2, "B": 10})
        self.assertEqual(result["overall_mean"], 6)
        self.assertEqual(result["subject_count"], 2)
        self.assertEqual(result, stats.aggregate(reversed(rows)))
        self.assertEqual(rows[0]["trial_scores"], [0, 0, 0])

    def test_session_ids_are_scoped_to_canonical_patient(self):
        result = stats.aggregate([record("site1-P1", "s", [1]),
                                  record("site2-P1", "s", [3])])
        self.assertEqual(result["subject_count"], 2)
        with self.assertRaises(ValueError):
            stats.aggregate([record("A", "s", [1]), record("A", "s", [2])])

    def test_invalid_scores_fail_closed(self):
        for scores in ([], [np.nan], [np.inf], [[1, 2]]):
            with self.subTest(scores=scores), self.assertRaises(ValueError):
                stats.aggregate([record("A", "s", scores)])
        with self.assertRaises(ValueError):
            stats.aggregate([])
        with self.assertRaises(ValueError):
            stats.aggregate([record("", "s", [1])])

    def test_sign_flip_independent_exhaustive_oracle(self):
        for delta in ([1], [0, 0], [1, 1, 1], [1, -1, 2],
                      [0.1, 0.2, -0.3], [0, 2, -3, 4]):
            # Python scalar enumeration independent of vectorized bit patterns.
            observed = abs(sum(delta))
            outcomes = [abs(sum(sign * value for sign, value in zip(signs, delta)))
                        for signs in itertools.product((-1, 1), repeat=len(delta))]
            expected = sum(value >= observed - 1e-12 for value in outcomes) / len(outcomes)
            result = stats.paired_sign_flip(delta)
            self.assertEqual(result["p_value"], expected)
            self.assertEqual(result["enumerations"], 2 ** len(delta))
            self.assertEqual(result["method"], "exact")

    def test_sign_flip_twenty_patient_boundary_and_above(self):
        result = stats.paired_sign_flip(np.ones(20))
        self.assertEqual(result["p_value"], 2 / (2 ** 20))
        self.assertEqual(result["method"], "exact")
        above = stats.paired_sign_flip(np.ones(21))
        self.assertEqual(above["method"], "monte_carlo")
        self.assertEqual(above["enumerations"], 100000)
        self.assertEqual(above["seed"], 20261011)
        self.assertGreaterEqual(above["p_value"], 1 / 100001)
        self.assertEqual(above, stats.paired_sign_flip(np.ones(21)))

    def test_subject_bootstrap_matches_independent_small_draws(self):
        delta = [0, 4]
        rng = np.random.default_rng(20261011)
        draws = rng.integers(0, 2, size=(10000, 2))
        reference = np.array([(delta[int(a)] + delta[int(b)]) / 2 for a, b in draws])
        result = stats.subject_statistics(delta)
        self.assertEqual(result["mean"], 2)
        self.assertEqual(result["ci"], (0, 4))
        self.assertAlmostEqual(result["se"], reference.std(ddof=1), places=14)
        self.assertEqual(result["sign_flip"]["p_value"], 1)
        self.assertEqual(result["replicates"], 10000)
        self.assertEqual(result["bootstrap"], "subject-only paired")
        constant = stats.subject_statistics([0.25] * 3)
        self.assertEqual(constant["ci"], (0.25, 0.25))
        self.assertEqual(constant["se"], 0)
        reversed_result = stats.subject_statistics([-value for value in delta])
        self.assertEqual(reversed_result["mean"], -result["mean"])
        self.assertEqual(reversed_result["ci"], (-4, 0))
        self.assertEqual(reversed_result["sign_flip"], result["sign_flip"])

    def test_bootstrap_budgets_cannot_change(self):
        for function, data in ((stats.trial_ci, [1, 2]),
                               (stats.subject_statistics, [1, 2]),
                               (stats.hierarchical_se, [record("A", "s", [1, 2])])):
            for options in ({"replicates": 9}, {"seed": 11}, {"seed": True}):
                with self.subTest(function=function, options=options):
                    with self.assertRaises(ValueError):
                        function(data, **options)

    def test_holm_six_hand_calculation_in_original_order(self):
        # Sorted raw .001,.01,.02,.04,.2,.9 => .006,.05,.08,.12,.4,.9.
        adjusted = stats.holm([0.04, 0.001, 0.9, 0.01, 0.2, 0.02])
        np.testing.assert_allclose(adjusted, [0.12, 0.006, 0.9, 0.05, 0.4, 0.08])
        np.testing.assert_allclose(stats.holm([0.02] * 6), [0.12] * 6)
        np.testing.assert_array_equal(stats.holm([1] * 6), np.ones(6))
        for values in ([0.1] * 5, [0.1] * 7, [0, 0, 0, 0, 0, -1],
                       [0, 0, 0, 0, 0, np.nan], [0, 0, 0, 0, 0, 1.1]):
            with self.assertRaises(ValueError):
                stats.holm(values)

    def test_whole_trial_ci_small_analytic(self):
        # Two iid draws from {0,2}: means {0,1,2} with probabilities {1/4,1/2,1/4}.
        result = stats.trial_ci([0, 2])
        self.assertEqual(result["mean"], 1)
        self.assertEqual(result["ci"], (0, 2))
        self.assertAlmostEqual(result["se"], np.sqrt(0.5), delta=0.02)
        singleton = stats.trial_ci([3])
        self.assertEqual(singleton["ci"], (3, 3))
        self.assertEqual(singleton["se"], 0)

    def test_hierarchy_keeps_all_sessions_and_primary_patient(self):
        rows = [record("A", "1", [0, 0, 0]), record("A", "2", [4]),
                record("B", "1", [10, 10])]
        result = stats.hierarchical_statistics(rows)
        # Each patient draw is 2 or 10; equal-session weighting must survive.
        rng = np.random.default_rng(20261011)
        indices = rng.integers(0, 2, size=(10000, 2))
        expected = np.array([(2 if a == 0 else 10) / 2 +
                             (2 if b == 0 else 10) / 2 for a, b in indices])
        self.assertEqual(result["mean"], 6)
        self.assertEqual(result["ci"], (2, 10))
        self.assertAlmostEqual(result["se"], expected.std(ddof=1), places=14)
        self.assertEqual(result, stats.hierarchical_statistics(reversed(rows)))
        self.assertEqual(stats.hierarchical_se(rows), result["se"])

    def test_duplicate_patient_draws_have_independent_trial_resampling(self):
        rows = [record("A", "s", [0, 2]), record("B", "s", [0, 2])]
        # Two independent patient slots, each two trials: Var(mean)=1/4.
        # Reusing trial draws on duplicate patients would inflate this variance.
        self.assertAlmostEqual(stats.hierarchical_se(rows), 0.5, delta=0.02)
        single = stats.hierarchical_statistics([record("A", "s", [0, 2])])
        self.assertAlmostEqual(single["se"], np.sqrt(0.5), delta=0.02)

    def test_patient_ci_equal_sessions_and_generator_input(self):
        rows = [record("A", "1", [0, 2]), record("A", "2", [4])]
        result = stats.patient_ci(iter(rows))
        self.assertEqual(result["mean"], 2.5)
        self.assertEqual(result["ci"], (2, 3))
        self.assertAlmostEqual(result["se"], np.sqrt(0.125), delta=0.02)
        with self.assertRaises(ValueError):
            stats.patient_ci(rows + [record("B", "1", [1])])

    def test_one_se_global_frontier_and_complexity_ridge_order(self):
        def candidate(label, scores, complexity, ridge):
            return {"config": {"name": label, "ridge": ridge},
                    "records": [record("A", "s", [scores[0]]),
                                record("B", "s", [scores[1]])],
                    "mean_parameters": complexity}

        choices = [candidate("best", [0, 4], 10, 0.001),
                   candidate("eligible", [0.7, 0.7], 2.5, 0.01),
                   candidate("ridge-tie", [0.7, 0.7], 2.5, 1.0),
                   candidate("order-tie", [0.7, 0.7], 2.5, 1.0),
                   candidate("below", [0.5, 0.5], 1, 1.0)]
        result = stats.choose_one_se(choices)
        self.assertEqual(result["best_index"], 0)
        self.assertAlmostEqual(result["best_se"], np.sqrt(2), delta=0.03)
        self.assertEqual(result["threshold"], 2 - result["best_se"])
        self.assertEqual(result["selected_index"], 2)
        self.assertEqual(result["selection"], choices[2]["config"])
        self.assertEqual([item["eligible"] for item in result["audit"]],
                         [True, True, True, True, False])
        self.assertEqual(choices[1]["mean_parameters"], 2.5)

    def test_one_se_zero_se_inclusive_threshold_and_mismatch_rejection(self):
        a = {"config": {"ridge": 0.01}, "records": [record("A", "s", [2])],
             "mean_parameters": 4}
        b = {"config": {"ridge": 1}, "records": [record("A", "s", [2])],
             "mean_parameters": 3}
        self.assertEqual(stats.choose_one_se([a, b])["selected_index"], 1)
        self.assertEqual(stats.choose_one_se([a, b])["best_se"], 0)
        for rows in ([record("B", "s", [2])], [record("A", "s", [2, 2])]):
            with self.assertRaises(ValueError):
                stats.choose_one_se([a, dict(b, records=rows)])
        with self.assertRaises(ValueError):
            stats.choose_one_se([dict(a, records=[dict(a["records"][0], trial_ids=[1])]),
                                 dict(b, records=[dict(b["records"][0], trial_ids=[2])])])
        for invalid in ([], [dict(a, mean_parameters=np.nan)],
                        [dict(a, config={"ridge": -0.1})]):
            with self.assertRaises(ValueError):
                stats.choose_one_se(invalid)

    def test_stationary_zero_ridge_is_eligible_and_can_be_selected(self):
        stationary = {"config": {"family": "stationary", "ridge": 0.0},
                      "records": [record("A", "s", [2, 2])],
                      "mean_parameters": 1}
        combined = {"config": {"family": "combined", "ridge": 1.0},
                    "records": [record("A", "s", [2, 2])],
                    "mean_parameters": 4}
        result = stats.choose_one_se([combined, stationary])
        self.assertTrue(result["audit"][1]["eligible"])
        self.assertEqual(result["selected_index"], 1)
        self.assertEqual(result["selection"], stationary["config"])
        tied = dict(combined, mean_parameters=1)
        self.assertEqual(stats.choose_one_se([stationary, tied])["selected_index"], 1)


class NullTests(unittest.TestCase):
    def arrays(self, bins):
        y = np.arange(2 * bins * 3).reshape(2, bins, 3)
        x = np.arange(2 * bins * 2).reshape(2, bins, 2)
        return y, x

    def test_bin_permutation_independent_reference_and_totals(self):
        y, _ = self.arrays(10)
        reference = y.copy()
        rng = np.random.default_rng(20261011 + 3)
        for trial, unit in itertools.product(range(2), range(3)):
            order = rng.permutation(10)
            reference[trial, :, unit] = y[trial, order, unit]
        result = stats.bin_permutation(y, 3)
        np.testing.assert_array_equal(result, reference)
        np.testing.assert_array_equal(result.sum(axis=1), y.sum(axis=1))
        np.testing.assert_array_equal(np.sort(result, axis=1), np.sort(y, axis=1))
        self.assertFalse(np.shares_memory(result, y))

    def test_circular_offsets_and_independent_index_oracle(self):
        for bins, upper in ((60, 20), (10, 9)):
            y, _ = self.arrays(bins)
            result, offsets = stats.circular_shift(y, 7)
            self.assertTrue(np.all((offsets >= 5) & (offsets <= upper)))
            for trial, unit in itertools.product(range(2), range(3)):
                shift = int(offsets[trial, unit])
                expected = [y[trial, (t - shift) % bins, unit] for t in range(bins)]
                np.testing.assert_array_equal(result[trial, :, unit], expected)
            np.testing.assert_array_equal(result.sum(axis=1), y.sum(axis=1))
            self.assertFalse(np.array_equal(y, result))

    def test_context_rotation_counts_unchanged_columns_coherent(self):
        y, x = self.arrays(60)
        counts, rotated, offsets = stats.context_rotate(y, x, 4)
        np.testing.assert_array_equal(counts, y)
        for trial in range(2):
            expected = np.array([x[trial, (t - int(offsets[trial])) % 60]
                                 for t in range(60)])
            np.testing.assert_array_equal(rotated[trial], expected)
        self.assertFalse(np.shares_memory(counts, y))
        self.assertFalse(np.shares_memory(rotated, x))

    def test_partition_substreams_stable_explicit_seed_context(self):
        name = "site-P1/session1/development"
        digest = hashlib.sha256(name.encode("utf-8")).digest()
        key = tuple(int.from_bytes(digest[i:i + 4], "little")
                    for i in range(0, 32, 4))
        expected = np.random.default_rng(np.random.SeedSequence(
            20261011 + 2, spawn_key=key)).integers(0, 100000, size=12)
        actual = stats.partition_rng(2, name).integers(0, 100000, size=12)
        np.testing.assert_array_equal(actual, expected)
        other = stats.partition_rng(2, name + "/train").integers(0, 100000, size=12)
        self.assertFalse(np.array_equal(actual, other))
        np.testing.assert_array_equal(actual, stats.partition_rng(2, name).integers(
            0, 100000, size=12))

    def test_transform_parent_api_purity_audit_and_partition_locality(self):
        for bins in (10, 60):
            y, x = self.arrays(bins)
            initial_y, initial_x = y.copy(), x.copy()
            for kind in ("bin_permutation", "circular_shift", "context_rotate"):
                args = {"external": bins == 10, "partition": "session/dev"}
                transformed, context, audit = stats.transform_null(y, x, kind, 1, **args)
                self.assertTrue(audit["count_preserved"])
                self.assertEqual(audit["before"], audit["after"])
                self.assertEqual(audit["root_seed"], 20261012)
                if kind == "context_rotate":
                    np.testing.assert_array_equal(transformed, y)
                else:
                    np.testing.assert_array_equal(context, x)
                stats.transform_null(y + 10, x, kind, 1, external=bins == 10,
                                     partition="other-session/train")
                again = stats.transform_null(y, x, kind, 1, **args)
                np.testing.assert_array_equal(transformed, again[0])
                np.testing.assert_array_equal(context, again[1])
                self.assertEqual(audit, again[2])
                self.assertFalse(np.shares_memory(transformed, y))
                self.assertFalse(np.shares_memory(context, x))
            np.testing.assert_array_equal(y, initial_y)
            np.testing.assert_array_equal(x, initial_x)

    def test_rng_does_not_touch_global_numpy_state(self):
        before = np.random.get_state()
        y, x = self.arrays(10)
        stats.transform_null(y, x, "circular_shift", 0, external=True,
                             partition="session/calibration")
        after = np.random.get_state()
        self.assertEqual(before[0], after[0])
        np.testing.assert_array_equal(before[1], after[1])
        self.assertEqual(before[2:], after[2:])

    def test_null_invalid_inputs_and_unregistered_epochs_fail_closed(self):
        y, x = self.arrays(10)
        for replicate in (-1, 200, 0.5, True):
            with self.assertRaises(ValueError):
                stats.partition_rng(replicate)
        for values in (y[:, :, :0], y[:, :0], y[:, 0], y.astype(float) + 0.5,
                       -y, np.full(y.shape, np.nan)):
            with self.assertRaises(ValueError):
                stats.bin_permutation(values, 0)
        with self.assertRaises(ValueError):
            stats.circular_shift(np.zeros((1, 20, 1)), 0)
        for options in ({"partition": ""}, {"partition": "s", "external": False}):
            with self.assertRaises(ValueError):
                stats.transform_null(y, x, "circular_shift", 0, **options)
        with self.assertRaises(TypeError):
            stats.transform_null(y, x, "circular_shift", 0, external=True)
        with self.assertRaises(ValueError):
            stats.transform_null(y, x[:, :9], "context_rotate", 0,
                                 external=True, partition="s")
        with self.assertRaises(ValueError):
            stats.transform_null(y, x, "unknown", 0, external=True, partition="s")


if __name__ == "__main__":
    unittest.main()
