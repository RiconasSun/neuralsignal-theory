"""Synthetic specification oracles only;no real neural source readers or fit pipeline."""
import itertools,math,hashlib
import numpy as np
from scipy.special import gammaln,logsumexp

MODEL_SLOTS={'B0':1,'B1':24,'B2':27,'B3':27,'B4':30}

def scored_log_rate(counts,exposures):
 counts=np.asarray(counts,dtype=float);exposures=np.asarray(exposures,dtype=float)
 if counts.shape!=exposures.shape or counts.size==0 or not np.isfinite(counts).all() or not np.isfinite(exposures).all() or np.any(counts<0) or np.any(exposures<=0):raise ValueError('Valid scored training rows required')
 total=counts.sum()
 return -10. if total==0 else float(np.clip(math.log(total/exposures.sum()),-10,10))

def complete_presentation(onset,stop,unit_support,invalid=()):
 end=grid(onset)[-1]
 if not math.isfinite(onset) or not math.isfinite(stop) or stop<end or not unit_support:return False
 if any(a<end and onset<b for a,b in invalid):return False
 for intervals in unit_support:
  cursor=onset
  for a,b in sorted(intervals):
   if not(math.isfinite(a) and math.isfinite(b)) or b<a:return False
   if a<=cursor:cursor=max(cursor,b)
   if cursor>=end:break
  if cursor<end:return False
 return True

def cuts(n):return {'A':(0,3*n//5),'B':(3*n//5,4*n//5),'E':(4*n//5,n),'C':(0,3*n//5),'D':(3*n//5,n)}
def event_available(event,t):return math.isfinite(event) and event<t

def grid(onset,width=.02):return onset+np.arange(round(.22/width)+1,dtype=float)*width

def past_rotation(starts,ends,rotation,t,invalid=()):
 if not(len(starts)==len(ends)==len(rotation)):raise ValueError('Same-row parent mismatch')
 choices=[i for i,(a,b,x) in enumerate(zip(starts,ends,rotation)) if all(math.isfinite(v) for v in [a,b,x]) and 0<b-a<=.1 and b<t and 0<t-b<=.1 and not any(l<b and a<r for l,r in invalid)]
 if not choices:return 0.,1.
 i=max(choices,key=lambda i:ends[i]);return math.tanh((rotation[i]/(ends[i]-starts[i]))/10),0.

def nuisance(color,k,previous_color,previous_gap,prior_same_count,ordinal,t,first_onset,r,missing,extra=()):
 if color not in [-1,1] or not 5<=k<11:raise ValueError('Primary condition/timebin invalid')
 out=np.zeros(24);out[(0 if color==-1 else 6)+k-5]=1
 prev_missing=previous_color is None;tau=(t-first_onset)/400
 out[12:]=[0 if prev_missing else previous_color,float(prev_missing),0 if prev_missing else previous_gap/(previous_gap+2),math.log1p(prior_same_count)/math.log(181),ordinal/179,tau,tau*tau,tau**3,r,r*r,color*r,missing]
 if not np.all(np.isfinite(out)) or np.max(np.abs(out))>1+1e-12:raise ValueError('Raw nuisance out of frozen domain')
 return np.r_[out,extra]

def histories(spikes,onset,k,width=.02):
 near=[round(x/width) for x in [0,.02,.06,.1]]
 if k<near[-1]:raise ValueError('No valid within-flash warmup')
 edges=grid(onset,width);features=[]
 for train in spikes:
  train=np.asarray(train)
  if not np.all(np.isfinite(train)) or np.any(np.diff(train)<0):raise ValueError('Source timestamp integrity')
  vals=[]
  for a,b in zip(near[:-1],near[1:]):
   count=np.searchsorted(train,edges[k-a],side='left')-np.searchsorted(train,edges[k-b],side='left')
   vals.append(count/((b-a)*width))
  features.append(vals)
 rate=np.asarray(features);other=(rate.sum(axis=0)[None,:]-rate)/(len(rate)-1)
 f=lambda x:np.log1p(x)/(1+np.log1p(x))
 return np.c_[f(rate),f(other)]

def scaler(X,psth=12):
 mean=X.mean(axis=0);scale=np.maximum(.25,X.std(axis=0));active=X.var(axis=0)>1e-12
 mean[:psth]=0;scale[:psth]=1;active[:psth]=True
 return mean,scale,active

def glm(beta,X,y,exposure,lam,psth=12):
 beta=np.asarray(beta);eta=X@beta;mu=np.asarray(exposure)*np.exp(eta);penalty=np.arange(len(beta))>=psth
 value=np.mean(mu-y*(np.log(exposure)+eta)+gammaln(y+1))+lam/2*np.sum(beta[penalty]**2)
 grad=X.T@(mu-y)/len(y)+lam*beta*penalty
 return float(value),grad

class Dual:
 def __init__(self,v,d):self.v=float(v);self.d=np.asarray(d,dtype=float)
 def other(self,x):return x if isinstance(x,Dual) else Dual(x,np.zeros_like(self.d))
 def __add__(self,x):x=self.other(x);return Dual(self.v+x.v,self.d+x.d)
 __radd__=__add__
 def __neg__(self):return Dual(-self.v,-self.d)
 def __sub__(self,x):return self+-self.other(x)
 def __rsub__(self,x):return self.other(x)+-self
 def __mul__(self,x):x=self.other(x);return Dual(self.v*x.v,self.d*x.v+x.d*self.v)
 __rmul__=__mul__
 def __truediv__(self,x):
  x=self.other(x);return Dual(self.v/x.v,(self.d*x.v-self.v*x.d)/(x.v*x.v))
 def __rtruediv__(self,x):return self.other(x)/self
 def log(self):return Dual(math.log(self.v),self.d/self.v)
 def exp(self):v=math.exp(self.v);return Dual(v,v*self.d)

def independent_AD(beta,X,y,exposure,lam,psth=12):
 d=len(beta);basis=np.eye(d);b=[Dual(v,basis[i]) for i,v in enumerate(beta)];total=Dual(0,np.zeros(d))
 for row,target,dt in zip(X,y,exposure):
  eta=sum(float(x)*v for x,v in zip(row,b));total+=float(dt)*eta.exp()-float(target)*(eta+math.log(float(dt)))+math.lgamma(float(target)+1)
 total=total/len(y)
 for j in range(psth,d):total+=lam/2*b[j]*b[j]
 return total.v,total.d

def projected_gradient(beta,g,lo,hi):
 return np.where(((beta<=lo+1e-12)&(g>0))|((beta>=hi-1e-12)&(g<0)),0,g)

def likelihood(counts,means):return np.sum(counts*np.log(means)-means-gammaln(counts+1),axis=-1)
def forward(counts,means,transition,initial):
 emit=likelihood(counts[:,None,:],means);alpha=np.log(initial)+emit[0]
 for i in range(1,len(counts)):alpha=logsumexp(alpha[:,None]+np.log(transition),axis=0)+emit[i]
 return float(logsumexp(alpha))
def enumerate_hmm(counts,means,transition,initial):
 emit=likelihood(counts[:,None,:],means);terms=[]
 for z in itertools.product(range(len(initial)),repeat=len(counts)):
  terms.append(math.log(initial[z[0]])+sum(emit[t,z[t]] for t in range(len(z)))+sum(math.log(transition[z[t-1],z[t]]) for t in range(1,len(z))))
 return float(logsumexp(terms))
def iid_mixture(counts,means,weights):return float(np.sum(logsumexp(likelihood(counts[:,None,:],means)+np.log(weights),axis=1)))
def finite_history(counts,decays,resets):
 state=np.zeros(len(decays));output=[]
 for i,x in enumerate(counts):
  if resets[i]:state[:]=0
  output.append(state.copy());state=np.asarray(decays)*state+x
 return np.asarray(output)

def count_bins(spikes,edges,supported):
 value=np.diff(np.searchsorted(spikes,edges,side='left'))
 return [int(x) if ok else None for x,ok in zip(value,supported)]
def gain(a,b,mask):
 if a.shape!=b.shape or mask.shape!=a.shape or not np.any(mask):raise ValueError('Identical valid target masks required')
 if not(np.isfinite(a[mask]).all() and np.isfinite(b[mask]).all()):raise ValueError('Nonfinite score')
 return float(np.sum((a-b)[mask])/int(mask.sum()))
def holm(p):
 order=np.argsort(p);out=np.zeros(len(p));prev=0
 for j,i in enumerate(order):prev=max(prev,(len(p)-j)*p[i]);out[i]=min(1.,prev)
 return out

def jitter_within_bins(spikes,edges,rng):
 idx=np.searchsorted(edges,spikes,side='right')-1
 if np.any(idx<0) or np.any(idx>=len(edges)-1):raise ValueError('Outside source support')
 out=[]
 for i in idx:
  a,b=edges[i:i+2];x=a+rng.random()*(b-a);out.append(min(np.nextafter(b,a),max(np.nextafter(a,b),x)))
 return np.sort(out)
def derangement(indices,rng):
 indices=np.asarray(indices)
 if len(indices)<6:raise ValueError('Unavailable trial stratum')
 for _ in range(128):
  perm=rng.permutation(indices)
  if np.all(perm!=indices):return perm
 raise ValueError('Unavailable structural derangement,no scientific redraw')
