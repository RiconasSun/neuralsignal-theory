"""Frozen metadata covariates and train-only transforms, no raw source loader."""
import json
from pathlib import Path
import numpy as np
from .source import ROOT

def event_series(record):
    v=json.loads((ROOT/record['header_file']).read_text())['decoded_values']
    kinds={'tone':[],'noise':[],'airpuff':[],'opto':[]}
    for path,values in v.items():
        if not path.startswith('/stimulus/presentation/') or not path.endswith('/timestamps'):continue
        name=path.lower()
        if 'khz' in name or 'puretone' in name:kind='tone'
        elif 'noise' in name:kind='noise'
        elif 'puff' in name:kind='airpuff'
        elif 'opto' in name:kind='opto'
        else:continue
        kinds[kind].extend(values)
    return {k:np.unique(np.asarray(v,dtype=float)) for k,v in kinds.items()}

def nuisance(record,epochs):
    series=event_series(record);out=[]
    for e in epochs:
        start=e['start']+np.arange(30)/10;v=(np.arange(30)+.5)/30;u=e['ordinal']/120
        index=np.searchsorted(series['tone'],start,side='left')
        prior=np.where(index>0,series['tone'][np.maximum(0,index-1)],start-60) if len(series['tone']) else start-60
        age=np.minimum(60,start-prior)
        cols=[v,v*v,np.sin(2*np.pi*v),np.cos(2*np.pi*v),np.full(30,u),np.full(30,u*u),np.log1p(age)]
        for key in ['tone','noise','airpuff','opto']:
            t=series[key]
            cols.append(np.searchsorted(t,start,side='left')-np.searchsorted(t,start-30,side='left'))
        out.append(np.stack(cols,axis=-1))
    x=np.stack(out)
    if x.shape!=(len(epochs),30,11) or not np.isfinite(x).all():raise ValueError('Nuisance shape/finite failure')
    return x
