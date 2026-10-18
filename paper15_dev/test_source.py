"""Focused source/role regression oracles, no real neural data access."""
import copy
import json
import unittest
import numpy as np
import pandas as pd
from .source import P, R, resolve, roster
from .metadata_access import permit_metadata
from .metadata_qc import partition, task_masks


class SourceTests(unittest.TestCase):
    def test_exact_original_roster(self):
        rows=roster();self.assertEqual(len(rows),20)
        self.assertEqual(sum(x['allocation']=='DEVELOPMENT' for x in rows),12)
        self.assertEqual(len({x['subject'] for x in rows}),20)
    def test_ap_name_regression(self):
        row=next(x for x in roster() if x['subject']=='CSHL059')
        inv=json.loads((P/'source'/(row['eid']+'_s3.json')).read_text())
        self.assertFalse(resolve(row,inv)['issues'])
    def test_duplicate_essential_denied(self):
        row=roster()[0];inv=json.loads((P/'source'/(row['eid']+'_s3.json')).read_text())
        x=copy.deepcopy(inv);hit=next(z for z in x['objects'] if '/alf/#2025-03-03#/_ibl_trials.table.' in z['key'])
        x['objects'].append(hit.copy())
        self.assertTrue(any(z['role']=='trials' for z in resolve(row,x)['issues']))
    def test_neural_object_denied_for_all_metadata_roles(self):
        for row in roster():
            for role in ['times','clusters','amplitudes','counts']:
                with self.assertRaises(PermissionError):permit_metadata(row,role)
    def test_final_wheel_denied(self):
        row=next(x for x in roster() if x['allocation']=='FINAL_RESERVED')
        for role in ['wheel_times','wheel_position']:
            with self.assertRaises(PermissionError):permit_metadata(row,role)
    def test_final_metadata_allowed(self):
        row=next(x for x in roster() if x['allocation']=='FINAL_RESERVED')
        for role in ['trials','recording_meta','sync','saturation','metrics','uuids','atlas','cluster_channels']:
            permit_metadata(row,role)
    def test_original_partition_and_guard(self):
        roles,guard,cuts=partition(101,True)
        self.assertEqual(cuts,dict(A=(0,60),B=(60,80),E=(80,101)))
        self.assertEqual(np.flatnonzero(~guard).tolist(),[59,60,79,80])
        self.assertEqual(roles[80],'E')
    def test_final_partition(self):
        roles,guard,cuts=partition(101,False)
        self.assertEqual(cuts,dict(C=(0,60),D=(60,101)))
        self.assertEqual(np.flatnonzero(~guard).tolist(),[59,60])
    def fixture(self):
        a=np.arange(20)*3.;s=a+1.2
        return pd.DataFrame(dict(intervals_0=a,stimOn_times=s,goCue_times=s-.1,
            feedback_times=s+.8,intervals_1=a+2.9,contrastLeft=np.repeat(.25,20),contrastRight=np.repeat(np.nan,20)))
    def test_epoch_must_fit_trial(self):
        tr=self.fixture();tr.loc[2,'stimOn_times']=tr.loc[2,'intervals_0']+.3
        _,mask,checks,_=task_masks(tr,[0,100],[],True)
        self.assertFalse(mask[2]);self.assertFalse(checks['neural_epoch_inside_trial'][2])
    def test_sync_domain_not_extrapolated(self):
        tr=self.fixture();_,mask,checks,_=task_masks(tr,[0,1],[],True)
        self.assertFalse(mask.any());self.assertEqual(int(checks['recording_sync_support'].sum()),0)
    def test_behavioral_support_saturation(self):
        tr=self.fixture();s=tr.stimOn_times.iloc[2]
        _,mask,checks,_=task_masks(tr,[0,100],[[s-.9,s-.8]],True)
        self.assertFalse(mask[2]);self.assertFalse(checks['no_known_saturation'][2])
    def test_valid_zero_wheel_is_coverage_not_neural_count(self):
        tr=self.fixture();wt=np.arange(-1,65,.01)
        _,mask,_,_=task_masks(tr,[0,100],[],True,(wt,np.zeros(len(wt))))
        self.assertGreater(mask.sum(),0)
    def test_future_wheel_does_not_change_metadata_mask(self):
        tr=self.fixture();wt=np.arange(-1,65,.01);wp=np.zeros(len(wt))
        _,mask,_,_=task_masks(tr,[0,100],[],True,(wt,wp))
        wp[wt>62]=1e9
        self.assertTrue(np.array_equal(mask,task_masks(tr,[0,100],[],True,(wt,wp))[1]))
    def test_unknown_contrast_excluded_not_zero_filled(self):
        tr=self.fixture();tr.loc[3,['contrastLeft','contrastRight']]=np.nan
        _,mask,_,_=task_masks(tr,[0,100],[],True)
        self.assertFalse(mask[3])


if __name__=='__main__':unittest.main(verbosity=2)
