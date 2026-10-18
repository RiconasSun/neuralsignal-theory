"""Frozen A-only physiology primitives; callers must enforce role/source gates."""
import numpy as np


def unit_qc(times, labels, units, uuids, trial_ids, epochs, original_A_stop):
    times=np.asarray(times,float);labels=np.asarray(labels)
    assert len(times)==len(labels) and np.isfinite(times).all() and (np.diff(times)>=0).all()
    assert epochs.shape==(len(trial_ids),2) and np.isfinite(epochs).all()
    assert (epochs[:,1]>epochs[:,0]).all() and (np.diff(epochs[:,0])>0).all()
    assert np.all(epochs[1:,0]>=epochs[:-1,1])
    assert np.all((trial_ids>=0)&(trial_ids<original_A_stop))
    # Original A quartiles precede masks and do not rebalance after attrition.
    quarter_cuts=np.array([0,*[int(k*.25*original_A_stop) for k in (1,2,3)],original_A_stop])
    qids=np.searchsorted(quarter_cuts[1:],trial_ids,side='right')
    exposure=float(np.sum(epochs[:,1]-epochs[:,0]))
    qexp=[float(np.sum((epochs[:,1]-epochs[:,0])[qids==q])) for q in range(4)]
    out=[]
    for unit,uuid in zip(units,uuids):
        st=times[labels==unit]
        count=0;pairs=0;refractory=0;qcounts=np.zeros(4,int)
        for i,(lo,hi) in enumerate(epochs):
            a,b=np.searchsorted(st,[lo,hi],side='left');part=st[a:b];n=len(part)
            count+=n;qcounts[qids[i]]+=n
            if n>1:
                pairs+=n-1;refractory+=int(np.sum(np.diff(part)<.001))
        rate=count/exposure if exposure else 0.
        isi=refractory/pairs if pairs else None
        qrates=[int(c)/e if e else 0. for c,e in zip(qcounts,qexp)]
        reasons=[]
        if not .5<=rate<=100:reasons.append('RATE_OUTSIDE_0.5_100_HZ')
        if count<100:reasons.append('SPIKES_LT_100')
        if pairs<99:reasons.append('ISI_PAIRS_LT_99')
        if isi is None or isi>.005:reasons.append('ISI_FRACTION_GT_0.005_OR_UNDEFINED')
        if min(qexp)<10:reasons.append('ORIGINAL_A_QUARTILE_EXPOSURE_LT_10_S')
        if min(qrates)<.1:reasons.append('ORIGINAL_A_QUARTILE_RATE_LT_0.1_HZ')
        strict=not reasons and 1<=rate<=50 and isi<=.0025 and min(qrates)>=.2
        out.append(dict(cluster_id=int(unit),uuid=str(uuid),A_spikes=count,A_exposure_seconds=exposure,
            A_rate_Hz=rate,A_within_epoch_ISI_pairs=pairs,A_refractory_pairs=refractory,A_refractory_fraction=isi,
            original_A_quartile_exposures=qexp,original_A_quartile_spikes=qcounts.tolist(),original_A_quartile_rates=qrates,
            primary_qualified=not reasons,strict_QC_qualified=strict,exclusion_reasons=reasons))
    ranked=sorted([x for x in out if x['primary_qualified']],key=lambda x:(x['A_refractory_fraction'],-x['A_rate_Hz'],x['uuid']))
    return out,ranked
