"""New Final worker orchestration regressions on synthetic fixtures only."""
import tempfile
import unittest
from pathlib import Path
import numpy as np
from .calibration import configurations,fit_one,check_production_gate,claim_attempt,failure_policy
from .test_models import fixture
from .source import read,P


class FinalCalibration(unittest.TestCase):
    def test_twelve_exact_global_configs_no_final_search(self):
        c=configurations();self.assertEqual(len(c),12)
        self.assertEqual({(x['family'],x['ridge']) for x in c},
            {('B0',0.),('B1',.01),('B2',.01),('B3',1.),('B4',.1),('C',.1),('D',.01),('S',.01)})
        self.assertEqual([(x['k'],x['seed']) for x in c if x['family']=='D'],[(3,11),(3,23),(3,37)])
        self.assertEqual([(x['k'],x['seed']) for x in c if x['family']=='S'],[(4,11),(4,23),(4,37)])

    def test_synthetic_actual_worker_fits_and_denies_second_attempt(self):
        scratch=P/'work/synthetic_test_tmp';scratch.mkdir(parents=True,exist_ok=True)
        assert scratch.resolve().is_relative_to((P/'work').resolve())
        with tempfile.TemporaryDirectory(dir=scratch) as tmp:
            for family in ['B0','B4','D','S']:
                model=fixture(family,3 if family=='D' else 4 if family=='S' else 2)
                path=Path(tmp)/(family+'.json');config=dict(family=family,id=family,ridge=.1,seed=11)
                result=fit_one(model,config,path,'synthetic-production-binding','synthetic-C-state')
                self.assertEqual(result['status'],'NUMERICAL_PASS',result.get('error'))
                self.assertLessEqual(result['PG'],.001);self.assertTrue(result['independent']['PASS'])
                self.assertEqual(result['training_population_bins'],model.T)
                self.assertEqual(result['training_unit_bins'],model.T*model.u)
                before=path.read_bytes()
                with self.assertRaises(FileExistsError):fit_one(model,config,path,'synthetic-production-binding','synthetic-C-state')
                self.assertEqual(before,path.read_bytes())

    def test_incomplete_production_gate_denied(self):
        for gate in [{},{'approved_selected_C_calibration':True,'hashes':{}}]:
            with self.assertRaises(PermissionError):check_production_gate(gate)

    def test_original_failure_branches_not_silently_narrowed(self):
        for family in ['B0','B1','B2','B3','B4','C','D','S']:
            row=dict(status='NUMERICAL_FAIL',configuration=dict(family=family))
            self.assertEqual(failure_policy(row,sensitivity=True),'CASE_FAMILY_UNAVAILABLE_NO_RETRY')
            self.assertEqual(failure_policy(row),'PRIMARY_BASELINE_STOP' if family.startswith('B') else 'SECONDARY_FAMILY_UNAVAILABLE_NO_RETRY')
            row['error']='injected implementation/source integrity failure'
            self.assertEqual(failure_policy(row,sensitivity=True),'CRITICAL_INTEGRITY_STOP')
            self.assertEqual(failure_policy(row),'CRITICAL_INTEGRITY_STOP')
        self.assertEqual(failure_policy(dict(status='STARTED')),'CRITICAL_INTEGRITY_STOP')


if __name__=='__main__':unittest.main()
