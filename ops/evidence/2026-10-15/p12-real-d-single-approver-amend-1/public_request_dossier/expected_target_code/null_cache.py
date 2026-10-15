"""Exact fixed-outcome covariate caching for S/B/O; temporal kernel unchanged."""
import numpy as np
from nulls import eta,get_gains
class Cache:
    def __init__(self,y,c,o,w,ms):
        self.y=y;self.c=c;self.o=o;self.base=eta(y,c,o,w,ms);self.beta=w/ms[1][None,:,:]
        self.conditions=np.concatenate((np.zeros((len(w),1,y.shape[-1])),self.beta[:,:,1:8].transpose(0,2,1)),axis=1)
        self.times=np.concatenate((np.zeros((len(w),1,y.shape[-1])),self.beta[:,:,8:27].transpose(0,2,1)),axis=1)
    def predict(self,c,o,bins,suite):
        if suite=='S':return self.base+(self.conditions[:,c,:]-self.conditions[:,self.c,:])[:,:,None,:]
        if suite=='O':
            a=o/599.;b=self.o/599.;d=self.beta[:,:,27][:,None,:]*(a-b)[None,:,None]+self.beta[:,:,28][:,None,:]*(a*a-b*b)[None,:,None]
            return self.base+d[:,:,None,:]
        if suite=='B':return self.base+self.times[:,bins,:]-self.times[:,np.arange(20),:][:,None,:,:]
        raise ValueError('SUITE')
