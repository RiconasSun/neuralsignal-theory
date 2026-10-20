"""Frozen prefit panel definitions and training-only subset/support decisions."""
import numpy as np
from .core import R,load,REFIT_PANELS,ImplementationStop
from .features import middle_rate_units

VISP={'VISp','VISp1','VISp2/3','VISp4','VISp5','VISp6a','VISp6b'}

def full_support(flashes,running):
    invalid=np.asarray(running.get('invalid',[])).reshape(-1,2)
    return np.asarray(flashes['main_valid'],bool)&np.array([not np.any((invalid[:,0]<b)&(a<invalid[:,1])) for a,b in zip(flashes['start'],flashes['stop'])])

def anatomy_subset(ids,certificates,channels,probe):
    rows=[x for x in channels if int(x['ecephys_probe_id'])==int(probe)]
    by_id={int(x['id']):x for x in rows};by_local={int(x['local_index']):x for x in rows};selected=[];composition=[]
    for uid in ids:
        peak=certificates[int(uid)]['peak_channel_id'];center=by_id.get(int(peak));labels=[]
        if center is not None:
            k=int(center['local_index']);labels=[by_local.get(i,{}).get('structure_acronym') for i in [k-1,k,k+1]]
        passed=len(labels)==3 and all(x in VISP for x in labels)
        composition.append({'unit_id':int(uid),'peak_channel_id':int(peak),'labels':labels,'proxy_pass':passed})
        if passed:selected.append(int(uid))
    return selected,composition

def prefit_plan(record,main_batch,flashes,running):
    if main_batch.role!='A':raise ImplementationStop('Panel decisions require A only')
    ids=main_batch.unit_ids.tolist();sid=record['source']['session_id'];mask=np.asarray(record['selection']['common_mask'],bool)
    certs={x['unit_id']:x for x in load(R/'paper16_dev_r3/SOURCE_CANDIDATE_CERTIFICATES.json')['candidates'] if x['session_id']==sid}
    strict=[uid for uid in ids if float(certs[uid]['provider_amplitude_cutoff'])<=.05 and float(certs[uid]['provider_presence_ratio'])>=.98 and float(certs[uid]['provider_isi_violations'])<=.1]
    channels=load(R/'paper16_m0/metadata/channels.body')['msg']
    anatomical,composition=anatomy_subset(ids,certs,channels,record['source']['probe_id'])
    middle,rates=middle_rate_units(main_batch);full=full_support(flashes,running)
    result=[]
    for panel in REFIT_PANELS:
        units=ids if panel not in ['S06','S07','S10','S11'] else {'S06':ids[:4],'S07':sorted(map(int,middle)),'S10':strict,'S11':anatomical}[panel]
        support=mask&full if panel=='S10' else mask.copy();reason=None
        if panel=='S05':reason='NO_FROZEN_VERIFIED_PUPIL_EXPOSURE_END_CERTIFICATE; frame availability is unknown, not absent arousal'
        elif len(units)<4:reason='FEWER_THAN_FOUR_ORIGINAL_MAIN_SUBSET_UNITS'
        elif panel=='S10':
            for lo,hi,floor in [(0,90,30),(90,120,8),(120,150,8)]:
                if any(np.count_nonzero(support[lo:hi]&(flashes['color'][lo:hi]==c))<floor for c in [-1,1]):reason='ORIGINAL_ROLE_COLOR_FULL_FLASH_COVERAGE_NOT_MET'
        row={'panel':panel,'unit_ids':units,'mask':support.tolist(),'status':'UNAVAILABLE' if reason else 'AVAILABLE',
            'pre_fit_reason':reason,'optimizer_tasks':0 if reason else 3*len(units)+6,
            'models':['B1','B4','C','D','S'],'D_S_seeds':[11,23,37],'lambda_policy':'MAIN_GLOBAL_B1_SELECTION'}
        if panel=='S07':row.update({'main_A_score_rates':rates.tolist(),'middle_rank_order':middle.tolist(),'rate_window_ms':[100,220],'ranking_mask':'MAIN_A_COMMON','fitting_order':'numeric Unit ID'})
        if panel=='S11':row['anatomy_composition']=composition
        if panel=='S05':row['availability_evidence']={'source':'Frozen M1 observation-QC pupil rule; R2 native running-only schema and its saved source certificates','unverified_timing_fails_before_fit':True,'not_a_numerical_failure':True}
        result.append(row)
    return result

def task_plan(records,panels):
    tasks=[]
    def add(mouse,panel,model,unit=None,seed=None,lam='GLOBAL'):
        task={'mouse_id':str(mouse),'panel':panel,'model':model,'unit_id':unit,'seed':seed,'lambda':lam}
        task['id']=':'.join(str(task[k]) for k in ['mouse_id','panel','model','unit_id','seed','lambda']);tasks.append(task)
    for record in records:
        mouse=record['source']['mouse_id'];ids=record['selection']['selected_unit_ids']
        for lam in [.01,.1,1.]:
            for unit in ids:add(mouse,'MAIN','B1',unit=unit,lam=lam)
        for model in ['B2','B3','B4','C']:
            for unit in ids:add(mouse,'MAIN',model,unit=unit)
        for model in ['D','S']:
            for seed in [11,23,37]:add(mouse,'MAIN',model,seed=seed)
        for panel in panels[str(mouse)]:
            if panel['status']!='AVAILABLE':continue
            for model in ['B1','B4','C']:
                for unit in panel['unit_ids']:add(mouse,panel['panel'],model,unit=unit)
            for model in ['D','S']:
                for seed in [11,23,37]:add(mouse,panel['panel'],model,seed=seed)
    if len(tasks)>7506 or len({x['id'] for x in tasks})!=len(tasks):raise ImplementationStop('Exact frozen task budget/identity')
    return {'tasks':tasks,'optimizer_attempt_count':len(tasks),'B1_selection_attempts':27*3*8,
        'full_study_ceiling':16178,'Final_reserved':7722,'reserved_Final_borrowed':0,'extra_or_replacement_tasks_allowed':False}
