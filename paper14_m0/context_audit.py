"""Context and support accounting from saved metadata; no neural access."""
import json
from pathlib import Path
import numpy as np
import pandas as pd
from .audit import P,ROOT,REGIONS,read,write,table,region,session_blocks,verify_inputs


def flag(s,value=True):return s.astype('string').str.lower().eq(str(value).lower()).fillna(False).to_numpy(dtype=bool)


def supported(text,windows):
    try:
        intervals=np.asarray(json.loads(text),dtype=float)
        if intervals.ndim!=2 or intervals.shape[1]!=2 or len(intervals)==0 or not np.isfinite(intervals).all():return False
        if np.any(intervals[:,0]>=intervals[:,1]) or np.any(intervals[1:,0]<intervals[:-1,1]):return False
        w=np.asarray(windows,dtype=float)
        if w.ndim!=2 or w.shape[1]!=2 or len(w)==0 or not np.isfinite(w).all() or np.any(w[:,0]>=w[:,1]):return False
        return bool(((intervals[:,0,None]<=w[None,:,0])&(w[None,:,1]<=intervals[:,1,None])).any(axis=0).all())
    except (TypeError,ValueError,json.JSONDecodeError):return False


def dr_blocks(frame):
    x=frame.reset_index(drop=True).copy();N=len(x)
    required=['trial_index','stim_start_time','stim_stop_time','start_time','stop_time','block_index','rewarded_modality','is_opto']
    if any(k not in x for k in required):raise ValueError('Missing registered DR field')
    time=x.stim_start_time.to_numpy(float);idx=x.trial_index.to_numpy(float)
    chronological=bool(np.isfinite(idx).all() and np.all(np.diff(idx)>0) and np.all(np.diff(time[np.isfinite(time)])>0))
    a=x[['start_time','stim_start_time','stim_stop_time','stop_time']].to_numpy(float)
    timing=np.isfinite(a).all(axis=1)&(a[:,0]<=a[:,1])&(a[:,1]<a[:,2])&(a[:,2]<=a[:,3])&(a[:,1]+.5<=a[:,3])
    runs=[];positions=[];prior=None;current=None
    for j,row in x.iterrows():
        block=row.block_index;ctx=row.rewarded_modality
        key=(block,ctx)
        if current is None or key!=prior:
            current={'run':len(runs),'source_block':int(block) if pd.notna(block) else None,'context':str(ctx),'raw_trials':0,'indices':[]};runs.append(current)
        current['raw_trials']+=1;current['indices'].append(j);positions.append(current['raw_trials']-1);prior=key
    unique_blocks=[r['source_block'] for r in runs]
    block_identity=len(unique_blocks)==len(set(unique_blocks)) and None not in unique_blocks and all(r['context'] in ['aud','vis'] for r in runs)
    positions=np.asarray(positions);instruction=positions<5;opto=~flag(x.is_opto,False)
    valid=timing&~instruction&~opto
    cut=len(runs)//2;usable=np.zeros(N,dtype=bool);runrows=[]
    for r in runs:
        r['valid_trials']=int(valid[r['indices']].sum());r['qualifying']=r['valid_trials']>=15;r['half']='calibration' if r['run']<cut else 'scoring'
        if r['qualifying']:usable[r['indices']]=valid[r['indices']]
        runrows.append({k:v for k,v in r.items() if k!='indices'})
    counts={}
    for ctx in ['aud','vis']:
        these=[r for r in runs if r['context']==ctx];q=[r for r in these if r['qualifying']];m=x.rewarded_modality.eq(ctx).to_numpy()
        counts[ctx]={'raw_trials':int(m.sum()),'valid_trials':int((m&valid).sum()),'usable_trials':int((m&usable).sum()),
            'runs':len(these),'qualifying_runs':len(q),
            'calibration_trials':sum(r['valid_trials'] for r in q if r['half']=='calibration'),
            'scoring_trials':sum(r['valid_trials'] for r in q if r['half']=='scoring'),
            'order_quartiles':[int((m&usable&(np.minimum(np.arange(N)*4//max(N,1),3)==j)).sum()) for j in range(4)]}
    eligible=chronological and block_identity and all(z['qualifying_runs']>=2 and z['calibration_trials']>=60 and z['scoring_trials']>=60 for z in counts.values())
    report={'chronological':chronological,'source_block_identity':block_identity,'run_count':len(runs),
        'context_switches':sum(runs[j]['context']!=runs[j-1]['context'] for j in range(1,len(runs))),
        'counts':counts,'eligible':bool(eligible),'exclusion_counts_nonexclusive':{'invalid_timing':int((~timing).sum()),'scheduled_first5':int(instruction.sum()),'opto_or_unknown':int(opto.sum())},
        'instruction_flags_outside_first5':int((flag(x.is_instruction)&~instruction).sum()) if 'is_instruction' in x else None}
    return report,runrows,usable


def overlap(frame,contexts,column,values,*,source,mouse,session):
    rows=[];sets={}
    for ctx in contexts:
        x=frame[frame[column]==ctx];counts=x[values].fillna('MISSING').astype(str).value_counts();sets[ctx]=set(counts.index)-{'MISSING'}
        for value,n in counts.items():rows.append({'source':source,'mouse':mouse,'session':session,'context':ctx,'covariate':values,'value':value,'count':int(n),'total_context_trials':len(x)})
    return rows,sorted(sets[contexts[0]]&sets[contexts[1]])


def signed_contrast(left,right):
    """Preserve missing stimulus and collapse IEEE signed zero to one level."""
    values=np.where(pd.notna(left),-np.asarray(left,dtype=float),np.asarray(right,dtype=float))
    return np.where(values==0,0.,values)


def dr(out):
    catalog=pd.read_csv(P/'metadata/dr_assets__datacube_sessions.csv',dtype={'subject_id':str,'session_id':str})
    if catalog.session_id.duplicated().any():raise ValueError('DR catalog has duplicate sessions')
    if len(catalog)>500:raise ValueError('Registered DR session budget exceeded')
    sessions=pd.read_csv(P/'metadata/session_metadata.csv.gz',dtype={'subject_id':str,'session_id':str})
    trials=pd.read_csv(P/'metadata/trials_metadata.csv.gz',dtype={'subject_id':str,'session_id':str},float_precision='round_trip')
    units=pd.read_csv(P/'metadata/units_metadata.csv.gz',dtype={'subject_id':str,'session_id':str,'electrode_group_name':str,'structure':'string'},float_precision='round_trip')
    if units[['session_id','electrode_group_name','cluster_id']].duplicated().any():raise ValueError('DR same-probe cluster identity duplicated')
    mapping=dict(zip(catalog.session_id,catalog.subject_id))
    bad={name:sorted(set(df.loc[df.session_id.map(mapping).notna()&df.session_id.map(mapping).ne(df.subject_id),'session_id'])) for name,df in [('session',sessions),('trials',trials),('units',units)]}
    if any(bad.values()):raise ValueError('DR catalog/table animal identity conflict')
    stratum=[]
    for name,x in catalog.groupby('session_type',dropna=False):
        good=x[flag(x.is_behavior_pass)]
        stratum.append({'session_type':'UNSPECIFIED' if pd.isna(name) else str(name),'all_sessions':len(x),'all_mice':int(x.subject_id.nunique()),'behavior_pass_sessions':len(good),'behavior_pass_mice':int(good.subject_id.nunique())})
    primary=catalog[catalog.session_type.eq('brainwide')&flag(catalog.is_behavior_pass)]
    table(out/'DR_catalog.csv',catalog);table(out/'DR_stratum_denominators.csv',pd.DataFrame(stratum))
    units['target_region']=units.structure.map(region);units['good']=flag(units.is_qc_pass)
    units['anatomy_coordinates_valid']=np.isfinite(units[['ccf_ap','ccf_dv','ccf_ml']].to_numpy(float)).all(axis=1)
    before=[]
    for (sid,probe),u in units[units.session_id.isin(catalog.session_id)].groupby(['session_id','electrode_group_name'],dropna=False):
        for r in REGIONS:
            m=u.target_region.notna() if r=='mPFC_composite' else u.target_region.eq(r).fillna(False)
            before.append({'mouse':mapping.get(sid),'session':sid,'probe':str(probe),'region':r,'raw_anatomical_units':int(m.sum()),
                'provider_good_units':int((m&u.good).sum()),'source_scope':'All pinned catalog sessions before behavior/context/support filters'})
    table(out/'DR_before_filter_populations.csv',pd.DataFrame(before))
    sessions_map={s:x for s,x in trials.groupby('session_id',sort=False)};summaries={};blocks=[];ctxrows=[];masks=[];populations=[];all_units=[]
    for entry in primary.itertuples():
        sid=entry.session_id;mouse=entry.subject_id
        if sid not in sessions_map or sid not in set(sessions.session_id):continue
        x=sessions_map[sid];summary,runs,usable=dr_blocks(x);summaries[sid]=summary
        blocks.extend(dict(session=sid,mouse=mouse,**r) for r in runs)
        masks.extend({'session':sid,'trial_index':int(x.iloc[j].trial_index),'usable_primary_metadata':bool(v)} for j,v in enumerate(usable))
        for ctx,c in summary['counts'].items():ctxrows.append(dict(session=sid,context=ctx,**c))
        windows=list(zip(x.loc[usable,'stim_start_time'].to_numpy(float),x.loc[usable,'stim_start_time'].to_numpy(float)+.5))
        u=units[units.session_id==sid].copy();target=u[u.target_region.notna()].copy()
        target['all_primary_windows_supported']=[supported(v,windows) if windows else False for v in target.obs_intervals]
        all_units.append(target)
        for probe,probeall in u.groupby('electrode_group_name',dropna=False):
            probe_target=target[target.electrode_group_name==probe]
            for r in REGIONS:
                v=probe_target if r=='mPFC_composite' else probe_target[probe_target.target_region==r]
                qualified=v.good&v.anatomy_coordinates_valid&v.all_primary_windows_supported
                reason=[]
                if int(qualified.sum())<10:reason.append('fewer_than10_good_anatomy_supported_units')
                if not summary['eligible']:reason.append('context_half_run_or_timing_failure')
                if pd.isna(probe):reason.append('missing_probe_identity')
                populations.append({'mouse':mouse,'session':sid,'probe':str(probe),'region':r,'raw_anatomical_units':len(v),
                    'provider_good_units':int(v.good.sum()),'qualified_metadata_units':int(qualified.sum()),
                    'source_drift_flag_false_among_good':int((v.good&~flag(v.is_not_drift)).sum()),
                    'minimum_context_half_trials':min(z[k] for z in summary['counts'].values() for k in ['calibration_trials','scoring_trials']),
                    'metadata_eligible':not reason,'exclusion_reasons':';'.join(reason),'physiological_QC_verified':False})
    pop=pd.DataFrame(populations)
    if pop.empty:raise ValueError('No source-compatible DR primary sessions')
    rank=pop.sort_values(['metadata_eligible','qualified_metadata_units','minimum_context_half_trials','session','probe'],ascending=[False,False,False,True,True])
    chosen=rank.drop_duplicates(['mouse','region']);coverage=pop.merge(pd.DataFrame(ctxrows),on='session',validate='many_to_many')
    selectedcov=chosen.merge(pd.DataFrame(ctxrows),on='session',validate='many_to_many')
    table(out/'DR_probe_region_context.csv.gz',coverage);table(out/'DR_Mouse_Region_Context.csv',selectedcov)
    table(out/'DR_populations.csv',pop);table(out/'DR_selected_populations.csv',chosen)
    table(out/'DR_blocks.csv',pd.DataFrame(blocks));table(out/'DR_trial_metadata_masks.csv.gz',pd.DataFrame(masks))
    if all_units:table(out/'DR_target_unit_metadata.csv.gz',pd.concat(all_units,ignore_index=True))
    nuisance=[];common=[]
    for entry in chosen[(chosen.region=='mPFC_composite')&chosen.metadata_eligible].itertuples():
        x=sessions_map[entry.session];_,_,usable=dr_blocks(x);x=x.loc[usable].copy()
        for name in ['stim_name','is_response','is_rewarded']:
            rows,shared=overlap(x,['aud','vis'],'rewarded_modality',name,source='DR',mouse=entry.mouse,session=entry.session)
            nuisance.extend(rows)
            common.append({'source':'DR','mouse':entry.mouse,'session':entry.session,'covariate':name,'common_values':';'.join(shared),'number_common_values':len(shared)})
    table(out/'DR_nuisance_overlap.csv',pd.DataFrame(nuisance));table(out/'DR_common_support.csv',pd.DataFrame(common))
    regions={}
    for r in REGIONS:
        sub=pop[pop.region==r];q=chosen[chosen.region==r]
        regions[r]={'anatomical_mice':int(sub[sub.raw_anatomical_units>0].mouse.nunique()),
            'mice_with10_provider_good_units':int(sub[sub.provider_good_units>=10].mouse.nunique()),
            'mice_with10_good_coordinate_supported_units':int(sub[sub.qualified_metadata_units>=10].mouse.nunique()),
            'metadata_eligible_mice':int(q[q.metadata_eligible].mouse.nunique()),
            'eligible_mouse_ids':sorted(q[q.metadata_eligible].mouse.tolist()),
            'single_probe_qualified_units_distribution':{str(int(k)):int(v) for k,v in sub.qualified_metadata_units.value_counts().sort_index().items()}}
    report={'source':'AIND DR v0.0.289; Git366809a4b2b3f39a7f36e054a4650dd79faadbe2',
        'catalog_mice':int(catalog.subject_id.nunique()),'catalog_sessions':len(catalog),'strata':stratum,
        'catalog_missing_subject_id_rows':int(catalog.subject_id.isna().sum()),
        'cached_session_metadata_mice':int(sessions.subject_id.nunique()),'cached_session_metadata_sessions':int(sessions.session_id.nunique()),
        'cached_sessions_outside_pinned_catalog':sorted(set(sessions.session_id)-set(catalog.session_id)),
        'before_behavior_raw_mPFC_anatomical_mice':int(pd.DataFrame(before).query("region=='mPFC_composite' and raw_anatomical_units>0").mouse.nunique()),
        'before_behavior_mPFC_mice_with10_provider_good_units':int(pd.DataFrame(before).query("region=='mPFC_composite' and provider_good_units>=10").mouse.nunique()),
        'primary_behavior_pass_mice':int(primary.subject_id.nunique()),'primary_behavior_pass_sessions':len(primary),
        'primary_sessions_with_trial_metadata':len(summaries),'primary_missing_session_or_trial_metadata':sorted(set(primary.session_id)-set(summaries)),
        'catalog_sessions_missing_units':sorted(set(primary.session_id)-set(units.session_id)),
        'cached_global_unit_metadata_rows':len(units),'regions':regions,'primary_probe_observations':int(pop[pop.region=='mPFC_composite'].shape[0]),
        'session_summaries':summaries,'physiologically_admitted_mice':None,
        'support_status':'Provider obs_intervals checked, not hardware packet completeness or training-only physiology',
        'movement_arousal_status':'Trial response/reward events measured; running/pupil sample availability and alignment not verified per candidate in M0',
        'source_data_license':'UNRESOLVED_FOR_EXACT_PUBLIC_SCRATCH_SNAPSHOT; do not inherit code/repository/other-bucket license',
        'new_neural_arrays_fits_scores':0,'M1_activated':False}
    write(out/'DR_AUDIT.json',report)
    return report


def ibl_overlap(out):
    old=pd.read_csv(ROOT/'paper13/metadata/trials_metadata.csv.gz',float_precision='round_trip')
    new=pd.read_csv(P/'metadata/IBL_trials_metadata.csv.gz',float_precision='round_trip')
    if old.eid.tolist()!=new.eid.tolist() or not np.array_equal(old.stimOn_times,new.stimOn_times,equal_nan=True):raise ValueError('Old/new IBL row identity differs')
    for col in ['contrastLeft','contrastRight','choice','feedbackType','rewardVolume']:old[col]=new[col]
    # Both sides NaN represent unavailable stimulus, not an invented zero-contrast.
    old['signed_contrast']=signed_contrast(old.contrastLeft,old.contrastRight)
    old['previous_choice']=old.groupby('eid',sort=False).choice.shift(1)
    old['previous_feedback']=old.groupby('eid',sort=False).feedbackType.shift(1)
    chosen=pd.read_csv(out/'IBL_selected_populations.csv');nuisance=[];common=[]
    for entry in chosen[(chosen.region=='mPFC_composite')&chosen.metadata_eligible].itertuples():
        x=old[old.eid==entry.eid];_,_,usable=session_blocks(x);x=x.loc[usable].copy()
        for name in ['signed_contrast','choice','previous_choice','previous_feedback']:
            rows,shared=overlap(x,[.2,.8],'probabilityLeft',name,source='IBL',mouse=entry.mouse,session=entry.eid)
            nuisance.extend(rows);common.append({'source':'IBL','mouse':entry.mouse,'session':entry.eid,'covariate':name,'common_values':';'.join(shared),'number_common_values':len(shared)})
    table(out/'IBL_nuisance_overlap.csv',pd.DataFrame(nuisance));table(out/'IBL_common_support.csv',pd.DataFrame(common))
    return {'metadata_rows_matched':len(old),'new_neural_access':False,'selected_mouse_profiles':int(chosen[(chosen.region=='mPFC_composite')&chosen.metadata_eligible].mouse.nunique())}


def run(out=None):
    out=Path(out) if out else P/'results';verify_inputs()
    d=dr(out);i=ibl_overlap(out);n=d['regions']['mPFC_composite']['metadata_eligible_mice']
    result={'candidate':'AIND_DYNAMIC_ROUTING','metadata_mouse_upper_bound':n,'capacity8plus8':n>=16,
        'critical_metadata_gaps':['Exact public scratch snapshot data license unresolved','Per-candidate continuous running/pupil coverage/alignment not established'],
        'source_status':'Snapshot ETags/decoded metadata hashes pinned; mutable scratch data not an immutable released neural cohort',
        'scientific_feasibility_verdict':'INCONCLUSIVE_METADATA','primary_recommended_for_neural_activation':False,
        'M1_activated':False,'additional_candidates_examined':2,'neural_arrays_or_fits_or_scores':0,'IBL_overlap':i}
    write(out/'M0_DECISION.json',result);verify_inputs();return result


if __name__=='__main__':print(json.dumps(run()))
