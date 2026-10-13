import itertools
import unittest
import numpy as np
from impossibility import complete,early_failure
from frozen_offset import apply
from baseline_features import design,training_scaler,transform
from competition import candidates


class M4ControlTests(unittest.TestCase):
    def test_exhaustive_convergence_predicate_and_monotonicity(self):
        slots=list(itertools.product(('CA1','DG'),(11,23,37)))
        for first in itertools.product((False,True),repeat=6):
            for second in itertools.product((False,True),repeat=6):
                rows=[]
                for s,flags in zip(('1','2'),(first,second)):
                    for (roi,seed),ok in zip(slots,flags):
                        rows.append(dict(session_id=s,region=roi,seed=seed,converged=ok,family='Discrete',kind=None,size=2,ridge=.1,validation_LL_nats_per_unit_bin=0,parameter_count=10))
                definition=dict(family='Discrete',size=2,ridge=.1)
                full=bool(candidates(rows,['1','2'],'Discrete'))
                self.assertEqual(complete(rows,['1','2'],definition),full)
                if not complete(rows[:6],['1'],definition):self.assertFalse(full)

    def test_prefix_requires_all216_attempts(self):
        rows=[]
        for f in ('Discrete','Continuous','Hybrid'):
            for size in ((1,2,4) if f=='Continuous' else (2,3,4)):
                for ridge in (.001,.01,.1,1.):
                    for roi,seed in itertools.product(('CA1','DG'),(11,23,37)):
                        rows.append(dict(session_id='1',region=roi,seed=seed,family=f,size=size,ridge=ridge,converged=f!='Continuous'))
        error,counts=early_failure(rows,['1']);self.assertIn('Continuous',error)
        self.assertEqual(counts,dict(Discrete=12,Continuous=0,Hybrid=12))
        with self.assertRaises(RuntimeError):early_failure(rows[:-1],['1'])

    def test_frozen_offset_mean_and_train_scaler(self):
        y=np.random.default_rng(11).poisson(.3,(8,20,2));v=y[:4];c=np.arange(8);o=c*70
        w=np.random.default_rng(23).normal(0,.05,(3,2,29));actual=apply(y,v,c,c[:4],o,o[:4],w)
        raw=np.concatenate((design(y,c,o,'event'),design(y,c,o,'drift')[...,1:]),axis=-1)
        x=transform(raw,training_scaler(raw))
        reference=np.mean([np.einsum('ntuf,uf->ntu',x,z) for z in w],axis=0)
        np.testing.assert_allclose(actual[0],reference,atol=1e-12,rtol=0)
        modified=apply(y,v+10,c,c[:4],o,o[:4],w)
        for a,b in zip(actual,modified):np.testing.assert_array_equal(a,b)
