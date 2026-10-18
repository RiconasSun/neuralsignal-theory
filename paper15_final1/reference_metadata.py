"""Freeze D control exposure from task/wheel metadata and C-only matching state."""
from collections import Counter
import numpy as np
from .source import P,read,dump,sha,source_rows
from .calibration import admitted,wheel
from .controls import stratum_keys,coverage
from .d_support import pre_epoch_wheel


def control_coverage(ids,keys2,keys3,bounds):
    ids=np.asarray(ids,int);lookup=set(ids.tolist());out={}
    out['N1']=dict(trial_ids=ids.tolist(),epochs=len(ids),total_epochs=len(ids),available=True)
    for suite,keys in [('N2',keys2),('N3',keys3)]:
        count=Counter(tuple(k) for k in keys);ix=[i for i,k in enumerate(keys) if count[tuple(k)]>=2]
        selected=ids[ix]
        out[suite]=dict(trial_ids=selected.tolist(),epochs=len(selected),total_epochs=len(ids),available=coverage(selected,len(ids)))
    blocks=[list(range(a,min(a+5,bounds[1]))) for a in range(bounds[0],bounds[1],5)]
    blocks=[b for b in blocks if len(b)==5 and all(i in lookup for i in b)]
    selected=set(i for b in blocks for i in b) if len(blocks)>=2 else set()
    selected=[i for i in ids.tolist() if i in selected]
    out['N4']=dict(trial_ids=selected,epochs=len(selected),total_epochs=len(ids),available=coverage(selected,len(ids)))
    return out


def prepare():
    target=P/'REFERENCE_METADATA_FREEZE.json';assert not target.exists()
    records=[]
    for subject in admitted():
        row=next(r for r in source_rows() if r['subject']==subject);meta=read(P/'metadata'/(subject+'_task.json'));wt,wp=wheel(row)
        cids=np.flatnonzero(np.asarray(meta['valid'])&(np.asarray(meta['roles'])=='C'))
        dids=np.flatnonzero(np.asarray(meta['valid'])&(np.asarray(meta['roles'])=='D'))
        cmag=pre_epoch_wheel(meta,cids,wt,wp);threshold=float(np.median(cmag));dmag=pre_epoch_wheel(meta,dids,wt,wp)
        bounds=meta['result']['partitions']['D'];keys2=stratum_keys(meta['trials'],dids,bounds,dmag,threshold);keys3=stratum_keys(meta['trials'],dids,bounds)
        prep=read(P/'states'/(subject+'_C_PREPROCESSING.json'));path=P/'work/C_features'/(subject+'.npz');assert sha(path)==prep['C_features_sha256']
        with np.load(path,allow_pickle=False) as arrays:warm_rate=arrays['y'][:,:10].sum(axis=1)/.5
        cov=control_coverage(dids,keys2,keys3,bounds)
        records.append(dict(subject=subject,D_trial_ids=dids.tolist(),C_wheel_median=threshold,C_wheel_magnitudes=cmag.tolist(),
            D_metadata_wheel_magnitudes=dmag.tolist(),keys_N2=keys2,keys_N3=keys3,role_bounds=bounds,coverage=cov,
            C_warm_rate_mean_by_unit=warm_rate.mean(axis=0).tolist(),C_warm_rate_sd_by_unit=warm_rate.std(axis=0).tolist(),
            C_wheel_displacement_mean=float(cmag.mean()),C_wheel_displacement_sd=float(cmag.std()),
            C_preprocessing_sha256=sha(P/'states'/(subject+'_C_PREPROCESSING.json')),task_sha256=sha(P/'metadata'/(subject+'_task.json'))))
        print(subject,'D metadata reference coverage',{s:(v['epochs'],v['available']) for s,v in cov.items()},flush=True)
    dump(target,dict(subjects=admitted(),records=records,replicates=999,suites=['N1','N2','N3','N4'],
        schedule='Original SHA256 P15-M1|150107|suite|subject|D|replicate; PCG64; no draws consumed by metadata coverage',
        D_neural_values_accessed=False,D_role_thinning_stream_consumed=False,matching_thresholds_fit_C_only=True))


if __name__=='__main__':prepare()
