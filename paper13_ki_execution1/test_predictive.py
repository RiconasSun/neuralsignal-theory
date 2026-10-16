import copy
import itertools
import unittest
import numpy as np
from scipy.special import gammaln,logsumexp
from . import predictive as e
from . import models as m


class PredictiveTests(unittest.TestCase):
    def fixture(self):
        rng=np.random.default_rng(203);y=rng.poisson(.2,(8,30,8));q=rng.normal(size=(8,30,11))
        bundle={'baseline_scalers':{},'baseline_thetas':{},'Bstar':'B2'}
        for name in ['B0','B1','B2','B3','B4']:
            raw,sources=m.raw_features(y,q,name);state=m.fit_scale(raw)
            bundle['baseline_scalers'][name]={**{k:v.tolist() for k,v in state.items()},'source_units':sources.tolist()}
            theta=rng.normal(0,.02,(8,raw.shape[-1]));theta[:,0]=np.log(.2)
            bundle['baseline_thetas'][name]=theta.ravel().tolist()
        _,state=m.continuous_features(y,(.3,1.),11)
        bundle['C']={'theta':rng.normal(0,.03,16).tolist(),'tau':[.3,1.],'seed':11,'state':{k:v.tolist() for k,v in state.items()}}
        bundle['D']={'theta':rng.normal(0,.05,16).tolist(),'p':.9}
        bundle['S']={'theta':rng.normal(0,.05,16).tolist(),'p':.5}
        return y,q,bundle

    def test_complete_fullunit_prediction_parity_with_frozen_models(self):
        y,q,bundle=self.fixture();result=e.evaluate(y,q,bundle)
        for name in ['B0','B1','B2','B3','B4']:
            raw,_=m.raw_features(y,q,name);s=bundle['baseline_scalers'][name]
            x=m.scale(raw,{k:np.asarray(s[k]) for k in ['mean','sd']})
            eta=m.glm_predict(bundle['baseline_thetas'][name],x)
            self.assertAlmostEqual(result['scores'][name],float(m.poisson_scores(y[:,5:],eta[:,5:]).mean()),13)
        offset=e.baseline_eta(y,q,bundle,'B4')
        for name in ['D','S']:
            state=bundle[name];score=m.hmm_eval(state['theta'],y,offset,state['p'],0,gradient=False,return_scores=True)
            self.assertAlmostEqual(result['scores'][name],float(score[:,5:].sum()/y[:,5:].size),13)
        state=bundle['C'];x,_=m.continuous_features(y,state['tau'],state['seed'],{k:np.asarray(v) for k,v in state['state'].items()})
        expected=float(m.poisson_scores(y[:,5:],m.glm_predict(state['theta'],x,offset)[:,5:]).mean())
        self.assertAlmostEqual(result['scores']['C'],expected,13)
        self.assertEqual(result['scores']['Bstar'],result['scores']['B2'])

    def test_omitted_unit_canary_invariance_all_models(self):
        y,q,bundle=self.fixture();mask=np.array([True]*4+[False]*4)
        original=e.evaluate(y,q,bundle,units=mask);changed=y.copy();changed[:,:,~mask]+=1000
        modified=e.evaluate(changed,q,bundle,units=mask)
        for name in original['scores']:self.assertAlmostEqual(original['scores'][name],modified['scores'][name],13)
        self.assertEqual(original['nominal_unit_bins'],8*25*4)
        raw_zero=y.copy();raw_zero[:,:,~mask]=0
        incorrect=e.baseline_eta(raw_zero,q,bundle,'B4')[:,:,mask]
        proper=e.baseline_eta(y,q,bundle,'B4',mask)
        self.assertGreater(float(np.max(np.abs(incorrect-proper))),1e-5)

    def test_29bin_alignment_denominator_and_input_state_not_mutated(self):
        y,q,bundle=self.fixture();before=copy.deepcopy(bundle)
        result=e.evaluate(y[:,:29],q[:,:29],bundle)
        self.assertEqual(result['scored_bins_per_epoch'],24);self.assertEqual(result['nominal_unit_bins'],8*24*8)
        self.assertEqual(bundle,before)

    def test_HMM_donor_filter_independent_path_enumeration(self):
        y=np.array([[[0,1],[1,0],[0,0],[2,0],[1,1],[0,1],[1,0]]]);donor=y[:,::-1].copy()
        offset=np.zeros_like(y,dtype=float)-1.;delta=np.array([[.2,-.1],[-.2,.1]]);p=.9
        got=e.hmm_scores(y,donor,offset,delta.ravel(),p)[0]
        expected=[]
        for t in range(y.shape[1]):
            den=[];num=[]
            for path in itertools.product(range(2),repeat=t+1):
                value=-np.log(2.)
                for j in range(t):
                    eta=offset[0,j]+delta[path[j]]
                    value+=float((donor[0,j]*eta-np.exp(eta)-gammaln(donor[0,j]+1)).sum())
                    value+=np.log(p if path[j]==path[j+1] else 1-p)
                den.append(value);eta=offset[0,t]+delta[path[t]]
                num.append(value+float((y[0,t]*eta-np.exp(eta)-gammaln(y[0,t]+1)).sum()))
            expected.append(logsumexp(num)-logsumexp(den))
        np.testing.assert_allclose(got,expected,atol=1e-13,rtol=1e-13)
        changed=donor.copy();changed[:,-1]+=100
        np.testing.assert_array_equal(got,e.hmm_scores(y,changed,offset,delta.ravel(),p)[0])

    def test_frozen_zeroSD_C_coordinates_and_mean_reference(self):
        y,q,bundle=self.fixture();model=copy.deepcopy(bundle['C'])
        model['state']['count_sd'][3]=0.;model['state']['h_sd'][0]=0.
        x=e.C_features(y,model);changed=y.copy();changed[:,:,3]+=100
        np.testing.assert_array_equal(x,e.C_features(changed,model))
        self.assertEqual(float(np.abs(x[:,:,:,0]).max()),0.)

    def test_donor_history_separated_from_original_scored_outcomes(self):
        y,q,bundle=self.fixture();donor=y[:,::-1].copy()
        result=e.evaluate(y,q,bundle,history_driver=donor,filter_driver=donor,return_sequences=True)
        offset=e.baseline_eta(donor,q,bundle,'B4')
        expected=e.hmm_scores(y,donor,offset,bundle['D']['theta'],.9)
        np.testing.assert_allclose(result['joint_bin_log_scores']['D'],expected,atol=0)
        for name in ['B0','B1']:
            self.assertAlmostEqual(result['scores'][name],e.evaluate(y,q,bundle)['scores'][name],13)

    def test_invalid_inputs_not_silently_cleaned_or_dropped(self):
        y,q,bundle=self.fixture()
        for bad in [y.astype(float)+.5,y.astype(float)*np.nan,-np.ones_like(y)]:
            with self.assertRaises(ValueError):e.evaluate(bad,q,bundle)
        with self.assertRaises(ValueError):e.evaluate(y,q,bundle,units=np.zeros(8,dtype=bool))
        with self.assertRaises(ValueError):e.evaluate(y,q[:,:29],bundle)


if __name__=='__main__':unittest.main(verbosity=2)
