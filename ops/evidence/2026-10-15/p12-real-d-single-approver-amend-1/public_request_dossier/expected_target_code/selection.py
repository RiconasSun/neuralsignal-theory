"""Frozen metadata/A-only selection; no validation or score argument."""
import math
def expected_shape(manifest_session,region,part):
    return (len(manifest_session['trial_ids'][part]),20,len(manifest_session['unit_ids'][region]))
def boundary(indices,metadata,distance):
    result=[]
    for i in indices:
        raw=metadata[i]['nearest_other_channel_label_vertical_um']
        try:value=float(raw)
        except (TypeError,ValueError):continue
        if math.isfinite(value) and value>distance:result.append(i)
    return result
def rate_pairs(ca,dg):
    unused=list(range(len(dg)));pairs=[]
    for i,x in enumerate(ca):
        eligible=[j for j in unused if x>0 and dg[j]>0 and abs(math.log(x/dg[j]))<=math.log(2)]
        if eligible:
            j=min(eligible,key=lambda j:(abs(math.log(x/dg[j])),j));pairs.append((i,j));unused.remove(j)
    return pairs
def views(ca,dg,metadata):
    base={'CA1':list(range(len(ca))),'DG':list(range(len(dg)))}
    result={'primary':base,'matched16':{k:v[:16] for k,v in base.items()}}
    pairs=rate_pairs(ca,dg);result['rate_matched']={'CA1':[i for i,j in pairs],'DG':[j for i,j in pairs]}
    for distance in (20,40):
        v={k:boundary(base[k],metadata[k],distance) for k in base};n=min(map(len,v.values()))
        result['boundary'+str(distance)]={k:vv[:n] for k,vv in v.items()}
    probes=sorted({str(m['probe_id']) for region in metadata.values() for m in region},key=int)
    candidates=[]
    for p in probes:
        v={k:[i for i,m in enumerate(metadata[k]) if str(m['probe_id'])==p] for k in base};n=min(map(len,v.values()))
        candidates.append((n,p,v))
        w={k:[i for i,m in enumerate(metadata[k]) if str(m['probe_id'])!=p] for k in base};n2=min(map(len,w.values()))
        if n2>=5:result['leave_probe_'+p]={k:vv[:n2] for k,vv in w.items()}
    if candidates:
        n,p,v=min(candidates,key=lambda t:(-t[0],int(t[1])))
        if n>=5:result['shared_probe_'+p]={k:vv[:n] for k,vv in v.items()}
    return result
