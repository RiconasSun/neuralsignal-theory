import unittest
import numpy as np
from accepted_fit import original_pg,accepted_fit
from glm import pg
import study as r
class AcceptanceTests(unittest.TestCase):
    def test_near_bound_distinguishes_old_oracle(self):
        theta=np.array([-8+1e-8]);gradient=np.array([1.])
        self.assertLess(pg(theta,gradient),.001);self.assertEqual(original_pg(theta,gradient),1)
    def test_exact_bounds_and_interior(self):
        self.assertEqual(original_pg(np.array([-8.,8.]),np.array([1.,-1.])),0)
        self.assertEqual(original_pg(np.array([0.,0.]),np.array([.1,-.2])),.2)
    def test_registered_coefficients_identical(self):
        reg=r.load(r.HERE/'original_pg_certificate_execution_registration.json');gate=r.load(r.HERE/'results/original_pg_certificate/native/gate_result.json')
        self.assertEqual(gate['new_model_cases'],reg['registered_expected_reconstructed_cases'])
        for p in (r.HERE/'results/original_pg_certificate/native').glob('*_fit.json'):
            old=r.load(r.HERE/'results/science/native'/p.name);new=r.load(p);self.assertEqual(old['coefficient_sha256'],new['coefficient_sha256'])
            for z in new['records']:self.assertLessEqual(z['original_definition_PG'],.001);self.assertLessEqual(z['AD_original_definition_PG'],.001);self.assertTrue(z['passed'])
    def test_acceptance_wrapper_on_synthetic(self):
        x=np.column_stack((np.ones(8),np.arange(8)/8));y=np.array([0,1,0,2,0,1,0,1]);w,record=accepted_fit(x,y);self.assertTrue(record['passed']);self.assertLessEqual(record['original_definition_PG'],.001)
if __name__=='__main__':unittest.main()
