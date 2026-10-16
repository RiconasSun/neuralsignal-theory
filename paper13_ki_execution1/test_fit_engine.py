"""Synthetic fit/attempt-preservation and gate oracles."""
import json
from pathlib import Path
import unittest
import uuid
from unittest.mock import patch
import numpy as np
from .source import P
from . import models as m
from .fit_engine import fit,ScientificStop

class FitTests(unittest.TestCase):
    def folder(self):
        p=P/'work'/('synthetic_fit_'+uuid.uuid4().hex);p.mkdir(parents=True);return p
    def fixture(self):
        rng=np.random.default_rng(130073);y=rng.poisson(.4,(4,9,2));q=rng.normal(0,.1,(4,9,11))
        x,_=m.raw_features(y,q,'B1');x=m.scale(x,m.fit_scale(x));return y,x
    def test_complete_GLMattempt_audits_three_frozen_states(self):
        y,x=self.fixture();path=self.folder()/'glm.json'
        r=fit(path,'GLM',{'y':y,'x':x},.1,m.glm_initial(x,y,11),source_hash='synthetic1')
        self.assertEqual(r['status'],'PASS');self.assertLessEqual(r['PG'],.001)
        self.assertEqual(set(r['derivatives']),{'initial','intermediate_first_callback','endpoint'})
        self.assertTrue(all(z['pass'] for z in r['derivatives'].values()))
        self.assertGreater(r['calls'],r['optimizer_calls'])
        self.assertEqual(fit(path,'GLM',{'y':y,'x':x},.1,m.glm_initial(x,y,11),source_hash='synthetic1'),r)
    def test_complete_HMMattempt_independent_checks(self):
        y,_=self.fixture();path=self.folder()/'hmm.json';o=np.zeros_like(y,dtype=float)-.7
        r=fit(path,'HMM',{'y':y},.1,np.array([.03,-.02,-.03,.02]),p=.9,offset=o,source_hash='synthetic2')
        self.assertEqual(r['status'],'PASS');self.assertLessEqual(r['PG'],.001)
        self.assertTrue(all(z['fixed_FD_error']['max_relative']<=1e-5 for z in r['derivatives'].values()))
        before=path.read_bytes()
        with self.assertRaisesRegex(ScientificStop,'request mismatch'):fit(path,'HMM',{'y':y},.1,np.array([.03,-.02,-.03,.02]),p=.98,offset=o,source_hash='synthetic2')
        self.assertEqual(path.read_bytes(),before)
    def test_preserved_required_failure_cannot_retry(self):
        y,x=self.fixture();path=self.folder()/'failed.json'
        with patch('paper13_ki_execution1.fit_engine.derivatives',return_value={'pass':False}):
            with self.assertRaises(ScientificStop):fit(path,'GLM',{'y':y,'x':x},.1,m.glm_initial(x,y,11),source_hash='bad')
        self.assertEqual(json.loads(path.read_text())['status'],'FAILED_REQUIRED_GATE')
        before=path.read_bytes()
        with self.assertRaises(ScientificStop):fit(path,'GLM',{},.1,np.array([]),source_hash='bad')
        self.assertEqual(path.read_bytes(),before)
    def test_source_mismatch_never_silently_refits(self):
        path=self.folder()/'saved.json';path.write_text(json.dumps({'status':'PASS','source_hash':'old'}))
        with self.assertRaises(ScientificStop):fit(path,'GLM',{},.1,np.array([]),source_hash='new')
    def test_changed_full_request_cannot_reuse_GLM_PASS(self):
        y,x=self.fixture();path=self.folder()/'bound.json';w=m.glm_initial(x,y,11)
        fit(path,'GLM',{'y':y,'x':x},.1,w,source_hash='same')
        before=path.read_bytes();y2=y.copy();y2[0,6,0]+=1;w2=w.copy();w2[0]+=.01
        requests=[('GLM',{'y':y2,'x':x},.1,w,{}),('GLM',{'y':y,'x':x+1},.1,w,{}),('GLM',{'y':y,'x':x},1,w,{}),
                  ('GLM',{'y':y,'x':x},.1,w2,{}),('GLM',{'y':y,'x':x},.1,w,{'identity':{'seed':23}}),
                  ('GLM',{'y':y,'x':x},.1,w,{'offset':np.zeros_like(y)}),('HMM',{'y':y},.1,w,{'p':.9,'offset':np.zeros_like(y)}),
                  ('C',{'y':y,'x':x},.1,w,{})]
        for kind,data,ridge,initial,kw in requests:
            with self.assertRaisesRegex(ScientificStop,'request mismatch'):fit(path,kind,data,ridge,initial,source_hash='same',**kw)
            self.assertEqual(path.read_bytes(),before)
    def test_incomplete_cached_request_is_not_a_lookup_API(self):
        path=self.folder()/'old.json';path.write_text(json.dumps({'status':'PASS','source_hash':'same'}));before=path.read_bytes()
        with self.assertRaises(ScientificStop):fit(path,'GLM',{},.1,np.array([]),source_hash='same')
        self.assertEqual(path.read_bytes(),before)
        with self.assertRaisesRegex(ScientificStop,'identity incomplete'):fit(path,'GLM',{},.1,np.array([]),source_hash='same',identity={'real_data':True})

if __name__=='__main__':unittest.main(verbosity=2)
