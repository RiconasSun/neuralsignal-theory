"""Pure custody binning/QC functions. Scientific observations must come from NWB."""
import numpy as np


def count_unit(times, trials, qc_partition):
    times = np.asarray(times)
    if times.ndim != 1 or times.dtype.kind != 'f' or not np.all(np.isfinite(times)) or np.any(np.diff(times)<0):
        raise ValueError('SOURCE_TIMESTAMP_INTEGRITY_FAILED')
    counts = np.zeros((len(trials),20),dtype='<u4')
    rate_total = active = pairs = violations = used = 0
    invalid_permitted = False
    for i,t in enumerate(trials):
        if not t['metadata_admitted']:
            continue
        edges = np.asarray(t['nominal_bin_edges'],dtype=float)
        if len(edges)!=21 or not np.allclose(np.diff(edges),.1,atol=1e-10,rtol=0) or edges[0]!=t['start'] or edges[-1]!=t['analysis_stop']:
            raise ValueError('FROZEN_BIN_EDGES_INVALID')
        indices = np.searchsorted(times,edges,side='left')
        vector = np.diff(indices)
        if np.any(vector>np.iinfo(np.uint32).max):
            raise ValueError('COUNT_OVERFLOW')
        counts[i]=vector
        if t['partition']==qc_partition:
            segment=times[indices[0]:indices[-1]]
            delta=np.diff(segment)
            invalid_permitted |= bool(np.any(segment<0) or np.any(delta<=0))
            rate_total+=len(segment)
            active+=bool(len(segment))
            used+=1
            pairs+=len(delta)
            violations+=int(np.count_nonzero(delta<.001))
    if not used:
        raise ValueError('NO_PERMITTED_QC_TRIALS')
    rate=rate_total/(2*used)
    fraction=active/used
    isi=violations/pairs if pairs else 0.
    eligible=.1<=rate<=100 and fraction>=.1 and isi<=.01 and not invalid_permitted
    qc={'rate_Hz':rate,'active_trial_fraction':fraction,'ISI_under_1ms_fraction':isi,'within_trial_ISI_pairs':pairs,
        'invalid_permitted_timestamps':invalid_permitted,'QC_trials':used,'eligible':bool(eligible)}
    return counts,qc


def public_train_export(counts,trials):
    indices=[i for i,t in enumerate(trials) if t['partition']=='train' and t['metadata_admitted']]
    return np.ascontiguousarray(counts[indices])


def guarded_publish(gate, payload):
    if not gate:
        raise PermissionError('CUSTODY_VERIFICATION_REQUIRED')
    if not isinstance(payload,bytes):
        raise ValueError('INVALID_PUBLIC_PAYLOAD')
    return payload
