"""Independent scalar/native input oracles; no optimizer or B/E neural reads."""
from bisect import bisect_left
import numpy as np

def nuisance_reference(trials,ids,starts,epochs,wt,wp):
    # Python bisect is independent of production numpy.searchsorted.
    timestamps=list(wt);prefix=np.r_[0.,np.cumsum(np.abs(np.diff(wp)))];out=[]
    def val(tr,key):return np.nan if tr.get(key) is None else np.float64(tr[key])
    def predecessor(t):
        index=bisect_left(timestamps,t)-1
        if index<0:raise ValueError('No strict-past wheel support')
        return index
    for tid,bs,epoch in zip(ids,starts,epochs):
        tr=trials[int(tid)];rows=[];base=predecessor(epoch)
        previous=None
        for candidate in trials[:int(tid)]:
            if val(candidate,'feedback_times')<epoch and val(candidate,'response_times')<epoch:previous=candidate
        for boundary in bs:
            a=val(tr,'intervals_0');s=val(tr,'stimOn_times');g=val(tr,'goCue_times')
            left=val(tr,'contrastLeft');right=val(tr,'contrastRight')
            if np.isnan(left):left=0.
            if np.isnan(right):right=0.
            e=np.clip(boundary-a,0,10)/10;seen=s<boundary;r=seen*np.clip(boundary-s,0,1)
            response=val(tr,'response_times')<boundary;feedback=val(tr,'feedback_times')<boundary
            order=float(tid)/1000;hour=boundary/3600
            cols=[e,np.power(e,2),r,np.power(r,2),np.power(r,3),seen*left,seen*right,seen*(left>0),seen*(right>0),
                seen*left*r,seen*right*r,g<boundary,(g<boundary)*np.clip(boundary-g,0,1),response,response*val(tr,'choice'),
                feedback,feedback*val(tr,'feedbackType'),0. if previous is None else val(previous,'feedbackType'),
                0. if previous is None else val(previous,'choice'),order,order**2,hour,np.power(hour,2)]
            ix=predecessor(boundary);dis=[];total=[];sq=[]
            for horizon in (.05,.1,.25,.5):
                j=predecessor(boundary-horizon);d=wp[ix]-wp[j]
                dis.append(d);total.append(prefix[ix]-prefix[j]);sq.append(np.power(d/horizon,2))
            cols += [wp[ix]-wp[base]]+dis+total+sq+[abs(dis[0])>.001]
            rows.append(cols)
        out.append(rows)
    return np.asarray(out,dtype=np.float64)

def counts_reference(times,labels,units,stimuli):
    edges=np.array([[np.float64(s)+np.float64(j-10)*np.float64(.05) for j in range(21)] for s in stimuli])
    edges[:,10]=stimuli;edges[:,-1]=stimuli+.5
    y=np.empty((len(stimuli),20,len(units)),np.int64);h=np.empty((len(stimuli),20,4*len(units)))
    for u,unit in enumerate(units):
        ordered=times[labels==unit].tolist()
        for i in range(len(stimuli)):
            for j in range(20):
                y[i,j,u]=bisect_left(ordered,edges[i,j+1])-bisect_left(ordered,edges[i,j])
                for k,(short,long) in enumerate([(0,1),(1,2),(2,4),(4,10)]):
                    h[i,j,4*u+k]=(bisect_left(ordered,edges[i,max(0,j-short)])-bisect_left(ordered,edges[i,max(0,j-long)]))/((long-short)*.05)
    return y,h,edges[:,:-1]

def masks_reference(trials,support,bad,wt):
    n=len(trials);cuts=[0,int(.6*n),int(.8*n),n];roles=[];valid=[]
    def v(tr,k):return np.nan if tr.get(k) is None else float(tr[k])
    for i,tr in enumerate(trials):
        role=0 if i<cuts[1] else 1 if i<cuts[2] else 2;roles.append('ABE'[role])
        a,s,g,f,z=[v(tr,k) for k in ['intervals_0','stimOn_times','goCue_times','feedback_times','intervals_1']]
        left,right=[v(tr,k) for k in ['contrastLeft','contrastRight']]
        ok=np.isfinite([a,s,g,f,z]).all() and a<=s<=f<=z and a<=g<=f
        ok=ok and s-.5>=a and s+.5<=z and s-1>=support[0] and s+.5<=support[1]
        ok=ok and not any(s-1<e and s+.5>b for b,e in bad)
        ok=ok and not (np.isnan(left) and np.isnan(right)) and (np.isnan(left) or 0<=left<=1) and (np.isnan(right) or 0<=right<=1)
        ok=ok and s-1>=v(trials[cuts[role]],'intervals_0') and s+.5<=v(trials[cuts[role+1]-1],'intervals_1')
        ok=ok and all(i not in (cut-1,cut) for cut in cuts[1:-1]) and s-1>wt[0] and s+.5<=wt[-1]
        for other in (i-1,i+1):
            if 0<=other<n:
                neighbor=v(trials[other],'stimOn_times')
                if np.isfinite([s,neighbor]).all() and max(s,neighbor)-.5<min(s,neighbor)+.5:ok=False
        valid.append(bool(ok))
    return np.asarray(roles),np.asarray(valid)

def physiology_reference(times,labels,units,uuids,ids,epochs,a_stop):
    cuts=[0,*[int(k*.25*a_stop) for k in (1,2,3)],a_stop]
    groups=np.array([next(q for q in range(4) if cuts[q]<=i<cuts[q+1]) for i in ids])
    exp=float(np.sum(epochs[:,1]-epochs[:,0]));qexp=[float(np.sum((epochs[:,1]-epochs[:,0])[groups==q])) for q in range(4)]
    output=[]
    for unit,uuid in zip(units,uuids):
        ordered=times[labels==unit].tolist();counts=0;pairs=0;bad=0;qc=[0]*4
        for epoch,q in zip(epochs,groups):
            part=ordered[bisect_left(ordered,epoch[0]):bisect_left(ordered,epoch[1])]
            counts+=len(part);qc[q]+=len(part);pairs+=max(0,len(part)-1)
            bad+=sum(b-a<.001 for a,b in zip(part[:-1],part[1:]))
        rate=counts/exp if exp else 0.;frac=bad/pairs if pairs else None;qr=[c/e if e else 0. for c,e in zip(qc,qexp)]
        qualified=.5<=rate<=100 and counts>=100 and pairs>=99 and frac is not None and frac<=.005 and min(qexp)>=10 and min(qr)>=.1
        output.append(dict(cluster_id=int(unit),uuid=uuid,A_spikes=counts,A_exposure_seconds=exp,A_rate_Hz=rate,
            A_within_epoch_ISI_pairs=pairs,A_refractory_pairs=bad,A_refractory_fraction=frac,original_A_quartile_exposures=qexp,
            original_A_quartile_spikes=qc,original_A_quartile_rates=qr,primary_qualified=qualified))
    ranking=sorted([x for x in output if x['primary_qualified']],key=lambda x:(x['A_refractory_fraction'],-x['A_rate_Hz'],x['uuid']))
    return output,ranking
