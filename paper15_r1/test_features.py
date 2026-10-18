"""Production causal features and A-only transformations, synthetic fixtures only."""
import unittest
import numpy as np
from .features import nuisance, observed_arrays, design, dct_state, fit_scale, scale


class FeatureTests(unittest.TestCase):
    def trials(self):
        return [dict(intervals_0=0.,stimOn_times=1.,goCue_times=.9,response_times=1.3,feedback_times=1.4,
            intervals_1=2.,choice=-1.,feedbackType=1.,contrastLeft=.25,contrastRight=None)]
    def wheel(self):
        wt=np.arange(-1,3,.01);return wt,np.sin(wt)
    def test_all_37_columns_strict_event_boundary(self):
        wt,wp=self.wheel();b=np.array([[.5,1.,1.05,1.3,1.35,1.4,1.45]])
        x=nuisance(self.trials(),[0],b,[.5],wt,wp)
        self.assertEqual(x.shape,(1,7,37))
        self.assertEqual(x[0,1,5],0);self.assertEqual(x[0,2,5],.25)
        self.assertEqual(x[0,3,13],0);self.assertEqual(x[0,4,13],1)
        self.assertEqual(x[0,5,15],0);self.assertEqual(x[0,6,16],1)
    def test_full_37_numeric_oracle_with_previous_trial_and_wheel(self):
        trials=self.trials()+[dict(intervals_0=3.,stimOn_times=4.,goCue_times=3.9,response_times=4.3,
            feedback_times=4.4,intervals_1=5.,choice=1.,feedbackType=-1.,contrastLeft=.25,contrastRight=None)]
        wt=np.arange(-1.,7.);wp=2*wt
        got=nuisance(trials,[1],np.array([[4.45]]),[3.5],wt,wp)[0,0]
        hour=4.45/3600
        expected=[.145,.145**2,.45,.45**2,.45**3,.25,0,1,0,.1125,0,1,.55,1,1,1,-1,1,-1,
            .001,.001**2,hour,hour**2,2,0,0,0,2,0,0,0,2,0,0,0,16,0]
        self.assertEqual(len(expected),37);np.testing.assert_allclose(got,expected,atol=1e-12,rtol=0)
    def test_future_behavior_perturbation_invariance(self):
        wt,wp=self.wheel();b=np.array([[.5,.75,1.]])
        original=nuisance(self.trials(),[0],b,[.5],wt,wp)
        wp[wt>=1.1]+=1000;tr=self.trials();tr[0]['choice']=1;tr[0]['feedbackType']=-1
        np.testing.assert_array_equal(original,nuisance(tr,[0],b,[.5],wt,wp))
    def test_half_open_counts_and_causal_history(self):
        times=np.array([.5,.55,1.,1.05,1.5]);labels=np.zeros(5,int)
        y,h,b,e,warm=observed_arrays(times,labels,[0],[1.])
        self.assertEqual(warm,10);self.assertEqual(int(y.sum()),4)
        self.assertEqual(h[0,0].tolist(),[0,0,0,0])
        self.assertEqual(y[0,10,0],1)
        self.assertEqual(h[0,10,0],0)
    def test_all_four_lag_windows_share_exact_target_microedges(self):
        times=1.+(np.arange(21)-10)*.05;labels=np.zeros(len(times),int)
        for delta in [.05,.1]:
            y,h,starts,_,warm=observed_arrays(times,labels,[0],[1.],delta=delta)
            np.testing.assert_array_equal(y,np.full_like(y,int(round(delta/.05))))
            np.testing.assert_allclose(h[0,warm:],np.full_like(h[0,warm:],20.),atol=1e-14)
            self.assertEqual(starts[0,warm],1.)
        times=1.+(np.arange(16)-5)*.05;labels=np.zeros(len(times),int)
        _,h,_,_,warm=observed_arrays(times,labels,[0],[1.],warmup=.25,history=.25)
        np.testing.assert_allclose(h[0,warm:],20.,atol=1e-14)
    def test_neural_future_perturbation_invariance(self):
        t=np.array([.55,.8,1.2,1.4]);l=np.zeros(4,int)
        y,h,*_=observed_arrays(t,l,[0],[1.]);t[2:]=[1.3,1.45]
        y2,h2,*_=observed_arrays(t,l,[0],[1.])
        np.testing.assert_array_equal(y[:,:12],y2[:,:12]);np.testing.assert_array_equal(h[:,:12],h2[:,:12])
    def test_no_history_cross_epoch_gap(self):
        t=np.array([1.45,2.55]);l=np.zeros(2,int)
        y,h,*_=observed_arrays(t,l,[0],[1.,3.])
        self.assertEqual(h[1,0].sum(),0);self.assertEqual(y[1].sum(),1)
    def test_A_score_only_scale_and_constant_fixedzero(self):
        raw=np.array([[[100.,9.],[200.,9.],[1.,9.],[3.,9.]]])
        state=fit_scale(raw,2);self.assertEqual(state['mean'],[2.,9.]);self.assertEqual(state['sd'],[1.,0.])
        other=np.array([[[10000.,90.]]]);np.testing.assert_array_equal(scale(other,state),np.array([[[3.,0.]]]))
    def test_DCT_exact_basis_and_finite_history_reset(self):
        rng=np.random.Generator(np.random.PCG64(1));y=rng.poisson(.3,(2,20,8))
        q,state=dct_state(y,2,.1);r=np.asarray(state['R'])
        np.testing.assert_allclose(r.T@r,np.eye(2),atol=1e-14)
        self.assertEqual(q.shape,(2,20,2));self.assertAlmostEqual(sum(state['weights']),1.)
        changed=y.copy();changed[0,15:]+=20
        q2,_=dct_state(changed,2,.1,state=state)
        np.testing.assert_array_equal(q[:,:15],q2[:,:15]);np.testing.assert_array_equal(q[1],q2[1])
    def test_design_full_nesting_shared_scale(self):
        x=np.arange(2*20*37).reshape(2,20,37)/1000;h=np.zeros((2,20,32))
        matrix,state,active=design(x,h,10)
        self.assertEqual(matrix.shape,(2,20,70));self.assertTrue((matrix[:,:,0]==1).all())
        self.assertFalse(active[38:].any());self.assertTrue((matrix[:,:,38:]==0).all())
    def test_rich_drift_exact_four_additions(self):
        wt,wp=self.wheel();b=np.array([[.5,1.,1.4]])
        original=nuisance(self.trials(),[0],b,[.5],wt,wp);rich=nuisance(self.trials(),[0],b,[.5],wt,wp,True)
        self.assertEqual(rich.shape[-1],41);np.testing.assert_array_equal(original,rich[:,:,:37])


if __name__=='__main__':unittest.main(verbosity=2)
