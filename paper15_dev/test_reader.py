"""Synthetic-only A extraction and physiological regression checks."""
import unittest
import numpy as np
from .reader import authorize, project_A
from .physiology import unit_qc


class ReaderTests(unittest.TestCase):
    def test_final_denied_before_any_payload(self):
        with self.assertRaises(PermissionError):authorize('final','A',dict(subject='final',allocation='FINAL_RESERVED'),{})
    def test_B_E_denied(self):
        for role in ['B','E','C','D']:
            with self.assertRaises(PermissionError):authorize('dev',role,dict(subject='dev',allocation='DEVELOPMENT'),{})
    def test_failed_metadata_denied(self):
        with self.assertRaises(PermissionError):authorize('dev','A',dict(subject='dev',allocation='DEVELOPMENT'),dict(result=dict(prephysiology_possible=False)))
    def test_only_A_half_open_export(self):
        t=np.array([0.,1.,1.5,2.,3.]);l=np.arange(5)
        at,al=project_A(t,l,1,2,5,[0,10],30000)
        self.assertEqual(at.tolist(),[1,1.5]);self.assertEqual(al.tolist(),[1,2])
    def test_B_E_values_do_not_change_A_export(self):
        t=np.array([1.,1.5,2.5,3.]);l=np.array([0,1,0,1]);expected=project_A(t,l,1,2,2,[0,10],30000)
        t[2:]=[8.,9.];l[2:]=[999,999]
        actual=project_A(t,l,1,2,2,[0,10],30000)
        for x,y in zip(expected,actual):np.testing.assert_array_equal(x,y)
    def test_unpartitionable_nan_fail_closed(self):
        with self.assertRaises(ValueError):project_A(np.array([1.,np.nan]),np.array([0,0]),1,2,1,[0,10],30000)
    def test_A_order_fail_closed(self):
        with self.assertRaises(ValueError):project_A(np.array([1.5,1.]),np.array([0,0]),1,2,1,[0,10],30000)
    def fixture(self):
        ids=np.arange(0,160,4);epochs=np.column_stack((ids*2.,ids*2.+1))
        times=[];labels=[]
        for lo,hi in epochs:
            for unit in range(3):
                ts=lo+np.array([.1,.3,.5,.7]) if unit<2 else lo+np.array([.1,.3,.5])
                times.extend(ts);labels.extend([unit]*len(ts))
        ix=np.argsort(times,kind='stable')
        return np.asarray(times)[ix],np.asarray(labels)[ix],ids,epochs
    def test_frozen_rate_pairs_quartiles_and_lexical_ranking(self):
        t,l,ids,epochs=self.fixture();metrics,rank=unit_qc(t,l,[0,1,2],['b','a','c'],ids,epochs,160)
        self.assertEqual([x['cluster_id'] for x in rank],[1,0])
        self.assertEqual(metrics[0]['A_spikes'],160);self.assertEqual(metrics[0]['A_within_epoch_ISI_pairs'],120)
        self.assertEqual(metrics[0]['original_A_quartile_exposures'],[10]*4)
        self.assertEqual(metrics[0]['original_A_quartile_rates'],[4]*4)
        self.assertIn('ISI_PAIRS_LT_99',metrics[2]['exclusion_reasons'])
    def test_genuine_zero_is_observed_rejected_unit(self):
        t,l,ids,epochs=self.fixture();metrics,rank=unit_qc(t,l,[9],['zero'],ids,epochs,160)
        self.assertEqual(metrics[0]['A_exposure_seconds'],40);self.assertEqual(metrics[0]['A_spikes'],0)
        self.assertFalse(rank)
    def test_no_ISI_across_epoch_boundaries(self):
        # Adjacent epoch-edge spikes never create a cross-epoch refractory pair.
        ids=np.array([0,1]);epochs=np.array([[0.,1.],[1.,2.]])
        metrics,_=unit_qc(np.array([.9999,1.0001]),np.array([0,0]),[0],['x'],ids,epochs,2)
        self.assertEqual(metrics[0]['A_within_epoch_ISI_pairs'],0)
        self.assertEqual(metrics[0]['A_refractory_pairs'],0)
    def test_original_quartile_not_rebalanced_after_missing(self):
        t,l,ids,epochs=self.fixture();take=ids<80
        metrics,_=unit_qc(t,l,[0],['x'],ids[take],epochs[take],160)
        self.assertEqual(metrics[0]['original_A_quartile_exposures'],[10,10,0,0])
        self.assertFalse(metrics[0]['primary_qualified'])


if __name__=='__main__':unittest.main(verbosity=2)
