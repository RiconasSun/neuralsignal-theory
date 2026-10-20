"""Predetermined, data-free fixtures; no real inputs or alternate optimizer policy."""
import numpy as np
from .common import *

class Fixture:
    def __init__(self,row):
        self.row=row;self.x0=np.array(row['x0'],float);self.lo,self.hi=np.array(row['bounds'],float)
        if row['name']=='poisson':
            self.X=np.c_[np.ones(12),np.linspace(-1,1,12),np.tile([1.,-1.],6)]
            self.y=np.array(row['y'],float);self.exposure=np.full(12,row['dt'])
    def analytic(self,x):
        name=self.row['name']
        if name=='poisson':return spec.glm(x,self.X,self.y,self.exposure,self.row['lambda'],1)
        if name=='rounded_plateau':return 1e20+.1*x[0],np.array([.1])
        d=np.array(self.row['diagonal']);z=x-np.array(self.row['center'])
        return float(.5*np.dot(d,z*z)),d*z
    def AD(self,x):
        if self.row['name']=='poisson':return spec.independent_AD(x,self.X,self.y,self.exposure,self.row['lambda'],1)
        basis=np.eye(len(x));v=[spec.Dual(z,basis[i]) for i,z in enumerate(x)]
        if self.row['name']=='rounded_plateau':out=1e20+.1*v[0]
        else:out=sum(.5*d*(z-c)*(z-c) for d,z,c in zip(self.row['diagonal'],v,self.row['center']))
        return out.v,out.d

