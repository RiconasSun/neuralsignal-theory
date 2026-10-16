import copy
import unittest
from unittest.mock import patch
import numpy as np
from . import control_core as c
from . import test_predictive as fixtures


class ControlTests(unittest.TestCase):
    def test_temporal_preserves_each_stratum_unit_epoch_counts(self):
        y=np.arange(8*30*8).reshape(8,30,8)
        out=c.temporal(y,np.random.default_rng(130101))
        np.testing.assert_array_equal(np.sort(out.reshape(8,6,5,8),axis=2),np.sort(y.reshape(8,6,5,8),axis=2))
        self.assertFalse(np.array_equal(y,out));np.testing.assert_array_equal(y,np.arange(y.size).reshape(y.shape))

    def test_donor_derangement_never_crosses_order_quartile(self):
        ordinal=np.r_[np.arange(61,91),np.arange(91,121)]
        out=c.donors(ordinal,np.random.default_rng(130102))
        self.assertTrue(np.all(out!=np.arange(60)))
        np.testing.assert_array_equal((ordinal[out]-1)//30,(ordinal-1)//30)
        self.assertEqual(sorted(out.tolist()),list(range(60)))
        with self.assertRaises(ValueError):c.donors([61,62,91],np.random.default_rng(1))

    def test_history_and_task_metadata_operators_keep_outcomes_fixed(self):
        y,q,bundle=fixtures.PredictiveTests().fixture();ordinal=np.arange(91,99)
        with patch.object(c,'evaluate',return_value='saved') as score:
            self.assertEqual(c.replicate('history',y,q,bundle,ordinal,np.random.default_rng(130102)),'saved')
            args,kwargs=score.call_args;np.testing.assert_array_equal(args[0],y);np.testing.assert_array_equal(args[1],q)
            np.testing.assert_array_equal(kwargs['history_driver'],kwargs['filter_driver'])
            c.replicate('task_order',y,q,bundle,ordinal,np.random.default_rng(130103))
            args,kwargs=score.call_args;np.testing.assert_array_equal(args[0],y)
            self.assertEqual(sorted(map(lambda a:a.tobytes(),args[1])),sorted(map(lambda a:a.tobytes(),q)))

    def test_conditional_null_sequential_means_match_independent_B2_formula(self):
        y,q,bundle=fixtures.PredictiveTests().fixture();bundle=copy.deepcopy(bundle);bundle['Bstar']='B2'
        class Recorder:
            def __init__(self):self.calls=[]
            def poisson(self,means):self.calls.append(means.copy());return np.full(means.shape,len(self.calls)%3,dtype=np.int64)
        rng=Recorder();out=c.conditional_counts(q,bundle,rng)
        scaler=bundle['baseline_scalers']['B2'];mean=np.asarray(scaler['mean']);sd=np.asarray(scaler['sd']);theta=np.asarray(bundle['baseline_thetas']['B2']).reshape(8,4)
        for t in range(30):
            h=np.zeros((8,8,3))
            for k,lags in enumerate([[1],[2,3],[4,5]]):
                for lag in lags:
                    if t>=lag:h[:,:,k]+=out[:,t-lag]
            raw=np.concatenate([np.ones((8,8,1)),h],axis=-1)
            x=np.divide(raw-mean,sd,out=np.zeros_like(raw),where=sd!=0)
            np.testing.assert_allclose(rng.calls[t],np.exp((x*theta).sum(axis=-1)),rtol=2e-14)

    def test_null_overflow_is_failure_without_clipping(self):
        _,q,bundle=fixtures.PredictiveTests().fixture();bundle['Bstar']='B0';bundle['baseline_thetas']['B0']=[1000]*8
        with self.assertRaises(FloatingPointError):c.conditional_counts(q,bundle,np.random.default_rng(1))

    def test_inclusive_plus_one_Holm2_and_exact_999_denominator(self):
        mice=[str(i) for i in range(8)];scores={m:{k:0. for k in c.LABELS} for m in mice}
        for m in mice:scores[m]['D']=1.;scores[m]['C']=1.
        arrays={s:np.zeros((999,8,9)) for s in c.SUITES}
        arrays['conditional_Bstar'][:24,:,c.LABELS.index('D')]=1.
        arrays['conditional_Bstar'][:24,:,c.LABELS.index('C')]=1.
        result,_=c.summarize(arrays,scores,mice)
        self.assertEqual(result['beyond_baseline_null_guards']['D']['conditional_Bstar_p'],.025)
        self.assertEqual(result['beyond_baseline_null_guards']['D']['conditional_Bstar_Holm2_p'],.05)
        arrays['temporal']=arrays['temporal'][:-1]
        with self.assertRaises(ValueError):c.summarize(arrays,scores,mice)
