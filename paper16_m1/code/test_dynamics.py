import unittest,math,json
import numpy as np
from scipy.optimize import minimize
from scipy.special import gammaln,logsumexp
from .dynamics import *
from .spec import glm,forward,enumerate_hmm,iid_mixture,projected_gradient
class DynamicsTests(unittest.TestCase):
 def test_full_primary_capacity_independent_gradient(self):
  rng=np.random.Generator(np.random.PCG64(16062));X=rng.uniform(-.2,.2,(2,6,8,30));X[:,:,:,:12]=0
  for j in range(2):
   for k in range(6):X[j,k,:,6*j+k]=1
  y=rng.poisson(.3,(2,6,8)).astype(float);gates=np.array([[1,-1,0],[1,1,1.]])
  for mode in ['D','S']:
   b=initial(y,.02,30,11,mode);value,g=objective(b,X,y,.02,.1,mode,gates);other,ad=independent_AD(b,X,y,.02,.1,mode,gates)
   self.assertEqual(len(g),251);self.assertAlmostEqual(value,other,places=11);np.testing.assert_allclose(g,ad,atol=1e-8,rtol=1e-8)
  self.assertEqual(len(constraints(8,42,24)[0]),347);self.assertEqual(8*46,368)
 def fixture(self):
  rng=np.random.Generator(np.random.PCG64(16061));X=rng.uniform(-.5,.5,(3,4,2,3));X[:,:,:,0]=1
  y=np.array([[[0,1],[1,0],[2,1],[0,0]],[[1,1],[0,2],[1,0],[1,1]],[[0,0],[1,1],[0,1],[2,0]]],dtype=float)
  gates=np.array([[1,-1,0],[1,1,.5],[1,-1,1.]])
  return X,y,gates
 def test_D_S_independent_AD_fixed_FD_initial_mid_endpoint(self):
  X,y,gates=self.fixture();u,f=X.shape[-2:]
  for mode,seed in [(m,s) for m in ['D','S'] for s in [11,23,37]]:
   theta=initial(y,.02,f,seed,mode,1);saved=[];lo,hi=constraints(u,f,1)
   fit=minimize(lambda b:objective(b,X,y,.02,.1,mode,gates,1),theta,jac=True,method='L-BFGS-B',bounds=list(zip(lo,hi)),callback=lambda x:saved.append(x.copy()),options={'maxiter':1500,'maxfun':6000,'maxls':40,'maxcor':10,'ftol':1e-12,'gtol':2e-6})
   self.assertLessEqual(np.max(np.abs(projected_gradient(fit.x,fit.jac,lo,hi))),1e-5)
   maxad=maxfd=0.
   for b in [theta,saved[len(saved)//2] if saved else fit.x,fit.x]:
    value,grad=objective(b,X,y,.02,.1,mode,gates,1);dv,dg=independent_AD(b,X,y,.02,.1,mode,gates,1)
    self.assertAlmostEqual(value,dv,places=11);np.testing.assert_allclose(grad,dg,atol=1e-8,rtol=1e-8)
    maxad=max(maxad,float(np.max(np.abs(grad-dg)/np.maximum(1,np.maximum(np.abs(grad),np.abs(dg))))))
    for h in [1e-3,1e-4,1e-5,1e-6]:
     fd=np.array([(objective(b+np.eye(len(b))[i]*h,X,y,.02,.1,mode,gates,1)[0]-objective(b-np.eye(len(b))[i]*h,X,y,.02,.1,mode,gates,1)[0])/(2*h) for i in range(len(b))])
     self.assertLessEqual(np.max(np.abs(fd-grad)/np.maximum(1,np.maximum(np.abs(fd),np.abs(grad)))),2e-5)
     if h==1e-5:maxfd=max(maxfd,float(np.max(np.abs(fd-grad)/np.maximum(1,np.maximum(np.abs(fd),np.abs(grad))))))
   print(json.dumps({'scope':'SYNTHETIC_FIXTURE_ONLY','model':mode,'seed':seed,'objective':float(fit.fun),'PG':float(np.abs(projected_gradient(fit.x,fit.jac,lo,hi)).max()),'iterations':fit.nit,'calls':fit.nfev,'AD_scaled_max':maxad,'frozen_FD_scaled_max':maxfd}))
 def test_nested_B4_at_zero_latent_offsets_and_logits(self):
  X,y,gates=self.fixture();beta=np.array([[1.,.1,.2],[1.2,-.1,.3]]);theta=np.r_[beta.ravel(),np.zeros(5)]
  baseline=sum(glm(beta[i],X[:,:,i].reshape(-1,3),y[:,:,i].ravel(),np.full(12,.02),.1,1)[0] for i in range(2))/2
  for mode in ['D','S']:self.assertAlmostEqual(objective(theta,X,y,.02,.1,mode,gates,1)[0],baseline,places=12)
 def test_D_forward_enumeration_S_presentation_static_and_IID(self):
  y=np.array([[0,1],[2,0],[1,1]]);mu=np.array([[[.2,.3],[.6,.7]]]*3);A=np.array([[.8,.2],[.3,.7]]);pi=np.array([.4,.6])
  self.assertAlmostEqual(forward(y,mu,A,pi),enumerate_hmm(y,mu,A,pi),places=12)
  emission=(y[:,None,:]*np.log(mu)-mu-gammaln(y[:,None,:]+1)).sum(axis=-1)
  with np.errstate(divide='ignore'):value=forward(y,mu,np.eye(2),pi)
  self.assertAlmostEqual(value,logsumexp(np.log(pi)+emission.sum(axis=0)),places=12)
  self.assertAlmostEqual(forward(y,mu,np.tile(pi,(2,1)),pi),iid_mixture(y,mu,pi),places=12)
 def test_causal_prediction_future_target_perturbation_and_reset(self):
  X,y,gates=self.fixture()
  for mode in ['D','S']:
   b=initial(y,.02,3,23,mode,1)
   _,_,a=objective(b,X,y,.02,.1,mode,gates,1,True)
   changed=y.copy();changed[:,2:]+=5
   _,_,c=objective(b,X,changed,.02,.1,mode,gates,1,True)
   np.testing.assert_allclose(a[:,:2],c[:,:2],atol=1e-12)
   changed=y.copy();changed[0]+=3
   _,_,c=objective(b,X,changed,.02,.1,mode,gates,1,True);np.testing.assert_allclose(a[1:],c[1:],atol=1e-12)
   value,grad,pred=objective(b,X,y,.02,.1,mode,gates,1,True)
   beta,delta,gamma=unpack(b,2,3);penalty=.025*np.sum(beta[:,1:]**2)+.025*np.sum(delta**2)+.005*np.sum(gamma**2)
   self.assertAlmostEqual(value,-pred.sum()/y.size+penalty,places=12)
 def test_continuous_history_strict_future_reset_and_parameter_counts(self):
  edges=grid(10.);t=edges[5];a=[np.array([edges[0],edges[2],np.nextafter(t,0)]),np.array([edges[1]])]
  x=continuous_features(a,10,5);b=[np.r_[a[0],t,t+.01],np.r_[a[1],t+.02]]
  np.testing.assert_array_equal(x,continuous_features(b,10,5))
  np.testing.assert_array_equal(x,continuous_features([np.r_[0,a[0]],np.r_[1,a[1]]],10,5))
  np.testing.assert_allclose(x,continuous_features(a,10,10,.01),atol=1e-12)
  self.assertTrue(np.all((x>=0)&(x<=1)));self.assertEqual(x.shape,(2,4))
  self.assertEqual(len(constraints(8,30)[0]),251);self.assertEqual(8*34,272)
  for mode in ['D','S']:np.testing.assert_array_equal(initial(np.ones((2,6,8)),.02,30,37,mode),initial(np.ones((2,6,8)),.02,30,37,mode))
if __name__=='__main__':unittest.main()
