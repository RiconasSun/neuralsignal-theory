"""Small non-predictive feasibility primitives; no model definitions."""
import numpy as np
from scipy.interpolate import interp1d

def map_clock(sync, probe_seconds):
    sync=np.asarray(sync,float)
    assert sync.ndim==2 and sync.shape[1]==2 and len(sync)>=2 and np.isfinite(sync).all()
    assert (np.diff(sync,axis=0)>0).all()
    # Identical interpolation/extrapolation convention to provider apply_sync.
    return interp1d(sync[:,0],sync[:,1],fill_value='extrapolate')(probe_seconds)

def overlap(starts,stops,bad):
    out=np.zeros(len(starts),bool)
    for a,b in np.asarray(bad).reshape(-1,2):
        assert np.isfinite([a,b]).all() and a<=b
        out|=(starts<b)&(stops>a)
    return out

def count_bins(times,labels,units,edges,bad=()):
    assert np.isfinite(times).all() and (np.diff(times)>=0).all()
    assert len(times)==len(labels) and np.isfinite(edges).all() and (np.diff(edges)>0).all()
    counts=np.zeros((len(edges)-1,len(units)),np.int64)
    for j,u in enumerate(units):
        st=times[labels==u]
        counts[:,j]=np.diff(np.searchsorted(st,edges,side='left'))
    valid=~overlap(edges[:-1],edges[1:],bad)
    return counts,valid
