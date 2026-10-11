"""Report-only regressions; fixtures are not experimental findings."""
import sys
import unittest
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import report_m3_m4_audit as report


class ReportTests(unittest.TestCase):
    def test_subject_equal_session_not_unit_weight(self):
        rows = [{'subject': 'a', 'candidate': 'x', 'family': 'history', 'alpha': 1.,
                 'validation_mean_nats_unit_bin': value, 'parameters': parameters, 'wall_seconds': 1.}
                for value, parameters in [(0., 1000), (2., 1)]]
        result = report.summarize(rows)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['validation_mean_nats_unit_bin'], 1.)
        self.assertEqual(result[0]['sessions'], 2)

    def test_subject_and_candidate_never_pooled(self):
        rows = [{'subject': subject, 'candidate': candidate, 'family': 'history', 'alpha': 1.,
                 'validation_mean_nats_unit_bin': -1., 'parameters': 10, 'wall_seconds': .2}
                for subject in ['a', 'b'] for candidate in ['x', 'y']]
        self.assertEqual(len(report.summarize(rows)), 4)

    def test_certified_scores_reject_nonconvergence(self):
        session = report.load(report.PAPER / 'results/M4/sessions/sub-01_ses-01.json')
        session['candidates'][0]['converged'] = False
        with self.assertRaises(ValueError):
            report.certified_scores(session)

    def test_certified_scores_reject_nonfinite(self):
        session = report.load(report.PAPER / 'results/M4/sessions/sub-01_ses-01.json')
        session['candidates'][0]['validation_trial_scores'][0] = np.nan
        with self.assertRaises(ValueError):
            report.certified_scores(session)

    def test_real_all_baseline_candidates_retained(self):
        sessions = [report.load(path) for path in (report.PAPER / 'results/M3/sessions').glob('*.json')]
        self.assertEqual(len(sessions), 23)
        self.assertEqual(sum(len(row['candidates']) for row in sessions), 483)
        self.assertEqual(len({row['subject'] for row in sessions}), 9)
        for session in sessions:
            self.assertEqual(len({row['candidate'] for row in session['candidates']}), 21)

    def test_real_failure_not_reclassified_as_model_loss(self):
        accuracy = report.load(report.PAPER / 'results/M4/accuracy/sub-01_ses-01/continuous_k1_d1_seed71.json')
        self.assertEqual(accuracy['gate'], 'FAIL')
        self.assertTrue(all(row['conservative_discrepancy'] > .001 for row in accuracy['comparisons']))
        gate = report.load(report.PAPER / 'results/M4/gate_result.json')
        self.assertFalse(gate['final_test_count_access'])


if __name__ == '__main__':
    unittest.main()
