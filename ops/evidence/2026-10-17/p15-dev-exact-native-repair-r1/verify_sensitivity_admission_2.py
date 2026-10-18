"""Independent actual saved sensitivity admission; A inputs only, never fits/scores."""
import datetime,hashlib,math,re,runpy
from bisect import bisect_left
from pathlib import Path
import numpy as np
from paper15_r1.source import P,R,load_json,dump
from paper15_r1.metadata_access import local_path
from paper15_r1.input_oracle import nuisance_reference,physiology_reference

E=Path(__file__).resolve().parent
def read(p):return load_json(p.read_text(encoding='utf8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
CASES=[dict(id='S01',units=5),dict(id='S02',units=12),dict(id='S03',units=20),dict(id='S04',units=8,delta=.1),
       dict(id='S05',units=8,warmup=.25,history=.25),dict(id='S06',units=8,strict=True),dict(id='S07',units=8,thin=True),
       dict(id='S08',units=8,dilation=.01),dict(id='S09',units=8,dilation=.05),dict(id='S10',units=8,rich=True),dict(id='S11',units=5,boundary=True)]

def nominal(c):
    f=c['family'];u=8
    return {'B0':u,'B1':38*u,'B2':42*u,'B3':66*u,'B4':70*u}.get(f,70*u+u*c['rank'] if f=='C' else 70*u+(c['k']-1)*u+c['k']-1+(c['k']*(c['k']-1) if f=='D' else 0)) if f not in ('B0','B1','B2','B3','B4') else {'B0':u,'B1':38*u,'B2':42*u,'B3':66*u,'B4':70*u}[f]

def choose(cs):
    best=max(x['equal_mouse_LL_per_unit_bin'] for x in cs)
    def tie(x):
        c=x['configurations'][0]
        return nominal(c),-c['ridge'],c.get('k',c.get('rank',0)),c.get('tau',0),x['id']
    return min((x for x in cs if best-x['equal_mouse_LL_per_unit_bin']<=1e-6),key=tie)['id']

def case_metadata(main,case):
    t=main['trials'];s=np.array([np.nan if x['stimOn_times'] is None else x['stimOn_times'] for x in t]);a=np.array([np.nan if x['intervals_0'] is None else x['intervals_0'] for x in t]);z=np.array([np.nan if x['intervals_1'] is None else x['intervals_1'] for x in t])
    lo=s-case.get('warmup',.5);hi=s+.5;support=main['result']['recording_sync_support']
    ck={k:np.array(v,bool) for k,v in main['check_masks'].items()}
    ck['neural_epoch_inside_trial']=(lo>=a)&(hi<=z);ck['recording_sync_support']=(lo>=support[0])&(hi<=support[1])
    overlap=np.ones(len(t),bool);ii=np.flatnonzero(np.isfinite(s))
    for before,after in zip(ii[:-1],ii[1:]):
        if lo[after]<hi[before]:overlap[[before,after]]=False
    ck['no_overlapping_epoch']=overlap
    sat=np.array(main['selected_probe_saturation_session_seconds']).reshape(-1,2).copy();d=case.get('dilation',0.)
    if len(sat):sat[:,0]-=d;sat[:,1]+=d
    ck['no_known_saturation']=np.array([not any(x-1<e and x+.5>b for b,e in sat) for x in s])
    valid=np.logical_and.reduce(list(ck.values()))
    return ck,valid,sat

def counts(st,units,stim,delta,warmup,history):
    micro=int(round((warmup+.5)/.05));mw=int(round(warmup/.05));step=int(round(delta/.05));n=micro//step
    edges=np.array([[s+(j-mw)*.05 for j in range(micro+1)] for s in stim]);edges[:,mw]=stim;edges[:,-1]=stim+.5
    starts=edges[:,np.arange(n)*step];y=np.empty((len(stim),n,len(units)),np.int64);h=np.empty((len(stim),n,4*len(units)))
    windows=[0,1,2,4,int(round(history/.05))]
    for u,unit in enumerate(units):
        ordered=st[unit]
        for i in range(len(stim)):
            for j in range(n):
                current=j*step;y[i,j,u]=bisect_left(ordered,edges[i,(j+1)*step])-bisect_left(ordered,edges[i,current])
                for k,(short,long) in enumerate(zip(windows[:-1],windows[1:])):
                    h[i,j,4*u+k]=(bisect_left(ordered,edges[i,max(0,current-short)])-bisect_left(ordered,edges[i,max(0,current-long)]))/((long-short)*.05)
    return y,h,starts

def run():
    target=E/'SENSITIVITY_ADMISSION_CHECKS_2.json';assert not target.exists()
    selected=read(P/'SELECTION_FREEZE.json');candidates=read(P/'results/B_CANDIDATE_SCORES.json');prep=read(P/'results/SENSITIVITY_PREPARATION.json');plan=read(P/'SENSITIVITY_FIT_PLAN.json')
    assert prep['cases']==CASES and len(candidates)==37
    subjects=selected['subjects'];gate=read(P/'results/M2_PHYSIOLOGY_GATE.json');assert subjects==[x['subject'] for x in gate['subjects'] if x['admitted']]
    assert sha(P/'results/B_CANDIDATE_SCORES.json')==selected['candidates_sha256']
    for rel,v in selected['source_hashes'].items():assert sha(P/rel)==v
    markers={}
    for name in ['BASELINE_ATTEMPTS_COMPLETE.json','DYNAMIC_ATTEMPTS_COMPLETE.json']:markers.update(read(P/'results'/name)['attempt_hashes'])
    assert len(markers)==610
    for c in candidates:
        assert c['available'] and c['nominal_parameters']==nominal(c['configurations'][0])
        assert [x['subject'] for x in c['mouse_scores']]==subjects
        for m in c['mouse_scores']:
            assert math.isfinite(m['LL']) and m['unit_bins']>0 and m['LL_per_unit_bin']==m['LL']/m['unit_bins']
            assert m['fit_hashes']==[markers[m['subject']+'/'+x['id']] for x in c['configurations']]
            assert m['seed_logmass_ensemble']==len(c['configurations'])
            if c['configurations'][0]['family'] in ('D','S'):assert [x['seed'] for x in c['configurations']]==[11,23,37]
        assert c['equal_mouse_LL_per_unit_bin']==float(np.mean([x['LL_per_unit_bin'] for x in c['mouse_scores']]))
    winners={f:choose([c for c in candidates if c['configurations'][0]['family']==f]) for f in ['B0','B1','B2','B3','B4','D','C']}
    dc=next(c for c in candidates if c['id']==winners['D'])['configurations'][0]
    winners['S']=choose([c for c in candidates if c['configurations'][0]['family']=='S' and c['configurations'][0]['k']==dc['k']+1])
    assert winners==selected['selected']
    assert prep['planned_fits']==plan['expected_attempts']==525
    assert len(prep['records'])==len({(x['subject'],x['case']) for x in prep['records']})==110
    source=read(P/'SOURCE_FILE_FREEZE.json');atlas={int(x['id']):x['acronym'] for x in read(R/'paper13/metadata/atlas.json')['msg']}
    rows=[];expected=[];thinning_units=0
    for subject in subjects:
        main=read(P/'metadata'/(subject+'_task.json'));qc=read(P/'results'/(subject+'_A_QC.json'));entry=next(x for x in source['subjects'] if x['subject']==subject)
        assert entry['allocation']=='DEVELOPMENT';export=P/'work/A_exports'/(subject+'.npz');assert sha(export)==qc['A_export_sha256']
        with np.load(export,allow_pickle=False) as a:times,labels=a['times'],a['labels']
        paths={f['role']:local_path(entry,f) for f in entry['files'] if f['role'] in ('wheel_times','wheel_position','atlas')}
        wt=np.load(paths['wheel_times'],allow_pickle=False);wp=np.load(paths['wheel_position'],allow_pickle=False);contacts=np.load(paths['atlas'],allow_pickle=False)
        original={x['cluster_id']:x for x in qc['physiology']};st={unit:times[labels==unit].tolist() for unit in qc['ranking']}
        for case in CASES:
            cid=case['id'];path=P/'sensitivity_states'/subject/(cid+'.json');state=read(path);manifest=next(x for x in prep['records'] if x['subject']==subject and x['case']==cid)
            assert state['subject']==subject and state['case']==case and state['status']==manifest['status']
            assert state['B_selection_sha256']==sha(P/'SELECTION_FREEZE.json') and state['source_QC_sha256']==sha(P/'results'/(subject+'_A_QC.json'))
            assert not state['Final_access'] and not state['E_neural_access']
            met=state['metadata'];assert met['trials']==main['trials'] and met['roles']==main['roles'] and met['native_table']==main['native_table']
            ck,valid,sat=case_metadata(main,case)
            assert met['check_masks']=={k:v.tolist() for k,v in ck.items()};np.testing.assert_array_equal(valid,met['valid'])
            np.testing.assert_array_equal(sat,np.array(met['selected_probe_saturation_session_seconds']).reshape(-1,2))
            roles=np.array(main['roles']);trial_counts={r:int(np.sum(valid&(roles==r))) for r in 'ABE'};assert trial_counts==state['trial_counts']
            ids=np.flatnonzero(valid&(roles=='A'));stim=np.array([main['trials'][i]['stimOn_times'] for i in ids]);warmup=case.get('warmup',.5)
            ranking=qc['ranking'];metrics=qc['physiology']
            if cid in ('S05','S08','S09'):
                eps=np.column_stack((stim-warmup,stim+.5));metrics,rr=physiology_reference(times,labels,list(original),[original[u]['uuid'] for u in original],ids,eps,main['result']['partitions']['A'][1]);ranking=[m['cluster_id'] for m in rr]
                assert len(metrics)==len(state['physiology'])
                for ref,actual in zip(metrics,state['physiology']):
                    for k,v in ref.items():assert actual[k]==v
            else:assert state['physiology']==metrics
            if cid=='S06':ranking=[u for u in ranking if original[u]['strict_QC_qualified']]
            if cid=='S11':
                allowed=[]
                for u in ranking:
                    ch=main['native_cluster_channel'][u]
                    if ch>=2 and ch+2<len(contacts) and all(re.fullmatch(r'MOp(?:1|2/3|4|5|6a|6b)?',str(atlas.get(int(v)))) for v in contacts[ch-2:ch+3]):allowed.append(u)
                ranking=allowed
            assert state['ranked_units']==ranking
            units=ranking[:case['units']];assert state['units']==units
            reasons=[]
            if len(units)<case['units']:reasons.append('INSUFFICIENT_REGISTERED_UNIT_CAPACITY')
            if any(trial_counts[r]<floor for r,floor in dict(A=80,B=40,E=40).items()):reasons.append('REGISTERED_TRIAL_COVERAGE_FAILURE')
            assert state['unavailability_reasons']==reasons
            if reasons:
                assert manifest['reasons']==reasons and state['status']=='UNAVAILABLE'
                rows.append(dict(subject=subject,case=cid,status='UNAVAILABLE',reasons=reasons,state_sha256=sha(path)));continue
            assert state['status']=='A_PREPROCESSING_SEALED' and sha(path)==manifest['state_sha256']
            series={u:st[u] for u in units}
            if cid=='S07':
                assert units==qc['selected_unit_ids'];thin=[];series={}
                for u in units:
                    uuid=original[u]['uuid'];seed=int.from_bytes(hashlib.sha256(f'P15-M1|150108|S07|{subject}|{uuid}|A'.encode()).digest()[:8],'big');p=min(1.,2/original[u]['A_rate_Hz'])
                    ix=np.flatnonzero(labels==u);mask=np.random.Generator(np.random.PCG64(seed)).random(len(ix))<p
                    series[u]=times[ix[mask]].tolist();thin.append(dict(unit=u,uuid=uuid,role='A',p=p,seed=seed,draw_count=len(ix),kept=int(mask.sum())));thinning_units+=1
                assert state['thinning_A']==thin
            delta=case.get('delta',.05);y,h,b=counts(series,units,stim,delta,warmup,case.get('history',.5))
            nx=nuisance_reference(main['trials'],ids,b,stim-.5,wt,wp)
            if cid=='S10':
                order=ids[:,None]/1000;hour=b/3600
                extra=np.stack([np.broadcast_to(order**3,b.shape),np.broadcast_to(order**4,b.shape),hour**3,hour**4],axis=-1);nx=np.concatenate([nx,extra],axis=-1)
            raw=np.concatenate([nx,h],axis=-1);warm=int(round(warmup/delta));score=raw[:,warm:].reshape(-1,raw.shape[-1]);mean=score.sum(axis=0)/len(score);sd=np.sqrt(((score-mean)**2).sum(axis=0)/len(score));active=sd>=1e-8
            np.testing.assert_array_equal(mean,state['scales']['mean']);np.testing.assert_array_equal(sd,state['scales']['sd']);np.testing.assert_array_equal(active,state['scales']['active'])
            x=np.concatenate([np.ones((*raw.shape[:2],1)),np.where(active,np.clip((raw-mean)/np.where(active,sd,1.),-3,3),0.)],axis=-1)
            arr=P/'work/sensitivity_A'/subject/(cid+'.npz');assert sha(arr)==state['A_features_sha256']
            with np.load(arr,allow_pickle=False) as a:
                np.testing.assert_array_equal(a['x'],x);np.testing.assert_array_equal(a['y'],y);np.testing.assert_array_equal(a['active'],np.r_[True,active]);np.testing.assert_array_equal(a['trial_ids'],ids)
            assert state['warm']==warm and state['delta']==delta and state['nuisance_columns']==(41 if cid=='S10' else 37)
            if cid=='S07':np.testing.assert_array_equal(state['achieved_A_epoch_rates_Hz'],y.sum(axis=(0,1))/(len(ids)*(warmup+.5)))
            for f in ['B0','B1','B2','B3','B4']:
                c=next(c for c in candidates if c['id']==winners[f])['configurations'][0]
                expected.append(dict(subject=subject,case=cid,family=f,ridge=c['ridge'],seed=11,state_sha256=sha(path)))
            rows.append(dict(subject=subject,case=cid,status=state['status'],state_sha256=sha(path),features_sha256=sha(arr),units=units,A_epochs=len(ids),independent_masks_QC_rank_counts_history_features_scalers_exact=True))
        print(subject,'eleven actual cases verified',flush=True)
    assert plan['attempts']==expected and len(expected)==525 and len(rows)==110 and thinning_units==80
    assert plan['max_retries']==0 and not plan['new_hyperparameter_search'] and plan['Final_fits']==0 and plan['B_selection_sha256']==sha(P/'SELECTION_FREEZE.json')
    assert plan['solver']==dict(maxiter=2000,maxfun=80000,maxls=40,ftol=1e-12,gtol=1e-6)
    assert not list((P/'sensitivity_fits').glob('*/*/*.json')) and not (P/'E_BATCH_CLAIM.json').exists()
    dump(target,dict(time=datetime.datetime.now(datetime.timezone.utc).isoformat(),script_sha256=sha(Path(__file__)),
         selection_sha256=sha(P/'SELECTION_FREEZE.json'),plan_sha256=sha(P/'SENSITIVITY_FIT_PLAN.json'),rows=rows,cases=110,available=105,unavailable=5,planned_attempts=525,
         independently_verified_B_saved_selection=True,S07_original_A_unit_streams_replayed=80,A_only_all_case_numerics=True,new_fits=0,B_E_neural_rescoring=False,Final_access=False))

if __name__=='__main__':run()
