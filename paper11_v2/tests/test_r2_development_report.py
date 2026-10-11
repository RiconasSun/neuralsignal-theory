"""Analytical identity fixtures only; no execution before parent registration."""
import copy
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import r2_development_report as report


def fixture():
    configurations = [{"family": "stationary", "ridge": 0.}, {"family": "combined", "ridge": .1}]
    sessions = ["p/s1", "p/s2", "q/s1"]
    qc, rows = [], []
    for session in sessions:
        qc.append({"key": session, "subject": session.split("/")[0], "feature_sha256": "fixture",
                   "unit_ids": [1, 4], "units": 2, "train_ids": [1, 2], "train_trials": 2,
                   "validation_ids": [3, 4], "validation_trials": 2})
        for c in configurations:
            for seed in ([None] if c["family"] == "stationary" else report.runner.SEEDS):
                rows.append({"session": session, "subject": session.split("/")[0], "config": c,
                             "seed": seed, "converged": True, "error": None, "real_data": True,
                             "feature_sha256": "fixture", "validation_trial_ids": [3, 4],
                             "training_unit_bins": 240, "validation_unit_bins": 240,
                             "trial_scores": [1., 3.], "validation_nats_per_unit_bin": 2.,
                             "loss": 1., "theta": [0., 0.], "extra_parameters": 2,
                             "shared_parameters": 0, "total_parameters": 2})
    return rows, qc, configurations, sessions


class SavedIdentityTests(unittest.TestCase):
    def test_frozen_grid_and_zero_ridge_stationary(self):
        configs = report.runner.baseline_configs() + report.runner.family_configs()
        self.assertEqual(len(configs), 57)
        self.assertEqual(sum(1 if c["family"] == "stationary" else 3 for c in configs), 169)
        self.assertEqual(23 * 169, 3887)
        rows, qc, configurations, sessions = fixture()
        resolved = report.validate_records(rows, qc, configurations, sessions)
        self.assertIsNone(resolved[report.config_key(configurations[0])][0]["seed"])
        self.assertEqual(resolved[report.config_key(configurations[1])][0]["seed"], 11)

    def test_missing_failed_duplicate_or_extra_seed_denied(self):
        rows, qc, configurations, sessions = fixture()
        variants = [rows[:-1], rows + [rows[0]], copy.deepcopy(rows), copy.deepcopy(rows)]
        variants[2][0]["converged"] = False
        variants[3][0]["seed"] = 11
        for changed in variants:
            with self.assertRaises(ValueError):
                report.validate_records(changed, qc, configurations, sessions)

    def test_matched_unitbin_trial_and_feature_denials(self):
        for key, value in (("validation_trial_ids", [4, 3]), ("validation_unit_bins", 120),
                           ("training_unit_bins", 120), ("feature_sha256", "different"),
                           ("subject", "wrong"), ("total_parameters", 3),
                           ("trial_scores", [float("nan"), 3.])):
            rows, qc, configurations, sessions = fixture()
            rows[0][key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                report.validate_records(rows, qc, configurations, sessions)
        rows, qc, configurations, sessions = fixture()
        qc[0]["unit_ids"] = [1, 1]
        with self.assertRaises(ValueError):
            report.validate_records(rows, qc, configurations, sessions)

    def test_training_seed_rule_not_development_best(self):
        rows, qc, configurations, sessions = fixture()
        for row in rows:
            if row["seed"] == 23:
                row["loss"] = 0.
            if row["seed"] == 37:
                row["trial_scores"] = [20., 20.]
                row["validation_nats_per_unit_bin"] = 20.
        result = report.validate_records(rows, qc, configurations, sessions)
        self.assertEqual([r["seed"] for r in result[report.config_key(configurations[1])]], [23] * 3)

    def test_equal_session_then_equal_patient_analytical(self):
        rows = [{"subject": "p", "trial_scores": [0., 0.]},
                {"subject": "p", "trial_scores": [2.]},
                {"subject": "q", "trial_scores": [5., 5., 5.]}]
        patients, mean = report.patient_means(rows)
        self.assertEqual(patients, {"p": 1., "q": 5.})
        self.assertEqual(mean, 3.)

    def test_existing_interval_identity_not_resampling(self):
        interval = {"replicates": 10000, "seed": 20261011, "ci": [-1., 1.], "se": .5}
        report.validate_interval(interval)
        for field, value in (("replicates", 999), ("seed", 1), ("ci", [1., -1.]), ("se", -1.)):
            with self.assertRaises(ValueError):
                report.validate_interval(dict(interval, **{field: value}))


if __name__ == "__main__":
    unittest.main()
