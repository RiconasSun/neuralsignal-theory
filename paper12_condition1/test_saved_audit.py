import copy
import unittest
from audit_saved import check_endpoint,sha_vector

def fixture():
    t=[0.]*384;g=[0.]*384
    endpoint={'theta':t,'analytical_gradient':g,'AD_gradient':g.copy(),'theta_sha256':sha_vector(t),'objective':1.,'AD_objective':1.,'PG':0.,'AD_PG':0.,'AD_abs_error':0.,'AD_scaled_error':0.,'bounds_pass':True,'finite':True,'AD_objective_error':0.,'transform_objective_error':0.,'transform_gradient_error':0.,'coordinate_roundtrip_error':0.,'independent_checks_pass':True,'feasible':True,'objective_gradient_calls':1,'accepted_steps':1}
    history={'calls':[{'call':1,'finite':True}],'accepted':[{'accepted':1,'call_count':1,'objective':1.,'PG':0.}],'call_count':1,'accepted_count':1,'warm_accepted':0}
    return endpoint,history,{'kind':'lbfgsb','objective_gradient_call_cap':2}

class SavedEvidence(unittest.TestCase):
    def test_valid_saved_gate(self):
        e,h,p=fixture();self.assertTrue(check_endpoint(e,h,p,[1.]*384))
    def test_no_optimizer_success_shortcut(self):
        e,h,p=fixture();e['optimizer_success']=True;e['PG']=.7
        with self.assertRaises(RuntimeError):check_endpoint(e,h,p,[1.]*384)
    def test_changed_vector_detected(self):
        e,h,p=fixture();e['theta'][0]=.1
        with self.assertRaises(RuntimeError):check_endpoint(e,h,p,[1.]*384)
    def test_truncated_gradient_detected(self):
        e,h,p=fixture();e['AD_gradient'].pop()
        with self.assertRaises(RuntimeError):check_endpoint(e,h,p,[1.]*384)
    def test_budget_expansion_detected(self):
        e,h,p=fixture();p['objective_gradient_call_cap']=0
        with self.assertRaises(RuntimeError):check_endpoint(e,h,p,[1.]*384)
    def test_scope_of_historical_FD(self):
        e,h,p=fixture();e['historical_fixed_checker']={'passed':False};self.assertTrue(check_endpoint(e,h,p,[1.]*384))
    def test_gradient_error_fabrication_detected(self):
        e,h,p=fixture();e['AD_gradient'][4]=.01
        with self.assertRaises(RuntimeError):check_endpoint(e,h,p,[1.]*384)
    def test_transform_gradient_failure_cannot_pass(self):
        e,h,p=fixture();e['transform_gradient_error']=.01
        with self.assertRaises(RuntimeError):check_endpoint(e,h,p,[1.]*384)
    def test_AD_objective_error_fabrication_detected(self):
        e,h,p=fixture();e['AD_objective']=2.
        with self.assertRaises(RuntimeError):check_endpoint(e,h,p,[1.]*384)
    def test_nonfinite_history_cannot_claim_feasibility(self):
        e,h,p=fixture();h['calls'][0]['finite']=False
        with self.assertRaises(RuntimeError):check_endpoint(e,h,p,[1.]*384)
    def test_baseline_parser_preserves_all42_without_padding_spaces(self):
        from package_results import baseline_items
        text='\n'.join(f'| REQ-{i:03d} | requirement{i} |oracle{i} |' for i in range(1,43))
        items=baseline_items(text);self.assertEqual(len(items),42);self.assertEqual(items[10][2],'oracle11');self.assertEqual(items[16][2],'oracle17')

if __name__=='__main__':unittest.main(verbosity=2)
