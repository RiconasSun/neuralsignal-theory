import math
import unittest
import numpy as np
from glm import raw,scale,transform,obj,independent_ad,fit,pg,score,MODELS
class GLMTests(unittest.TestCase):
    def setUp(self):
        self.r=np.random.default_rng(120214);self.y=self.r.poisson(.4,(8,20,3));self.x=raw(self.y,np.arange(8),np.arange(8));self.ms=scale(self.x);self.z=transform(self.x,self.ms)
    def test_causal_future(self):
        y=self.y.copy();y[:,10:]+=5
        np.testing.assert_array_equal(raw(y,np.arange(8),np.arange(8))[:,:11, :,29:39],self.x[:,:11,:,29:39])
    def test_trial_reset(self):np.testing.assert_array_equal(self.x[:,0,:,29:39],0)
    def test_excludes_own(self):
        y=self.y.copy();y[:,:,0]+=1
        np.testing.assert_allclose(raw(y,np.arange(8),np.arange(8))[:,:,0,34:39],self.x[:,:,0,34:39],atol=1e-12,rtol=0)
    def test_nesting_objective(self):
        for name,indices in MODELS.items():
            t=self.r.normal(0,.1,len(indices));full=np.zeros(39);full[indices]=t
            f,g=obj(t,self.z[:,:,0,indices].reshape(-1,len(indices)),self.y[:,:,0].ravel());ff,gg=obj(full,self.z[:,:,0,:].reshape(-1,39),self.y[:,:,0].ravel())
            self.assertAlmostEqual(f,ff,places=12);np.testing.assert_allclose(g,gg[indices],atol=1e-12)
    def test_ad_full_coordinates(self):
        t=self.r.normal(0,.03,39);x=self.z[:,:,0,:].reshape(-1,39);y=self.y[:,:,0].ravel();f,g=obj(t,x,y);af,ag=independent_ad(t,x,y)
        self.assertLess(abs(f-af),1e-12);np.testing.assert_allclose(g,ag,atol=1e-12,rtol=0)
    def test_fixed_fd_steps(self):
        t=self.r.normal(0,.03,39);x=self.z[:,:,0,:].reshape(-1,39);y=self.y[:,:,0].ravel();f,g=obj(t,x,y)
        for h in (1e-5,1e-6):
            fd=[]
            for i in range(39):
                d=np.zeros(39);d[i]=h;fd.append((obj(t+d,x,y)[0]-obj(t-d,x,y)[0])/(2*h))
            self.assertLess(np.max(np.abs(g-fd)/np.maximum(1,np.abs(g))),1e-5)
    def test_scalar_poisson(self):
        for y in range(6):
            t=np.array([.1]);x=np.ones((1,1));f,g=obj(t,x,np.array([y]));expected=math.exp(.1)-y*.1+math.lgamma(y+1)
            self.assertLess(abs(f-expected),1e-12)
    def test_fit_box_and_oracle(self):
        for name,indices in MODELS.items():
            x=self.z[:,:,0,indices].reshape(-1,len(indices));w,r=fit(x,self.y[:,:,0].ravel());self.assertTrue(r['passed'],str(r))
    def test_active_pg(self):self.assertEqual(pg(np.array([-8.,8.]),np.array([1.,-1.])),0)
    def test_ridge_intercept_unpenalized(self):
        x=np.ones((1,2));y=np.array([1]);t=np.array([.2,.3]);f,g=obj(t,x,y);af,ag=independent_ad(t,x,y);self.assertAlmostEqual(g[1]-g[0],.03,places=12)
    def test_order_and_batch_score(self):
        w=np.zeros((3,39));w[:,0]=-.2;a=score(self.y,self.z,w);idx=np.arange(8)[::-1];b=score(self.y[idx],self.z[idx],w)
        self.assertLess(abs(a-b),1e-10);c=sum(score(self.y[i:i+1],self.z[i:i+1],w) for i in range(8))/8;self.assertLess(abs(a-c),1e-10)
    def test_scaler_A_only(self):
        old=tuple(z.copy() for z in self.ms);v=raw(self.y*2,np.arange(8),np.arange(8));transform(v,self.ms)
        for a,b in zip(old,self.ms):np.testing.assert_array_equal(a,b)
if __name__=='__main__':unittest.main()
