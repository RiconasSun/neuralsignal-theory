import unittest
from unittest.mock import patch
import numpy as np
import calibration as m
from glm import raw,scale,transform,obj
from baseline_fit import objective
from accepted_fit import original_pg

class CalibrationTests(unittest.TestCase):
    def setUp(self):
        self.c=np.repeat(np.arange(8),24);self.o=np.arange(len(self.c));self.y=np.random.default_rng(12).poisson(.3,(len(self.c),20,32))
        self.s={'mouse_id':'m','session_id':'s','trial_ids':{'C':[str(x) for x in self.o]},'unit_ids':{k:[str(x) for x in range(32)] for k in ('CA1','DG')}}
        self.z={k+'_C':self.y.copy() for k in ('CA1','DG')};self.z.update({k+'_unit_ids':np.array(self.s['unit_ids'][k]) for k in ('CA1','DG')});self.z.update(conditions_C=self.c,orders_C=self.o,trial_ids_C=np.array(self.s['trial_ids']['C']))
    def test_C_schema(self):self.assertTrue(m.validate_arrays(self.z,self.s))
    def test_D_field_rejected_before_access(self):
        z=dict(self.z);z['D']=object()
        with self.assertRaises(PermissionError):m.validate_arrays(z,self.s)
    def test_actual_trial_masks(self):
        s=dict(self.s);s['trial_ids']={'C':self.s['trial_ids']['C'][::-1]}
        with self.assertRaises(ValueError):m.validate_arrays(self.z,s)
    def test_N_feature_scaler_parity(self):
        x=raw(self.y,self.c,self.o);np.testing.assert_array_equal(m.features(self.y,self.c,self.o),transform(x,scale(x))[...,:29])
    def test_N_flattened_objective_AD(self):
        x=m.features(self.y,self.c,self.o);w=np.random.default_rng(3).normal(0,.02,(32,29));f,g=objective(w.ravel(),self.y,x,.1,'per_unit_exposure');ff=0;gg=[]
        for u in range(32):
            a,b=obj(w[u],x[:,:,u,:].reshape(-1,29),self.y[:,:,u].ravel());ff+=a;gg.append(b)
        self.assertLess(abs(f-ff),1e-10);np.testing.assert_allclose(g,np.asarray(gg).ravel(),atol=1e-12,rtol=0)
        cert=m.certificate(w,x,self.y);self.assertLess(cert['AD_scaled_error'],1e-5);self.assertLess(cert['AD_objective_error'],1e-10)
    def test_original_PG_near_bound(self):self.assertEqual(original_pg(np.array([-8+1e-8]),np.array([1.])),1.)
    def test_coverage_before_any_optimizer(self):
        with patch.object(m,'minimize',side_effect=AssertionError('FIT_MUST_NOT_RUN')) as fit:
            with self.assertRaises(ValueError):m.fit_all([self.s],lambda s:self.z,{},lambda *a:None,lambda a:None)
            fit.assert_not_called()
    def roster_fixture(self):
        sessions=[dict(self.s,mouse_id='m'+str(i),session_id='s'+str(i)) for i in range(13)]
        metadata={(s['session_id'],uid):{'probe_id':str(int(uid)%2),'nearest_other_channel_label_vertical_um':100.} for s in sessions for uid in self.s['unit_ids']['CA1']}
        return sessions,metadata
    def test_prospective_roster_durable_before_first_fit_failure(self):
        sessions,metadata=self.roster_fixture();rows=[]
        def fail(*args,**kwargs):
            self.assertEqual(rows[0][0],'private_prefit_roster');self.assertEqual(len(rows[0][1]['sessions']),13)
            self.assertEqual(rows[0][1]['registration'],'PROSPECTIVE_BEFORE_ANY_OPTIMIZER')
            raise RuntimeError('INJECTED_FIRST_FIT')
        with patch.object(m,'minimize',side_effect=fail) as fit:
            with self.assertRaisesRegex(RuntimeError,'INJECTED_FIRST_FIT'):m.fit_all(sessions,lambda s:self.z,metadata,lambda k,v:rows.append((k,v)),lambda a:None)
            self.assertEqual(fit.call_count,1)
        self.assertTrue(rows[-1][0].endswith('_exception'))
    def test_insufficient_coverage_preserves_roster_without_fit(self):
        sessions,metadata=self.roster_fixture();rows=[]
        for value in metadata.values():value['nearest_other_channel_label_vertical_um']=0.
        with patch.object(m,'minimize',side_effect=AssertionError('NO_FIT')) as fit:
            with self.assertRaisesRegex(ValueError,'MANDATORY_VIEW_MINIMUM_EIGHT'):m.fit_all(sessions,lambda s:self.z,metadata,lambda k,v:rows.append((k,v)),lambda a:None)
            fit.assert_not_called()
        self.assertEqual(rows[0][0],'private_prefit_roster');self.assertEqual(rows[0][1]['paired_counts']['boundary20'],0)
        self.assertIn('boundary20',rows[0][1]['sessions'][0]['unavailable_views'])
    def test_seed_initialization_and_failed_attempt_preservation(self):
        rows=[];checkpoints=[]
        def failed(fun,initial,**kwargs):
            np.testing.assert_array_equal(initial,np.random.default_rng(11).normal(0,.05,32*29));self.assertEqual(kwargs['options'],m.OPTIONS)
            raise RuntimeError('INJECTED_SOLVER_FAILURE')
        with patch.object(m,'minimize',side_effect=failed) as fit:
            with self.assertRaisesRegex(RuntimeError,'INJECTED_SOLVER_FAILURE'):m.fit_n(self.y,self.c,self.o,'case',lambda k,v:rows.append((k,v)),{},float('inf'),lambda a:checkpoints.append(a))
            self.assertEqual(fit.call_count,1)
        self.assertEqual(len(checkpoints),1);self.assertTrue(rows[-1][0].endswith('_exception'))
    def test_subset_scaler_and_changed_pool(self):
        full=raw(self.y,self.c,self.o);part=raw(self.y[:,:,:16],self.c,self.o);a=scale(full);b=scale(part)
        for aa,bb in zip(a,b):np.testing.assert_array_equal(aa[:16,:34],bb[:,:34])
        self.assertFalse(np.array_equal(full[:,:,:16,34:],part[:,:,:,34:]))
    def test_noninteger_context_and_counts(self):
        z=dict(self.z);z['conditions_C']=self.c.astype(float)
        with self.assertRaises(ValueError):m.validate_arrays(z,self.s)
        z=dict(self.z);z['CA1_C']=self.y.astype(float)+.1
        with self.assertRaises(ValueError):m.validate_arrays(z,self.s)
if __name__=='__main__':unittest.main()
