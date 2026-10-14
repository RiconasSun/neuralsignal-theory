import unittest
import numpy as np
from glm import raw,scale,transform,MODELS
from nulls import eta,temporal,permute_labels,rng
class NullTests(unittest.TestCase):
    def test_exact_predictor_parity(self):
        r=np.random.default_rng(1);y=r.poisson(.4,(8,20,3));c=np.arange(8);o=np.arange(8);x=raw(y,c,o);ms=scale(x);w=r.normal(0,.02,(6,3,39))
        for i,indices in enumerate(MODELS.values()):w[i,:,list(set(range(39))-set(indices))]=0
        direct=np.einsum('ntuf,muf->mntu',transform(x,ms),w)
        np.testing.assert_allclose(direct,eta(y,c,o,w,ms),atol=1e-12,rtol=0)
    def test_count_preservation(self):
        y=np.ones((8,20,3),int);v=temporal(y,np.zeros_like(y,dtype=float),rng('s','CA1','T',0));np.testing.assert_array_equal(v.sum(axis=1),y.sum(axis=1))
    def test_fixed_assignments_order(self):
        c=np.array([0,0,1,1]);o=np.array([1,2,3,4]);cc,oo,b=permute_labels(c,o,'O',rng('s','DG','O',1));np.testing.assert_array_equal(cc,c)
        for k in (0,1):self.assertEqual(sorted(oo[c==k]),sorted(o[c==k]))
    def test_condition_block(self):
        c=np.array([0,1,2,3]);o=np.array([1,2,101,102]);cc,oo,b=permute_labels(c,o,'S',rng('s','DG','S',1));np.testing.assert_array_equal(oo,o)
        self.assertEqual(sorted(cc[:2]),sorted(c[:2]));self.assertEqual(sorted(cc[2:]),sorted(c[2:]))
    def test_bins_and_repeatability(self):
        c=np.arange(8);o=np.arange(8);a=permute_labels(c,o,'B',rng('s','CA1','B',0))[2];b=permute_labels(c,o,'B',rng('s','CA1','B',0))[2]
        np.testing.assert_array_equal(a,b)
        for row in a:self.assertEqual(sorted(row),list(range(20)))
if __name__=='__main__':unittest.main()
