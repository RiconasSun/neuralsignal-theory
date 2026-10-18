"""Frozen sensitivity semantics and nondefault numerical cases, synthetic only."""
import json
import unittest
from unittest.mock import patch
import numpy as np
import pandas as pd
from .sensitivities import CASES,metadata_case,boundary_units
from .metadata_qc import task_masks
from .models import Model
from .features import observed_arrays,nuisance
from .independent_ad import coordinate_check
from .source import R
from .sensitivity_fits import verify_plan


class SensitivityTests(unittest.TestCase):
    def fixture(self):
        a=np.arange(20)*3.;s=a+1.2
        tr=pd.DataFrame(dict(intervals_0=a,stimOn_times=s,goCue_times=s-.1,feedback_times=s+.8,
            intervals_1=a+2.9,contrastLeft=np.full(20,.25),contrastRight=np.full(20,np.nan)))
        tr.loc[2,'stimOn_times']=a[2]+.3;tr.loc[2,'goCue_times']=a[2]+.2
        roles,mask,checks,cuts=task_masks(tr,[0,100],[],True)
        return dict(trials=json.loads(tr.to_json(orient='records')),roles=roles.tolist(),valid=mask.tolist(),
            check_masks={k:v.tolist() for k,v in checks.items()},selected_probe_saturation_session_seconds=[],
            result=dict(recording_sync_support=[0,100],partitions={r:list(x) for r,x in cuts.items()}))
    def test_exact_eleven_ids_and_unit_capacities(self):
        self.assertEqual([x['id'] for x in CASES],[f'S{i:02}' for i in range(1,12)])
        self.assertEqual([x['units'] for x in CASES[:3]],[5,12,20])
        self.assertEqual(CASES[-1]['units'],5)
    def test_shorter_neural_warmup_preserves_behavior_role_guards(self):
        original=self.fixture();short=metadata_case(original,CASES[4])
        self.assertFalse(original['valid'][2]);self.assertTrue(short['valid'][2])
        self.assertEqual(original['roles'],short['roles'])
        self.assertEqual(original['check_masks']['boundary_guard'],short['check_masks']['boundary_guard'])
        self.assertEqual(original['check_masks']['behavioral_support'],short['check_masks']['behavioral_support'])
    def test_saturation_dilation_changes_mask_never_targets_to_zero(self):
        state=self.fixture();s=state['trials'][3]['stimOn_times']
        state['selected_probe_saturation_session_seconds']=[[s+.52,s+.53]]
        ten=metadata_case(state,CASES[7]);fifty=metadata_case(state,CASES[8])
        self.assertTrue(ten['valid'][3]);self.assertFalse(fifty['valid'][3])
        self.assertEqual(state['trials'],fifty['trials'])
    def test_rich_drift_is_in_every_nonstationary_baseline(self):
        x=np.zeros((1,20,50));x[:,:,0]=1;y=np.zeros((1,20,2))
        expected={'B1':84,'B2':92,'B3':92,'B4':100}
        for family,count in expected.items():
            m=Model(x,y,family,nuisance=41);self.assertEqual(m.size,count)
            self.assertTrue(m.mask[38:42].all())
    def test_S05_neural_reset_shortens_but_scored_nuisance_references_unchanged(self):
        trials=[dict(intervals_0=0.,stimOn_times=1.,goCue_times=.9,response_times=1.1,feedback_times=1.2,
            intervals_1=2.,choice=1.,feedbackType=1.,contrastLeft=.25,contrastRight=None)]
        wt=np.arange(-1,3,.01);wp=wt**2
        _,_,main_b,_,main_warm=observed_arrays(np.array([]),np.array([],int),[0],[1.])
        _,_,short_b,short_neural,short_warm=observed_arrays(np.array([]),np.array([],int),[0],[1.],warmup=.25,history=.25)
        main=nuisance(trials,[0],main_b,np.array([.5]),wt,wp)
        short=nuisance(trials,[0],short_b,np.array([.5]),wt,wp)
        np.testing.assert_array_equal(main[:,main_warm:],short[:,short_warm:])
        wrong=nuisance(trials,[0],short_b,short_neural,wt,wp)
        self.assertGreater(float(np.max(np.abs(wrong[:,short_warm:]-short[:,short_warm:]))),0.)
    def test_nondefault_exposure_warmup_and_rich_gradients(self):
        rng=np.random.default_rng(15)
        for delta,warm,nuisance in [(.1,5,37),(.05,5,37),(.05,10,41)]:
            l=warm+int(.5/delta);x=rng.normal(0,.1,(1,l,1+nuisance+8));x[:,:,0]=1;y=rng.poisson(.2,(1,l,2))
            m=Model(x,y,'B4',ridge=.1,warm=warm,delta=delta,nuisance=nuisance)
            self.assertTrue(coordinate_check(m,m.initialize(),synthetic=True)['PASS'])
    def test_boundary_proxy_requires_all_five_native_contacts(self):
        atlas=json.loads((R/'paper13/metadata/atlas.json').read_text(encoding='utf8'))['msg']
        mop=next(x['id'] for x in atlas if x['acronym']=='MOp');mos=next(x['id'] for x in atlas if x['acronym']=='MOs')
        state=dict(native_cluster_channel=[2,3,6,0]);row=dict(files=[dict(role='atlas')])
        contacts=np.array([mop,mop,mop,mop,mop,mos,mop,mop,mop])
        with patch('paper15_r1.sensitivities.local_path',return_value='synthetic'),patch('paper15_r1.sensitivities.np.load',return_value=contacts):
            self.assertEqual(boundary_units(state,row),{0})
    def test_exact_case_fit_plan_rejects_added_grid_seed_or_Final_subject(self):
        import copy
        selected=dict(selected={f:f for f in ['B0','B1','B2','B3','B4']})
        candidates=[dict(id=f,available=True,configurations=[dict(family=f,ridge=0. if f=='B0' else .1)]) for f in selected['selected']]
        prep=dict(cases=CASES,records=[dict(subject='dev',case=c['id'],status='UNAVAILABLE',reasons=['registered capacity']) for c in CASES])
        prep['records'][0]=dict(subject='dev',case='S01',status='A_PREPROCESSING_SEALED',state_sha256='state')
        attempts=[dict(subject='dev',case='S01',family=f,ridge=0. if f=='B0' else .1,seed=11,state_sha256='state') for f in selected['selected']]
        plan=dict(attempts=attempts,expected_attempts=5,max_retries=0,new_hyperparameter_search=False,Final_fits=0,
            maximum_Development=550,maximum_all_registered_sensitivities=1100,
            solver=dict(maxiter=2000,maxfun=80000,maxls=40,ftol=1e-12,gtol=1e-6))
        verify_plan(plan,selected,candidates,prep,['dev'])
        for field,value in [('seed',23),('ridge',10.),('family','D'),('subject','FinalMouse')]:
            bad=copy.deepcopy(plan);bad['attempts'][1][field]=value
            with self.assertRaises(AssertionError):verify_plan(bad,selected,candidates,prep,['dev'])
        for field,value in [('maxiter',2001),('maxfun',80001),('ftol',1e-9)]:
            bad=copy.deepcopy(plan);bad['solver'][field]=value
            with self.assertRaises(AssertionError):verify_plan(bad,selected,candidates,prep,['dev'])
        for records in [[],prep['records'][:-1],prep['records']+[prep['records'][0]]]:
            bad=copy.deepcopy(prep);bad['records']=records
            with self.assertRaises(AssertionError):verify_plan(plan,selected,candidates,bad,['dev'])


if __name__=='__main__':unittest.main(verbosity=2)
