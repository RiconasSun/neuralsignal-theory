"""Synthetic serializer/guard fixtures only, never experimental cohort evidence."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import numpy as np
import model_math as m
import reuse_dynamics as reuse

class Reuse(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name);self.y=np.ones((2,6,2));self.x=np.zeros((2,6,3));self.offset=np.zeros_like(self.y)
        self.rows=[];states={}
        for roi in ('CA1','DG'):
            for f in ('Discrete','Continuous','Hybrid'):
                for k in ((1,2,4) if f=='Continuous' else (2,3,4)):
                    for ridge in (.001,.01,.1,1.):
                        for seed in (11,23,37):
                            model=m.make(f,self.y,self.x,self.offset,k);t=np.zeros(model.n_parameters);loss,g=m.objective(t,model,ridge)
                            states[f'{roi}_{f}_{k}_{ridge}_{seed}']=t
                            self.rows.append(dict(mouse_id='744912849',session_id='766640955',region=roi,family=f,size=k,ridge=ridge,seed=seed,
                                converged=True,optimizer_success=True,optimizer_message='SYNTHETIC_FIXTURE_NOT_A_FIT',iterations=0,objective_calls=0,
                                projected_gradient=m.projected_gradient(t,g),penalized_training_objective=loss,bound_hits=0,elapsed_seconds=0,validation_access=False,final_access=False))
        self.summary=dict(rows=self.rows,conditioning=[dict(region=roi,training_array_sha256=hashlib.sha256(self.y.tobytes()).hexdigest()) for roi in ('CA1','DG')],validation_access=False,final_access=False)
        np.savez(self.root/'reuse_states.npz',**states);self.write_summary()
        self.filepatch=patch.object(reuse,'__file__',str(self.root/'reuse_dynamics.py'));self.filepatch.start();reuse._bundle=None
        self.model=m.make('Discrete',self.y,self.x,self.offset,2)
    def digest(self,name):return hashlib.sha256((self.root/name).read_bytes()).hexdigest()
    def write_summary(self):
        (self.root/'reuse_summary.json').write_text(json.dumps(self.summary))
        (self.root/'reuse_gate.json').write_text(json.dumps(dict(gate='PASS',completed_fit_count=216,fitted_states_sha256=self.digest('reuse_states.npz'))))
        hashes={n:self.digest(n) for n in ('reuse_states.npz','reuse_summary.json','reuse_gate.json')}
        binding=dict(gate=hashes['reuse_gate.json'],summary=hashes['reuse_summary.json'],receipt='synthetic',proof='synthetic',oracles='synthetic')
        (self.root/'reuse_bundle.json').write_text(json.dumps(dict(sha256=hashes,completed_smoke_bindings=binding)))
    def tearDown(self):self.filepatch.stop();reuse._bundle=None;self.temp.cleanup()
    def call(self,validation=None):
        return reuse.fit_or_reuse(m,dict(session_id='766640955'),'CA1','Discrete',2,self.y,self.model,validation or self.model,.1,11)
    def test_valid_reuse_never_refits(self):
        with patch.object(m,'fit',side_effect=AssertionError('MUST_NOT_REFIT')):
            theta,metrics=self.call();self.assertTrue(metrics['reused_training_fit']);self.assertEqual(metrics['validation_LL_nats_per_unit_bin'],-1.)
    def test_scoring_failure_preserves_ordinary_candidate_semantics(self):
        with patch.object(self.model,'score',side_effect=FloatingPointError('SYNTHETIC_SCORE_FAILURE')):
            with self.assertRaises(FloatingPointError):self.call()
    def test_empty_hash_manifest_stops(self):
        (self.root/'reuse_bundle.json').write_text(json.dumps(dict(sha256={})))
        with self.assertRaises(reuse.ReuseIntegrityError):self.call()
    def test_true_validation_access_stops(self):
        self.summary['validation_access']=True;self.write_summary()
        with self.assertRaises(reuse.ReuseIntegrityError):self.call()
    def test_corrupt_state_artifact_stops(self):
        with (self.root/'reuse_states.npz').open('ab') as f:f.write(b'SYNTHETIC_CORRUPTION')
        with self.assertRaises(reuse.ReuseIntegrityError):self.call()
    def test_training_identity_mismatch_stops(self):
        with self.assertRaises(reuse.ReuseIntegrityError):
            reuse.fit_or_reuse(m,dict(session_id='766640955'),'CA1','Discrete',2,self.y+1,self.model,self.model,.1,11)

if __name__=='__main__':unittest.main(verbosity=2)
