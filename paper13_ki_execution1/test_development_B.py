"""Synthetic B gating, export invariance, frozen scaling and selection tests."""
import io
import json
import uuid
import unittest
from unittest.mock import patch
import h5py
import numpy as np
from . import development_B as d
from .selection import ridge_choice,strongest


class BTests(unittest.TestCase):
    def fixture(self):
        root=d.P/'work'/('B_tests_'+uuid.uuid4().hex);root.mkdir(parents=True)
        units=[{'unit_id':i,'row':i,'electrode_row':i,'label':'PL5'} for i in range(8)]
        record={'mouse_id':'synthetic','role':'development','epochs':[{'ordinal':61+i,'start':100.+i*5,'stop':103.+i*5,'partition':'B'} for i in range(30)]}
        qc={'mouse_id':'synthetic','role':'development','partition':'A','selected_units':units,'source_freeze':'A-frozen'}
        return root,record,qc

    def test_unapproved_entry_denies_before_numerical_gate_or_values(self):
        root,_,_=self.fixture()
        with patch.object(d,'P',root),patch.object(d,'numerical_gate',side_effect=AssertionError('gate before approval')):
            with self.assertRaisesRegex(PermissionError,'Fresh B'):d.run()

    def test_final_or_wrong_B_epoch_count_denied(self):
        _,record,_=self.fixture()
        with self.assertRaises(PermissionError):d.B_windows({**record,'role':'final'})
        with self.assertRaises(d.ScientificStop):d.B_windows({**record,'epochs':record['epochs'][:29]})

    def test_required_A_numerical_gate_before_reader(self):
        _,record,qc=self.fixture()
        with patch.object(d,'approved',return_value='code'),patch.object(d.b,'read',return_value={'M3_A_NUMERICS':'FAILED_REQUIRED_GATE'}),patch.object(d,'SourceReader',side_effect=AssertionError('source before A gate')):
            with self.assertRaises(d.ScientificStop):d.export_B(record,qc,'code')
            with self.assertRaises(PermissionError):d.export_B(record,qc,'changed-code')

    def test_unit_selection_mismatch_denied_before_reader(self):
        _,record,qc=self.fixture()
        with patch.object(d,'approved',return_value='code'),patch.object(d.b,'read',side_effect=[{'M3_A_NUMERICS':'PASS','completed':390,'required':390},{**qc,'selected_units':[]}]),patch.object(d,'SourceReader',side_effect=AssertionError('source before unit gate')):
            with self.assertRaises(PermissionError):d.export_B(record,qc,'code')

    def hdf(self,record,extra):
        stream=io.BytesIO();all_times=[];ends=[]
        for unit in range(8):
            all_times.extend([e['start']+t for e in record['epochs'] for t in [.1,.7,2.9]])
            all_times.extend(extra);ends.append(len(all_times))
        with h5py.File(stream,'w') as h:
            h['units/id']=np.arange(8);h['units/spike_times']=all_times;h['units/spike_times_index']=ends
        return stream.getvalue()

    def synthetic_export(self,extra):
        root,record,qc=self.fixture();raw=self.hdf(record,extra);real_read=d.b.read
        def metadata(path):
            name=str(path).replace('\\','/')
            if name.endswith('/M3_A_GATE.json'):return {'M3_A_NUMERICS':'PASS','completed':390,'required':390}
            if name.endswith('/qc/synthetic.json'):return qc
            return real_read(path)
        with patch.object(d,'P',root),patch.object(d,'approved',return_value='code'),patch.object(d.b,'read',side_effect=metadata),patch.object(d,'SourceReader',side_effect=lambda _:io.BytesIO(raw)),patch('paper13_ki_execution1.qc.screen',side_effect=AssertionError('B QC forbidden')),patch.object(d.m,'fit_scale',side_effect=AssertionError('B scaler fitting forbidden')):
            result=d.export_B(record,qc,'code')
        with np.load(d.ROOT/result['state_file'],allow_pickle=False) as state:counts=state['counts'].copy()
        rows=[json.loads(x) for x in (root/'results/development_B/synthetic.attempts.jsonl').read_text().splitlines()]
        return counts,result,rows

    def test_synthetic_B_export_denies_QC_and_excluded_canaries(self):
        a,ra,rows=self.synthetic_export([10000.,10001.])
        b,rb,_=self.synthetic_export([20000.,30000.,40000.])
        np.testing.assert_array_equal(a,b);self.assertEqual(a.shape,(30,30,8));self.assertEqual(int(a.sum()),720)
        self.assertFalse(ra['QC_or_scaling_on_B']);self.assertFalse(ra['E_D_exported'])
        self.assertEqual([r['event'] for r in rows].count('B_UNIT_COMPLETE'),8)
        self.assertEqual(rows[-1]['event'],'B_EXPORT_COMPLETE')

    def test_score_uses_frozen_A_scaler_and_exact_unit_bins(self):
        rng=np.random.default_rng(18);a=rng.poisson(.1,(60,30,8));qb=rng.normal(2,1,(30,30,11));yb=rng.poisson(.2,(30,30,8))
        qa=rng.normal(size=(60,30,11));xa,_=d.m.raw_features(a,qa,'B1');state=d.m.fit_scale(xa)
        raw,_=d.m.raw_features(yb,qb,'B1');expected_x=d.m.scale(raw,state)
        theta=np.zeros((8,12));theta[:,0]=-2;theta[:,1]=.05
        expected=d.m.poisson_scores(yb[:,5:],d.m.glm_predict(theta.ravel(),expected_x)[:,5:]).sum()/6000
        scaler={k:v.tolist() for k,v in state.items()}
        with patch.object(d.m,'fit_scale',side_effect=AssertionError('B scaling forbidden')):
            actual=d.score_fixed(yb,qb,'B1',{'theta':theta.ravel()},scaler)
        self.assertAlmostEqual(actual,expected,14)
        self.assertNotAlmostEqual(float(expected_x[:,:,:,1].mean()),0.)

    def test_paired_SE_not_marginal_and_larger_ridge_ties(self):
        common=np.arange(8)*100.
        matrix=np.stack([common+1,common+.9,common+.8],axis=1)
        choice=ridge_choice(matrix);self.assertEqual(choice['selected_ridge'],.1)
        self.assertLess(max(choice['paired_SE']),1e-10)
        self.assertEqual(ridge_choice(np.ones((8,3)))['selected_ridge'],10.)

    def test_Bstar_requires_all_baselines_and_complexity_tie(self):
        scores={f'B{i}':np.ones(8) for i in range(5)}
        self.assertEqual(strongest(scores)['B_star'],'B0')
        scores['B3']=np.ones(8)*1.1;self.assertEqual(strongest(scores)['B_star'],'B3')
        del scores['B1']
        with self.assertRaises(ValueError):strongest(scores)

    def test_nonfinite_scores_and_insufficient_mouse_counts_stop(self):
        with self.assertRaises(ValueError):ridge_choice(np.ones((7,3)))
        with self.assertRaises(ValueError):ridge_choice(np.full((8,3),np.nan))
        y=np.zeros((30,30,8));q=np.zeros((30,30,11));scaler={'mean':np.zeros((8,1)).tolist(),'sd':np.ones((8,1)).tolist()}
        with np.errstate(over='ignore',invalid='ignore'):
            with self.assertRaises(d.ScientificStop):d.score_fixed(y,q,'B0',{'theta':np.full(8,1000.)},scaler)


if __name__=='__main__':unittest.main(verbosity=2)
