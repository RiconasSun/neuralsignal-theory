"""Pinned official barcode parsing plus independent all-code affine diagnostics."""
import importlib.util
import importlib.machinery
import json
from collections import Counter
import numpy as np
from register import HERE, sha

def check_policy():
    record=json.loads((HERE/'clock_registration.json').read_text())
    for path,digest in record['sha256'].items():
        if sha(HERE/path)!=digest: raise RuntimeError('Clock policy/source changed')
    if (HERE/'amendment1_registration.json').exists():
        amendment=json.loads((HERE/'amendment1_registration.json').read_text())
        for path,digest in amendment['sha256'].items():
            if sha(HERE/path)!=digest:raise RuntimeError('Schema amendment evidence changed')
    return json.loads((HERE/'CLOCK_POLICY.json').read_text())

def official():
    check_policy()
    loader=importlib.machinery.SourceFileLoader('pinned_allen_barcode',str(HERE/'metadata/sdk_source_0.receipt'))
    spec=importlib.util.spec_from_loader(loader.name,loader)
    module=importlib.util.module_from_spec(spec)
    exec(compile(loader.get_source(loader.name),loader.path,'exec'),module.__dict__)
    return module

def decode(on,off):
    policy=check_policy()
    times,codes=official().extract_barcodes_from_times(np.asarray(on),np.asarray(off),**policy['barcode_parameters'])
    if len(times)!=len(codes):raise RuntimeError('Barcode time/code mismatch; do not truncate identity pairing')
    return np.asarray(times,dtype=float),np.asarray(codes,dtype=np.uint64),0

def unwrap(counters):
    c=np.asarray(counters,dtype=np.int64)
    wraps=np.r_[0,np.diff(c)<0].astype(np.int64)
    return c+np.cumsum(wraps)*(2**32),int(wraps.sum())

def affine(master_times,master_codes,probe_times,probe_codes):
    mt=np.asarray(master_times,float);pt=np.asarray(probe_times,float)
    mc=Counter(int(c) for c in master_codes);pc=Counter(int(c) for c in probe_codes)
    lookup={int(c):t for c,t in zip(master_codes,mt) if mc[int(c)]==1}
    pairs=[(t,lookup[int(c)]) for t,c in zip(pt,probe_codes) if pc[int(c)]==1 and int(c) in lookup]
    result={'matched_codes':len(pairs),'master_duplicate_codes':sum(v>1 for v in mc.values()),
            'probe_duplicate_codes':sum(v>1 for v in pc.values()),'probe_unmatched_codes':sum(int(c) not in lookup for c in probe_codes),
            'pass':False}
    if len(pairs)<3:result['error']='Fewer than3 unique matching codes';return result
    x,y=np.asarray(pairs).T
    xc=x-x.mean();slope=float(np.dot(xc,y-y.mean())/np.dot(xc,xc));offset=float(y.mean()-slope*x.mean())
    residual=y-(slope*x+offset)
    result.update({'slope':slope,'offset_seconds':offset,'probe_anchor_min_seconds':float(x.min()),
                   'probe_anchor_max_seconds':float(x.max()),'master_anchor_min_seconds':float(y.min()),
                   'master_anchor_max_seconds':float(y.max()),'residual_max_seconds':float(np.max(np.abs(residual))),
                   'residual_p95_seconds':float(np.quantile(np.abs(residual),.95)),
                   'residual_rms_seconds':float(np.sqrt(np.mean(residual**2)))})
    policy=check_policy()['diagnostic_accuracy_seconds']
    result['pass']=bool(slope>0 and result['residual_p95_seconds']<=policy['p95_absolute_residual_maximum'] and
                        result['residual_max_seconds']<=policy['absolute_residual_maximum'])
    return result

def probe_segments(times,states):
    times=np.asarray(times,float)/30000
    states=np.asarray(states)
    if len(times)!=len(states) or times.ndim!=1 or states.ndim!=1:raise RuntimeError('Digital edge shape mismatch')
    if not np.all(np.isin(states,np.arange(-16,17))):raise RuntimeError('Undefined digital channel identifier')
    if not np.all(np.isfinite(times)) or np.any(np.diff(times)<0):raise RuntimeError('Non-monotone native digital timestamps')
    starts,codes,parser_mismatch=decode(times[states==1],times[states==-1])
    markers=times[states==0]
    intervals=np.diff(starts)
    irregular=np.where(np.abs(intervals-np.median(intervals))>.0001*np.median(intervals))[0] if len(intervals) else []
    # Preserve the upstream split algorithm, including its negative-index edge case.
    splits=[0.0]+list(markers)
    for i in irregular:
        splits.append(float(starts[i-1]))
        if i+1<len(starts):splits.append(float(starts[i+1]))
    return starts,codes,sorted(set(splits)),{'state_zero_markers':len(markers),'irregular_barcode_intervals':len(irregular),
                                          'parser_length_mismatch':parser_mismatch,'native_first_edge_seconds':float(times.min()) if len(times) else None,
                                          'native_last_edge_seconds':float(times.max()) if len(times) else None,
                                          'nonbarcode_line_identifiers_not_interpreted':int(np.sum(~np.isin(states,[-1,0,1]))),
                                          'first_barcode_ignored_by_official_parser':True}
