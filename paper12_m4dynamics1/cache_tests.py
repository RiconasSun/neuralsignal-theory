import importlib.util
import sys
import unittest
from pathlib import Path
import numpy as np

spec=importlib.util.spec_from_file_location('oracle_original',Path(__file__).with_name('oracle.py'))
original=importlib.util.module_from_spec(spec);sys.modules['oracle_original']=original;spec.loader.exec_module(original)
import oracle_cached as cached

class Cache(unittest.TestCase):
    def test_exact_factorials_and_unbounded_original_fallback(self):
        for y in (np.arange(10001,dtype=float),np.array([1000001.,2000000.])):
            eta=np.full_like(y,-.3)
            np.testing.assert_array_equal(cached.pmf(y,eta),original.pmf(y,eta))
    def test_likelihoods_and_independent_bytecode_identity(self):
        for name in ('state_parts','scalar_ll','scalar_objective','check_gradient'):
            self.assertIs(getattr(cached,name).__code__,getattr(original,name).__code__)
        count=0
        for family,size,ridge,seed,model,theta in original.synthetic_cases():
            x=model.x if family=='Continuous' else np.empty(model.y.shape[:2]+(0,))
            self.assertEqual(cached.scalar_ll(theta,family,model.y,x,model.offset,size),original.scalar_ll(theta,family,model.y,x,model.offset,size));count+=1
        self.assertEqual(count,108)

if __name__=='__main__':unittest.main(verbosity=2)
