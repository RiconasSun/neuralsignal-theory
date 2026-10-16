import unittest
from unittest.mock import patch
from . import final_D as d
from .test_final_D_integration import IntegrationTests
from paper13_ki_execution1.sensitivity_plan import MANDATORY


class FailureRetentionTests(unittest.TestCase):
    def test_first_sensitivity_error_keeps_already_computed_primary_before_stop(self):
        root,allocation,c,sealed,models,export=IntegrationTests().fixture()
        with patch.object(d,'P',root),patch.object(d,'ROOT',root),patch.object(d,'ALLOCATION',allocation),patch.object(d,'approved',return_value='synthetic-source'),patch.object(d,'prior_gates',return_value=(c,sealed,models)),patch.object(d,'export',side_effect=export) as source,patch.object(d,'nuisance',side_effect=lambda record,epochs:d.np.zeros((len(epochs),30,11))),patch.object(d.sensitivity_scores,'score_mouse',side_effect=ValueError('injected first sensitivity failure')),patch.object(d,'run_controls',side_effect=AssertionError('no controls after sensitivity stop')),patch('builtins.print'):
            with self.assertRaisesRegex(ValueError,'first sensitivity failure'):d.run()
            mouse=c['mouse_order'][0]
            saved=d.b.read(root/'results/final_D/primary_mouse'/(mouse+'.json'))
            self.assertEqual(saved['mouse_id'],mouse);self.assertEqual(len(saved['result']['scores']),9)
            self.assertEqual(saved['result']['nominal_unit_bins'],12000)
            self.assertTrue((root/'results/final_D'/(mouse+'_bin_scores.npz')).exists())
            self.assertFalse((root/'results/FINAL_D_RESULTS.json').exists())
            with self.assertRaises(FileExistsError):d.run()
            self.assertEqual(source.call_count,1)

    def test_new_nonrecent_coverage_failure_stops_retains_panel_and_no_retry(self):
        root,allocation,c,sealed,models,export=IntegrationTests().fixture()
        report={'panels':{name:{'required_coverage_pass':name not in ['recent_event','deep_PL5_PL6a']} for name in MANDATORY}}
        with patch.object(d,'P',root),patch.object(d,'ROOT',root),patch.object(d,'ALLOCATION',allocation),patch.object(d,'approved',return_value='synthetic-source'),patch.object(d,'prior_gates',return_value=(c,sealed,models)),patch.object(d,'export',side_effect=export) as source,patch.object(d,'nuisance',side_effect=lambda record,epochs:d.np.zeros((len(epochs),30,11))),patch.object(d.sensitivity_scores,'score_mouse',return_value={}),patch.object(d.sensitivity_scores,'aggregate',return_value=report),patch.object(d,'run_controls',return_value={'synthetic_stub_only':True}),patch('builtins.print'):
            with self.assertRaisesRegex(d.ScientificStop,'deep_PL5_PL6a'):d.run()
            saved=d.b.read(root/'results/final_D/sensitivity_report.json')
            self.assertFalse(saved['panels']['deep_PL5_PL6a']['required_coverage_pass'])
            self.assertFalse(saved['panels']['recent_event']['required_coverage_pass'])
            self.assertTrue((root/'results/final_D/primary_results.json').is_file())
            self.assertFalse((root/'results/FINAL_D_RESULTS.json').exists())
            with self.assertRaises(FileExistsError):d.run()
            self.assertEqual(source.call_count,9)


if __name__=='__main__':unittest.main()
