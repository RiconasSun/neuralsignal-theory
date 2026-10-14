import copy
import unittest
import audit_saved as a

def rows():
    result=[]
    for item in a.roster()[:61]:
        row=dict(zip(('mouse_id','session_id','region','family','size','ridge','seed'),item))
        row.update(converged=True,optimizer_success=True,penalized_training_objective=1.,projected_gradient=.0001,validation_access=False,final_access=False,terminal_gradient_check=dict(passed=True))
        result.append(row)
    result[36].update(converged=False,projected_gradient=.0016052460119657442)
    result[-1].update(converged=False,optimizer_success=False,iterations=2000,projected_gradient=.692604771056502,bound_hits=0,optimizer_message='STOP: TOTAL NO. OF ITERATIONS REACHED LIMIT',terminal_gradient_check=dict(passed=False,scaled_gradient_error=.00020676306270142608))
    # d2/.001/11 follows the 12 dimension-1 configurations.
    result[36].update(converged=True,projected_gradient=.0001)
    result[48].update(converged=False,projected_gradient=.0016052460119657442)
    return result

class AuditRegression(unittest.TestCase):
    def test_valid_saved_roster(self): self.assertEqual(a.validate_rows(rows(),'smoke'),(61,59))
    def test_missing_fit(self):
        with self.assertRaises(ValueError): a.validate_rows(rows()[:-1],'smoke')
    def test_duplicate_identity(self):
        data=rows();data[1]=copy.deepcopy(data[0])
        with self.assertRaises(ValueError): a.validate_rows(data,'smoke')
    def test_solver_success_not_convergence(self):
        data=rows();data[48]['converged']=True
        with self.assertRaises(ValueError): a.validate_rows(data,'smoke')
    def test_nan_rejected_as_converged(self):
        data=rows();data[0]['projected_gradient']=float('nan')
        with self.assertRaises(ValueError): a.validate_rows(data,'smoke')
    def test_failed_identity_retained(self):
        data=rows();data[-1]['seed']=37
        with self.assertRaises(ValueError): a.validate_rows(data,'smoke')
    def test_frozen_error_retained(self):
        data=rows();data[-1]['terminal_gradient_check']['scaled_gradient_error']=1e-6
        with self.assertRaises(ValueError): a.validate_rows(data,'smoke')
    def test_final_access_rejected(self):
        data=rows();data[0]['final_access']=True
        with self.assertRaises(ValueError): a.validate_rows(data,'smoke')
    def test_timed_out_receipt_rejected(self):
        gate=dict(gate='FAIL',validation_access=False,final_access=False)
        receipt=dict(exit_code=2,timed_out=True,profile_cleanup_hresult='0x00000000',role_proof_pass=True,final_values_exposed_to_analysis=False,final_holdout_evaluated=False)
        proof=dict(pass_=True)
        with self.assertRaisesRegex(ValueError,'INCOMPLETE_RECEIPT'): a.validate_completion(gate,receipt,proof,{},'smoke')
    def test_uncompleted_exit_rejected(self):
        with self.assertRaisesRegex(ValueError,'NATIVE_EXIT_GATE'): a.validate_completion(dict(gate='FAIL'),dict(exit_code=None),{}, {},'smoke')

if __name__ == '__main__': unittest.main(verbosity=2)
