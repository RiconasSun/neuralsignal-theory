"""Synthetic array-only QC/selection/statistical specification oracles; no source IO."""
import itertools,math
import numpy as np
from .spec import holm

def physiological_summary(spikes,windows,role):
 if role not in ['A','C']:raise ValueError('QC role denied')
 spikes=np.asarray(spikes,dtype=float)
 if not np.isfinite(spikes).all() or np.any(np.diff(spikes)<0):raise ValueError('Source timestamp integrity')
 count=occupied=pairs=short=0;exposure=0.
 for a,b in windows:
  if not(math.isfinite(a) and math.isfinite(b)) or b<=a:raise ValueError('Support integrity')
  x=spikes[np.searchsorted(spikes,a,'left'):np.searchsorted(spikes,b,'left')];count+=len(x);occupied+=bool(len(x));exposure+=b-a
  differences=np.diff(x);pairs+=len(differences);short+=int((differences<.0015).sum())
 if not exposure:raise ValueError('No observed exposure')
 return {'spikes':count,'occupied':occupied,'exposure':exposure,'rate':count/exposure,'ISI_pairs':pairs,'short_ISI_fraction':short/pairs if pairs else None,'pass':bool(count>=30 and occupied>=20 and .5<=count/exposure<=150 and pairs>=20 and short/pairs<=.02)}

def select_lambda(records):
 grid=[.01,.1,1.];support=None;scores={};records=list(records);protocols={};seen=set()
 for row in records:
  if not isinstance(row,dict) or not {'lambda','mouse_id','protocol','logscore'}<=row.keys():raise ValueError('B record schema')
  lam,mouse,protocol,score=(row[x] for x in ['lambda','mouse_id','protocol','logscore'])
  if isinstance(lam,bool) or not isinstance(lam,(int,float,np.integer,np.floating)) or lam not in grid:raise ValueError('Unregistered lambda')
  if isinstance(mouse,bool) or not isinstance(mouse,(str,int,np.integer)) or not str(mouse).isdigit() or str(int(mouse))!=str(mouse):raise ValueError('Invalid mouse identity')
  mouse=str(mouse)
  if protocol not in ['BO','FC'] or isinstance(score,bool) or not isinstance(score,(int,float,np.integer,np.floating)) or not math.isfinite(score):raise ValueError('B protocol/score integrity')
  if (lam,mouse) in seen or (mouse in protocols and protocols[mouse]!=protocol):raise ValueError('Duplicate mouse or protocol switch')
  seen.add((lam,mouse));protocols[mouse]=protocol
 for lam in grid:
  rows=[x for x in records if x['lambda']==lam];ids=[str(x['mouse_id']) for x in rows]
  if len(ids)!=len(set(ids)) or not rows or not all(math.isfinite(x['logscore']) for x in rows):raise ValueError('B score integrity')
  if support is None:support=set(ids)
  if set(ids)!=support:raise ValueError('Unequal candidate support across grid')
  means=[]
  for protocol in ['BO','FC']:
   group=[x['logscore'] for x in rows if x['protocol']==protocol]
   if len(group)<(3 if protocol=='BO' else 10):raise ValueError('Protocol coverage failure')
   means.append(math.fsum(group)/len(group))
  if len(rows)<14:raise ValueError('Development floor')
  scores[lam]=sum(means)/2
 best=max(scores.values());return max(lam for lam in grid if scores[lam]>=best-1e-12)

def select_seed(records):
 if sorted(x['seed'] for x in records)!=[11,23,37] or not all(x['numerical_pass'] and math.isfinite(x['objective']) for x in records):raise ValueError('Every frozen seed must pass')
 best=min(x['objective'] for x in records);return min(x['seed'] for x in records if x['objective']<=best+1e-12)

def statistics(effects):
 effects=np.asarray(effects,dtype=float)
 if effects.ndim!=2 or effects.shape[1]!=6 or effects.shape[0]<2 or not np.isfinite(effects).all():raise ValueError('Six paired mouse effects required')
 n,c=effects.shape;mean=np.array([math.fsum(effects[:,k])/n for k in range(c)]);extreme=np.zeros(c,dtype=np.int64)
 exact=n<=16
 signs=itertools.product([-1,1],repeat=n) if exact else np.random.Generator(np.random.PCG64(16041)).integers(0,2,size=(99999,n))*2-1
 count=0
 for row in signs:
  value=np.array([math.fsum(float(row[i])*float(effects[i,k]) for i in range(n))/n for k in range(c)])
  extreme+=np.abs(value)>=np.abs(mean);count+=1
 p=extreme/count if exact else (1+extreme)/(1+count)
 draw=np.random.Generator(np.random.PCG64(16042)).integers(0,n,size=(10000,n));boot=effects[draw].mean(axis=1);ci=np.quantile(boot,[.025,.975],axis=0,method='linear')
 loo=np.array([[math.fsum(effects[i,k] for i in range(n) if i!=drop)/(n-1) for k in range(c)] for drop in range(n)])
 return {'mean':mean,'CI':ci,'p':p,'secondary_Holm5':holm(p[1:]),'LOMO':loo,'exact':exact,'sign_patterns':count}

def classify(result,n,required_gates,main_robust,secondary_directions,n3_DS):
 labels=['B4-B1','B4-B2','B4-B3','D-B4','C-B4','D-S']
 if not required_gates or n<6:return dict.fromkeys(labels,'INCONCLUSIVE_REQUIRED_GATE')
 if n<12:return dict.fromkeys(labels,'FALLBACK_DESCRIPTIVE_COVERAGE_FAIL')
 p=np.r_[result['p'][0],result['secondary_Holm5']];out={};positive=False
 for k,label in enumerate(labels):
  threshold=.002 if k==0 else .001
  own=result['mean'][k]>=threshold and result['CI'][0,k]>threshold and p[k]<=.05 and np.all(result['LOMO'][:,k]>0)
  guards=main_robust and (k==0 or positive)
  if k>=3:guards=guards and secondary_directions[k-3]
  if k==5:guards=guards and n3_DS
  if result['mean'][k]<=0:out[label]='NEGATIVE_DIRECTION'
  elif own and guards:out[label]='HELDOUT_DESCRIPTIVE_POSITIVE'
  else:out[label]='MIXED_UNSUPPORTED'
  if k==0:positive=out[label]=='HELDOUT_DESCRIPTIVE_POSITIVE'
 return out

def circular_shift(spikes,onset,stop,rng):
 spikes=np.asarray(spikes,dtype=float)
 if stop<=onset or not np.isfinite(spikes).all() or np.any(spikes<onset) or np.any(spikes>=stop):raise ValueError('Source event support')
 shifted=onset+np.remainder(spikes-onset+rng.uniform(0,stop-onset),stop-onset)
 return np.sort(np.minimum(np.nextafter(stop,onset),np.maximum(onset,shifted)))
