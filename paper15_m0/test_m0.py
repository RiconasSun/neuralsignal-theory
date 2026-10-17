import unittest, json
import numpy as np
import pandas as pd
from .coverage import P, region_of, trial_mask, allocate
from .numerics import map_clock, overlap, count_bins

class Checks(unittest.TestCase):
    def test_distinct_anatomy(self):
        regs=['MOp','SSp-ul','SSp-bfd','SSs']
        for a,r in [('MOp2/3','MOp'),('SSp-ul6a','SSp-ul'),('SSp-bfd4','SSp-bfd'),('SSs','SSs')]:self.assertEqual(region_of(a,regs),r)
        for a in ['MOs5','SSp','MOpjunk','SSp-ul20','root',None]:self.assertIsNone(region_of(a,regs))
    def test_trial_cue_before_stim_allowed(self):
        t=pd.DataFrame(dict(intervals_0=[0.],stimOn_times=[.2],goCue_times=[.1],feedback_times=[1.],intervals_1=[2.],bwm_include=[True],saturation_stim_plus06=[False]))
        self.assertTrue(trial_mask(t)[0])
        for k,v in [('saturation_stim_plus06',True),('bwm_include',False),('goCue_times',3.),('stimOn_times',float('nan')),('intervals_1',.4)]:
            q=t.copy();q[k]=v;self.assertFalse(trial_mask(q)[0])
    def test_no_animal_pseudoreplication(self):
        rows=pd.DataFrame([dict(subject=str(i),lab='a' if i%2 else 'b') for i in range(20)])
        a=allocate(rows,'fixed');b=allocate(rows.sample(frac=1,random_state=11),'fixed')
        self.assertEqual(a,b);self.assertEqual(sum(x['allocation']=='FINAL_RESERVED' for x in a),8)
    def test_zero_and_halfopen_edges(self):
        t=np.array([0.,.05,.1,.2]);lab=np.array([1,1,2,1]);edges=np.array([0.,.1,.2])
        c,m=count_bins(t,lab,[1,2,3],edges)
        np.testing.assert_array_equal(c,[[2,0,0],[0,1,0]]);self.assertTrue(m.all())
    def test_invalid_is_not_zero(self):
        c,m=count_bins(np.array([.1]),np.array([1]),[1,2],np.array([0.,.1,.2]),[[.11,.12]])
        self.assertEqual(c.shape,(2,2));np.testing.assert_array_equal(m,[True,False]);self.assertEqual(c[0,0],0)
    def test_clock_and_invalid_map(self):
        s=np.array([[0.,2.],[10.,12.001]])
        np.testing.assert_allclose(map_clock(s,[0.,5.,10.]),[2.,7.0005,12.001])
        for z in [s[::-1],np.array([[0.,0.],[0.,1.]]),np.array([[0.,0.],[1.,np.nan]])]:
            with self.assertRaises(AssertionError):map_clock(z,[1.])
    def test_nonfinite_unordered_stop(self):
        for t in [np.array([np.nan]),np.array([2.,1.])]:
            with self.assertRaises(AssertionError):count_bins(t,np.ones(len(t)),[1],np.array([0.,3.]))
    def test_frozen_pilots_development_only(self):
        f=json.loads((P/'PILOT_IDENTITY_FREEZE.json').read_text(encoding='utf8'))
        self.assertEqual(len(f['pilots']),2);self.assertTrue(all(x['allocation']=='DEVELOPMENT' for x in f['pilots']))
        a=pd.read_csv(P/'results/ALLOCATION.csv');self.assertFalse(set(x['subject'] for x in f['pilots'])&set(a[a.allocation.eq('FINAL_RESERVED')].subject))
    def test_bounded_inventory(self):
        f=json.loads((P/'PILOT_FILE_FREEZE.json').read_text(encoding='utf8'));self.assertLessEqual(f['total_bytes'],1200000000)
        self.assertTrue(all(x['bytes']<=450000000 for x in f['files']));self.assertEqual(len(f['files']),24)
        self.assertTrue(all(not any(q in x['key'] for q in ['.cbin','.mp4','waveforms']) for x in f['files']))
if __name__=='__main__':unittest.main()
