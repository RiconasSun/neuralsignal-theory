import itertools
import unittest
import numpy as np
from scipy.special import logsumexp,gammaln
import model_math as m


class NumericalTests(unittest.TestCase):
    def test_poisson_analytic(self):
        y=np.array([0.,1.,2.,7.]);eta=np.log(.37)
        expected=y*eta-.37-gammaln(y+1)
        self.assertLess(np.max(np.abs(m.poisson_logpmf(y,eta)-expected)),1e-12)

    def test_exhaustive_states(self):
        y=np.array([[[0.,1.],[2.,0.],[1.,1.]]]);offset=np.full_like(y,np.log(.3))
        for k in (2,3,4):
            for lags in (0,5):
                model=m.StatePoisson(y,offset,k,lags);theta=model.initial(11)
                pi,transition,_,_=model.unpack(theta)
                emissions=m.poisson_logpmf(y[:,:,None,:],model.log_means(theta)).sum(axis=-1)[0]
                oracle=[]
                for states in itertools.product(range(k),repeat=3):
                    oracle.append(pi[states[0]]+sum(emissions[t,s] for t,s in enumerate(states))+
                                  sum(transition[states[t-1],states[t]] for t in (1,2)))
                self.assertLess(abs(logsumexp(oracle)-model.score(theta)),1e-10)

    def fixtures(self):
        y=np.random.default_rng(20261013).poisson(.3,(3,20,2)).astype(float)
        x=np.random.default_rng(20261014).normal(0,.1,(3,20,28));offset=np.full_like(y,np.log(.3))
        for family,sizes in (('Discrete',(2,3,4)),('Continuous',(1,2,4)),('Hybrid',(2,3,4)):
            for size in sizes:yield family,size,y,x,offset

    def test_all_gradients_and_ridge_exposure(self):
        for family,size,y,x,offset in self.fixtures():
            model=m.make(family,y,x,offset,size);theta=model.initial(23)
            ll,gradient=model._likelihood_gradient(theta);loss,penalized=m.objective(theta,model,.1)
            self.assertAlmostEqual(loss,-ll/(len(y)*20)+.05*np.dot(theta,theta),12)
            numeric=np.empty_like(theta)
            for index in range(len(theta)):
                hi=theta.copy();lo=theta.copy();hi[index]+=1e-6;lo[index]-=1e-6
                numeric[index]=(m.objective(hi,model,.1)[0]-m.objective(lo,model,.1)[0])/2e-6
            self.assertLess(np.max(np.abs(numeric-penalized)/np.maximum(1.,np.abs(penalized))),1e-5)

    def test_causal_future_and_batch_reset(self):
        for family,size,y,x,offset in self.fixtures():
            model=m.make(family,y,x,offset,size);theta=model.initial(37)
            future=y.copy();future[:,12:]+=4
            changed=m.make(family,future,x,offset,size)
            self.assertLess(np.max(np.abs(model.score_bins(theta)[:,:12]-changed.score_bins(theta)[:,:12])),1e-12)
            pieces=sum(m.make(family,y[i:i+1],x[i:i+1],offset[i:i+1],size).score(theta) for i in range(3))
            reverse=m.make(family,y[::-1],x[::-1],offset[::-1],size).score(theta)
            self.assertLess(abs(pieces-model.score(theta)),1e-10)
            self.assertLess(abs(reverse-model.score(theta)),1e-10)

    def test_archived_batch_sequential_parity(self):
        for family,size,y,x,offset in self.fixtures():
            if family=='Continuous':continue
            model=m.make(family,y,x,offset,size);theta=model.initial(11)
            sequential=m.SequentialState(y,offset,size,5 if family=='Hybrid' else 0)
            self.assertLess(np.max(np.abs(model.score_bins(theta)-sequential.score_bins(theta))),1e-10)
            ll,gradient=model._likelihood_gradient(theta);other_ll,other_gradient=sequential._likelihood_gradient(theta)
            self.assertLess(abs(ll-other_ll),1e-10)
            self.assertLess(np.max(np.abs(gradient-other_gradient)),1e-10)


if __name__=='__main__':unittest.main()
