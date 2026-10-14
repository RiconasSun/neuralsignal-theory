import unittest
import numpy as np
from glm import raw,scale,MODELS
from nulls import eta,permute_labels,rng,get_gains
from null_cache import Cache
class CacheTests(unittest.TestCase):
    def test_all_covariate_controls_match_direct(self):
        random=np.random.default_rng(2);y=random.poisson(.4,(8,20,3));c=np.arange(8);o=np.arange(8)*70;ms=scale(raw(y,c,o));w=random.normal(0,.03,(6,3,39));cache=Cache(y,c,o,w,ms)
        for suite in ('S','B','O'):
            for rep in range(3):
                cc,oo,bb=permute_labels(c,o,suite,rng('s','DG',suite,rep));direct=eta(y,cc,oo,w,ms,bb);fast=cache.predict(cc,oo,bb,suite)
                np.testing.assert_allclose(direct,fast,atol=1e-12,rtol=0);np.testing.assert_allclose(get_gains(y,direct),get_gains(y,fast),atol=1e-12,rtol=0)
    def test_cache_is_fixed_and_has_no_new_counts(self):
        y=np.ones((8,20,3),int);c=np.arange(8);o=np.arange(8);w=np.zeros((6,3,39));ms=scale(raw(y,c,o));cache=Cache(y,c,o,w,ms);old=cache.base.copy();cc,oo,bb=permute_labels(c,o,'B',rng('s','DG','B',1));cache.predict(cc,oo,bb,'B');np.testing.assert_array_equal(cache.base,old)
if __name__=='__main__':unittest.main()
