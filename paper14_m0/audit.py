"""Saved behavioral/anatomical metadata only; never reads neural arrays."""
import gzip
import hashlib
import itertools
import json
import re
from pathlib import Path
import numpy as np
import pandas as pd

P=Path(__file__).resolve().parent
ROOT=P.parent
REGIONS=['ACAd','ACAv','PL','ILA','mPFC_composite']
CONTEXTS=[.2,.8]


def read(path):return json.loads(Path(path).read_text(encoding='utf8'))
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def write(path,obj):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(obj,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
def table(path,frame):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    raw=frame.to_csv(index=False,lineterminator='\n').encode()
    path.write_bytes(gzip.compress(raw,mtime=0) if path.suffix=='.gz' else raw)


def workdir(root=None):
    """Initialize ignored scratch in a checkout that never ran retrieval."""
    path=(P if root is None else Path(root))/'work'
    path.mkdir(parents=True,exist_ok=True)
    return path


def verify_inputs():
    for name,digest in read(P/'INPUT_FREEZE.json')['hashes'].items():
        if sha(ROOT/name)!=digest:raise ValueError('Original metadata changed: '+name)


def region(acronym):
    m=re.fullmatch(r'(ACAd|ACAv|PL|ILA)(?:1|2/3|4|5|6a|6b)?',str(acronym))
    return m.group(1) if m else None


def session_blocks(frame):
    """Preserve original trial/run order and cut before any exclusions."""
    x=frame.reset_index(drop=True).copy();N=len(x)
    for name in ['stimOn_times','goCue_times','feedback_times','intervals_0','intervals_1','probabilityLeft']:
        if name not in x:raise ValueError('Missing required trial field: '+name)
    if any(name not in x for name in ['bwm_include','saturation_stim_plus06']):raise ValueError('Missing required source mask')
    times=x['stimOn_times'].to_numpy(dtype=float);finite_times=times[np.isfinite(times)]
    chronological=bool(np.all(np.diff(finite_times)>0))
    a=x[['intervals_0','stimOn_times','goCue_times','feedback_times','intervals_1']].to_numpy(dtype=float)
    reasons={
        'nonfinite_event':~np.isfinite(a).all(axis=1),
        'invalid_event_order':~((a[:,0]<=a[:,1])&(a[:,1]<=a[:,2])&(a[:,2]<=a[:,3])&(a[:,3]<=a[:,4])&(a[:,0]<a[:,4])),
        'window_outside_trial':~(a[:,1]+.5<=a[:,4]),
        'provider_excluded':~x['bwm_include'].eq(True).to_numpy(),
        'saturation_or_unknown':~x['saturation_stim_plus06'].eq(False).to_numpy()}
    valid=~np.logical_or.reduce(list(reasons.values()))
    runs=[];run_index=np.full(N,-1,dtype=int);previous=None;current=None
    for j,p in enumerate(x['probabilityLeft']):
        label=float(p) if pd.notna(p) else None
        if label not in CONTEXTS:previous=None;current=None;continue
        if current is None or label!=previous:
            runs.append({'run':len(runs),'context':label,'first_trial':j,'last_trial':j,'raw_trials':0,'valid_trials':0})
            current=runs[-1]
        current['last_trial']=j;current['raw_trials']+=1;current['valid_trials']+=int(valid[j]);run_index[j]=current['run'];previous=label
    cut=len(runs)//2
    for r in runs:r.update(half='calibration' if r['run']<cut else 'scoring',qualifying=r['valid_trials']>=15)
    counts={}
    usable=np.zeros(N,dtype=bool)
    for r in runs:
        if r['qualifying']:usable|=(run_index==r['run'])&valid
    for ctx in CONTEXTS:
        selected=[r for r in runs if r['context']==ctx];qual=[r for r in selected if r['qualifying']]
        mask=x['probabilityLeft'].eq(ctx).to_numpy()
        counts[ctx]={'raw_trials':int(mask.sum()),'valid_trials':int((mask&valid).sum()),
            'usable_trials':int((mask&usable).sum()),'runs':len(selected),'qualifying_runs':len(qual),
            'calibration_trials':sum(r['valid_trials'] for r in qual if r['half']=='calibration'),
            'scoring_trials':sum(r['valid_trials'] for r in qual if r['half']=='scoring'),
            'order_quartiles':[int((mask&usable&(np.minimum(np.arange(N)*4//max(N,1),3)==q)).sum()) for q in range(4)]}
    eligible=chronological and all(z['qualifying_runs']>=2 and z['calibration_trials']>=60 and z['scoring_trials']>=60 for z in counts.values())
    return {'chronological':chronological,'run_count':len(runs),'context_switches':sum(runs[j]['context']!=runs[j-1]['context'] for j in range(1,len(runs))),
        'neutral_trials':int(x['probabilityLeft'].eq(.5).sum()),'unknown_context_trials':int((~x['probabilityLeft'].isin([.2,.5,.8])).sum()),
        'counts':counts,'eligible':bool(eligible),'exclusion_counts_nonexclusive':{k:int(v.sum()) for k,v in reasons.items()}},runs,usable


def ibl(out):
    fixture=pd.read_csv(ROOT/'paper13/metadata/fixture.csv',dtype={'pid':str,'eid':str,'subject':str})
    if fixture.pid.duplicated().any():raise ValueError('Duplicate probe identity')
    if fixture.groupby('eid').subject.nunique().max()!=1:raise ValueError('Ambiguous session animal')
    clusters=pd.read_csv(ROOT/'paper13/metadata/clusters_metadata.csv.gz')
    if clusters[['pid','cluster_id']].duplicated().any():raise ValueError('Duplicate local unit identity')
    if not set(clusters.pid)<=set(fixture.pid):raise ValueError('Unregistered probe')
    atlas={int(x['id']):x['acronym'] for x in read(ROOT/'paper13/metadata/atlas.json')['msg']}
    clusters['region']=clusters.atlas_id.map(atlas).map(region)
    trials=pd.read_csv(ROOT/'paper13/metadata/trials_metadata.csv.gz',float_precision='round_trip')
    if not set(trials.eid)<=set(fixture.eid):raise ValueError('Unregistered trial session')
    summaries={};runrows=[];context_rows=[];trialmasks=[]
    for eid,x in trials.groupby('eid',sort=True):
        summary,runs,usable=session_blocks(x);summaries[eid]=summary
        runrows.extend(dict(eid=eid,**r) for r in runs)
        trialmasks.extend({'eid':eid,'trial_ordinal':j,'usable_primary_metadata':bool(u)} for j,u in enumerate(usable))
        for ctx,c in summary['counts'].items():context_rows.append(dict(eid=eid,context=ctx,session_metadata_eligible=summary['eligible'],chronological=summary['chronological'],**c))
    counts={}
    for pid,x in clusters.groupby('pid',sort=False):
        for r in REGIONS:
            mask=x.region.notna() if r=='mPFC_composite' else x.region.eq(r)
            counts[(pid,r)]=(int(mask.sum()),int((mask&x.label.eq(1)).sum()))
    populations=[]
    for f in fixture.itertuples():
        s=summaries.get(f.eid)
        if s is None:raise ValueError('Missing probe-session trial metadata')
        for r in REGIONS:
            raw,good=counts.get((f.pid,r),(0,0))
            reason=[]
            if good<10:reason.append('fewer_than10_provider_good_units')
            if not s['chronological']:reason.append('nonmonotone_trial_clock')
            if not s['eligible']:reason.append('insufficient_registered_context_half_or_run_coverage')
            minimum=min(z[k] for z in s['counts'].values() for k in ['calibration_trials','scoring_trials'])
            populations.append({'mouse':f.subject,'lab':f.lab,'eid':f.eid,'pid':f.pid,'region':r,
                'anatomical_units':raw,'provider_good_units':good,'metadata_eligible':not reason,
                'minimum_context_half_trials':minimum,'exclusion_reasons':';'.join(reason),
                'raw_ephys_support_verified':False,'physiological_QC_verified':False})
    pop=pd.DataFrame(populations)
    coverage=pop.merge(pd.DataFrame(context_rows),on='eid',validate='many_to_many')
    ranking=pop.sort_values(['metadata_eligible','provider_good_units','minimum_context_half_trials','eid','pid'],ascending=[False,False,False,True,True])
    selected=ranking.drop_duplicates(['mouse','region'])
    mousecov=selected.merge(pd.DataFrame(context_rows),on='eid',validate='many_to_many')
    summaries_by_region={}
    for r in REGIONS:
        sub=pop[pop.region==r];chosen=selected[selected.region==r]
        summaries_by_region[r]={'anatomical_mice':int(sub[sub.anatomical_units>0].mouse.nunique()),
            'mice_with10_provider_good_units':int(sub[sub.provider_good_units>=10].mouse.nunique()),
            'metadata_eligible_mice':int(chosen[chosen.metadata_eligible].mouse.nunique()),
            'selected_eligible_mice':sorted(chosen[chosen.metadata_eligible].mouse.tolist()),
            'single_probe_good_units_distribution':{str(int(k)):int(v) for k,v in sub.provider_good_units.value_counts().sort_index().items()}}
    table(out/'IBL_probe_region_context.csv.gz',coverage)
    table(out/'Context_Mouse_Region_Coverage.csv',mousecov)
    table(out/'IBL_populations.csv',pop)
    table(out/'IBL_selected_populations.csv',selected)
    table(out/'IBL_blocks.csv',pd.DataFrame(runrows))
    table(out/'IBL_trial_metadata_masks.csv.gz',pd.DataFrame(trialmasks))
    unitrows=clusters[clusters.region.notna()].merge(fixture[['pid','eid','subject','lab']],on=['pid','eid'],validate='many_to_one')
    table(out/'IBL_target_unit_metadata.csv.gz',unitrows)
    report={'independent_mice':int(fixture.subject.nunique()),'sessions':int(fixture.eid.nunique()),'probes':len(fixture),
        'all_cluster_metadata_rows':len(clusters),'provider_good_global':int(clusters.label.eq(1).sum()),'task_trials':len(trials),
        'regions':summaries_by_region,'source':'2024_Q2_IBL_et_al_BWM','unit_admission':'Provider good only; future training-only physiology unconfirmed',
        'session_metadata_summary':summaries,'no_neural_values_read':True,'new_fits_or_scores':0}
    write(out/'IBL_AUDIT.json',report)
    return report


def ki(out):
    old=ROOT/'paper13_ki_feasibility1/results/review1'
    rec=pd.read_csv(old/'all_recording_identities.csv',dtype=str);rec=rec[rec.dandiset.str.zfill(6)=='001260'].copy()
    units=pd.read_csv(old/'all_unit_metadata.csv',dtype=str);units=units[units.dandiset.str.zfill(6)=='001260']
    rows=[]
    for f in rec.itertuples():
        u=units[units.recording_id==f.recording_id]
        for r in REGIONS:
            v=u[u.region.isin(REGIONS[:-1])] if r=='mPFC_composite' else u[u.region==r]
            for context in ['UNRESOLVED_WITHIN_TASK_A','UNRESOLVED_WITHIN_TASK_B']:
                rows.append({'mouse':f.mouse_id,'session':f.session_id,'probe':f.probe_id,'recording':f.recording_id,
                    'region':r,'source_task_stratum':f.task,'context':context,'anatomical_units':int(v.unit_id.nunique()),
                    'provider_good_units':None,'context_observations':None,'paired_context_verified':False,
                    'quality_admission':'UNKNOWN_NOT_PASS','primary_metadata_admitted':False})
    tables=pd.DataFrame(rows);table(out/'KI_Mouse_Region_Context.csv',tables)
    task={name:{'mice':int(x.mouse_id.nunique()),'sessions':int(x.session_id.nunique()),'probes':len(x)} for name,x in rec.groupby('task')}
    paired=[]
    for a,b in itertools.combinations(sorted(task),2):
        both=sorted(set(rec[rec.task==a].mouse_id)&set(rec[rec.task==b].mouse_id))
        paired.append({'task_A':a,'task_B':b,'shared_mice':len(both),'mouse_ids':';'.join(both),'same_population_context_comparison_verified':False})
    table(out/'KI_cross_task_animal_overlap.csv',pd.DataFrame(paired))
    report={'release':'001260/0.250911.0744','independent_mice':int(rec.mouse_id.nunique()),'sessions':int(rec.session_id.nunique()),'probes':len(rec),
        'raw_subject_labels':int(rec.raw_subject_id.nunique()),'task_strata':task,'within_Context_task_animal_upper_bound':task.get('Context',{}).get('mice',0),
        'context_quality_or_new_neural_QC_verified':False,'cross_session_tasks_interchangeable':False,
        'candidate_verdict':'INCONCLUSIVE_METADATA','Context_task_route_verdict':'DATA_INSUFFICIENT_FOR_8_PLUS_8',
        'other_routes':'Stimulus-history/task-phase within each source stratum may exist; no individual task stratum supplies16animals. A heterogeneous cross-task design is not the registered primary.',
        '000473':'EXPOSED_P13_HISTORY_NOT_FRESH_CONFIRMATION','new_neural_access':False}
    write(out/'KI_AUDIT.json',report)
    return report


def run(out=None):
    verify_inputs();out=Path(out) if out else P/'results';out.mkdir(parents=True,exist_ok=True)
    a=ibl(out);k=ki(out)
    upper=a['regions']['mPFC_composite']['metadata_eligible_mice']
    result={'mission':'P14-CONTEXT-DYNAMICS-DATA-FEASIBILITY','registered_primary':'IBL single-probe ACAd/ACAv/PL/ILA composite, priorLeft.2vs.8',
        'primary_metadata_mouse_upper_bound':upper,'minimum_total_mice':16,'8_plus_8_metadata_capacity':upper>=16,
        'physiologically_admitted_mice':None,'actual_final_allocation':None,'M1_activated':False,
        'additional_dataset_screen_required':upper<16,'scientific_final_verdict':'PENDING_COVARIATE_AND_SOURCE_REVIEW',
        'neural_arrays_accessed':0,'fits':0,'predictive_scores':0,'KI_Context_task_upper_bound':k['within_Context_task_animal_upper_bound']}
    write(out/'M0_PRELIMINARY.json',result);verify_inputs()
    return result


if __name__=='__main__':print(json.dumps(run()))
