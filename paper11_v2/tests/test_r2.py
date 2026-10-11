"""Independent R2 numerical/context/access tests, not experimental findings."""
import sys
import unittest
from pathlib import Path

import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
sys.path.insert(0,str(Path(__file__).resolve().parent))
import r2_models as models
import r2_data as data
import predictive_models as frozen
import test_r1_models as oracles


def kernel_audit():
    y,x,offset = oracles.fixture()
    score_error,gradient_error,cases = 0.,0.,0
    for k in [1,2,4]:
        for lag in [0,1,5]:
            new = models.StatePoisson(y,offset,k,lag)
            old = frozen.StatePoisson(y,offset,k,lag)
            for seed in [11,23,37]:
                theta = new.initial(seed)
                independent = oracles.state_oracle(theta,y,offset,k,lag)
                score_error = max(score_error,float(np.max(np.abs(new.score_bins(theta)-independent)))/y.shape[-1])
                for ridge in [.001,.01,.1,1.]:
                    g,_ = oracles.gradient_error(new,theta,lambda p:oracles.state_oracle(p,y,offset,k,lag,prefixes=False),ridge)
                    gradient_error = max(gradient_error,g)
                    np.testing.assert_allclose(new.objective(theta,ridge)[1],old.objective(theta,ridge)[1],atol=1e-12,rtol=0)
                    cases += 1
    if score_error>1e-10 or gradient_error>1e-6:
        raise AssertionError('Batch-parallel exact kernel numerical gate failed')
    return {'score_error_nats_unit_bin':score_error,'gradient_error':gradient_error,'cases':cases,
            'oracle':'Independent exhaustive path enumeration and finite differences, plus sequential frozen kernel parity'}


class R2Tests(unittest.TestCase):
    def test_exact_kernel_oracles(self):
        self.assertEqual(kernel_audit()['cases'],108)

    def test_causal_score_prefix_and_trial_reset(self):
        y,x,offset = oracles.fixture()
        for k,lag in [(2,0),(4,1),(4,5)]:
            a = models.StatePoisson(y,offset,k,lag)
            theta = a.initial(23)
            changed = y.copy(); changed[0,1:] += 3
            b = models.StatePoisson(changed,offset,k,lag)
            np.testing.assert_array_equal(a.score_bins(theta)[:,:1],b.score_bins(theta)[:,:1])
            separate = models.StatePoisson(y[1:],offset[1:],k,lag)
            np.testing.assert_array_equal(a.score_bins(theta)[1:],separate.score_bins(theta))

    def test_context_excludes_future_outcomes_and_unavailable_load(self):
        rows = []
        for tid in [1,2,3]:
            for label,onset,duration in [('Fixation_ss8_c1_m2',-6,1),('Stimulus_ss8_xxxxxxxx',-5,2),('Maintenance',-3,3),('Response_c1',2,0),('Probe_m2_H',0,0)]:
                rows.append({'trial':str(tid),'nix_event':label,'onset':str(onset),'duration':str(duration)})
        x,_ = data.event_context(rows,[1,2],{1:4,2:8,3:6},[1,2])
        np.testing.assert_array_equal(x[:,:10,4],0.)
        self.assertEqual(x[0,10,2],1.)
        self.assertEqual(x[0,30,3],1.)
        altered = [{**r,'nix_event':r['nix_event'].replace('_c1','_c999').replace('_m2','_m999')} for r in rows]
        np.testing.assert_array_equal(x,data.event_context(altered,[1,2],{1:4,2:8,3:1000},[1,2])[0])

    def test_missing_or_unknown_event_schedule_stops(self):
        with self.assertRaises(ValueError):
            data.event_context([], [1], {1:4}, [1])

    def test_train_only_transforms(self):
        train = np.array([[[0.,1.],[1.,1.]],[[0.,1.],[1.,1.]]])
        val = np.array([[[0.,999.],[1.,999.]]])
        xt,xv,pt,pv,audit = data.train_transforms([1,2],[100],train,val)
        self.assertEqual(audit['context_columns'],[0])
        self.assertEqual(pv[0],99.)
        np.testing.assert_array_equal(xt,train[:,:,:1])
        np.testing.assert_array_equal(xv,val[:,:,:1])

    def test_frozen_budget_and_models_unchanged(self):
        self.assertIs(models.fit_model,frozen.fit_model)
        self.assertIs(models.PoissonGLM,frozen.PoissonGLM)
        self.assertEqual(models.RecurrentPoisson.__module__,'predictive_models_code1')


if __name__ == '__main__':
    unittest.main()
