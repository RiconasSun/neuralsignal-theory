"""Saved metadata audit and proposed-QC contracts; never reads neural values."""
import argparse
from collections import Counter
import csv
import json
import math
from pathlib import Path
import re

P=Path(__file__).resolve().parent
ROOT=P.parent
OLD=ROOT/'paper13_ki_feasibility1'
M=OLD/'metadata'

def validate_intervals(rows):
    if not isinstance(rows,list):raise ValueError('Interval table required')
    for r in rows:
        if len(r)!=2 or any(isinstance(x,bool) or not isinstance(x,(int,float)) or not math.isfinite(x) for x in r) or r[1]<=r[0]:raise ValueError('Invalid interval')
    return rows

def saturation(v,band):
    paths=[f'/analysis/{band} saturation {k}/timestamps' for k in ['start','stop']]
    if any(k not in v for k in paths):raise ValueError('Missing saturation metadata is not no-events')
    a,b=[v[k] for k in paths]
    if a==[None] and b==[None]:return [],'provider_single_nan_sentinel'
    if len(a)!=len(b):raise ValueError('Saturation lengths disagree')
    rows=[[x,y] for x,y in zip(a,b)]
    # Zero-width recorded events still require a buffer; other nonfinite values fail.
    for x,y in rows:
        if not all(isinstance(z,(int,float)) and math.isfinite(z) for z in [x,y]) or y<x:raise ValueError('Corrupt saturation metadata')
    return rows,'explicit_intervals' if rows else 'explicit_empty'

def intersects(a,b,touch=False):return a[0]<=b[1] and b[0]<=a[1] if touch else a[0]<b[1] and b[0]<a[1]

def candidate_windows(v,schema):
    tones=[]
    for k,x in v.items():
        if re.fullmatch(r'/stimulus/presentation/[^/]+/timestamps',k) and re.search(r'(?:\d+(?:\.\d+)?khz|puretone)',k,re.I):tones+=x
    if any(not isinstance(t,(int,float)) or not math.isfinite(t) for t in tones):raise ValueError('Invalid tone timestamps')
    tones=sorted(set(tones));eps=[[t-3,t] for t in tones]
    clock=next(x for x in schema if x['path']=='/processing/ecephys/LFP/ElectricalSeries/starting_time')
    shape=next(x for x in schema if x['path']=='/processing/ecephys/LFP/ElectricalSeries/data')['shape']
    start=v[clock['path']];rate=clock['attrs']['rate']
    if not math.isfinite(start) or not math.isfinite(rate) or rate<=0 or shape[0]<=0:raise ValueError('Recording support invalid')
    stop=start+shape[0]/rate
    keep=[];excluded=Counter()
    for i,e in enumerate(eps):
        if e[0]<start or e[1]>stop:excluded['support']+=1
        elif any(intersects(e,eps[j]) for j in [i-1,i+1] if 0<=j<len(eps)):excluded['overlap']+=1
        else:keep.append(e)
    return keep,dict(excluded),[start,stop],len(tones)

def future_qc_contract():
    return {'status':'PROPOSED_ONLY_NOT_ACTIVATED','historical_columns_used_for_admission':False,
            'partition':'training epochs only, after mouse and epoch assignments frozen',
            'finite_strictly_increasing_times':True,'refractory_threshold_seconds':0.0015,
            'refractory_fraction_max':0.01,'definition':'sum adjacent within-epoch ISIs<1.5ms / number of adjacent within-epoch ISIs; no ISI across gaps; this is NOT the published contamination/ISI-violation ratio',
            'minimum_training_spikes':50,'minimum_adjacent_ISIs':30,'minimum_occupied_training_epochs':12,
            'rate_hz_min':0.1,'rate_hz_max':100.0,'rate_denominator':'all valid training epoch exposure, including zero-spike epochs',
            'waveform_requirement':'No new waveform reading or waveform-good certification; target is prospectively screened curated-release units, not certified isolated single neurons',
            'selection':'first8 passing PL units sorted by numeric NWB unit_id, single probe; no replacement after B/D scores',
            'limitation':'Activity/refractory screen is an operational QC, not purity or sorting certification; training-only screen cannot undo full-record retrospective provider sorting.',
            'mouse_gate':'8eligible simultaneous units AND120valid epochs; at least8development+8final mice; stop without replacements if allocation loses this minimum'}

def run(out):
    prev=json.loads((OLD/'results/review1/audit.json').read_text())
    previous={r['recording_id']:r for r in prev['all_records'] if r['dandiset']=='000473'}
    active=json.loads((M/'provider_active_intervals.json').read_text())['selected_members']
    manual=json.loads((P/'metadata/manual_bad_intervals.json').read_text())
    validate_intervals(manual['intervals'])
    headers=[json.loads(f.read_text()) for f in sorted((M/'headers').glob('000473_*.json'))]
    if len(headers)!=25 or len(previous)!=25:raise ValueError('Not complete25')
    rows=[];epochs=[];allq=[]
    for h in headers:
        if h['spike_values_read']:raise ValueError('Forbidden neural-value access')
        v=h['decoded_values'];rec=v['/general/session_id'];old=previous[rec]
        if rec!=v['/general/subject/subject_id']+'_'+old['session_id'].split('_')[-1]+'-'+old['probe_id']:raise ValueError('Identity conflict')
        ids=v['/units/id'];electrodes=v['/units/electrodes'];loc=v['/general/extracellular_ephys/electrodes/location']
        if len(ids)!=len(electrodes) or len(ids)!=len(set(ids)):raise ValueError('Unit mapping invalid')
        npl=sum(bool(re.fullmatch(r'PL(?:1|2|3|2/3|4|5|6|6a|6b)?',loc[e])) for e in electrodes)
        if npl!=old['region_counts'].get('PL',0):raise ValueError('Independent PL recount disagrees')
        q=v['/units/quality']
        if len(q)!=len(ids) or any(len(x)!=2 or any(not isinstance(y,(int,float)) or not math.isfinite(y) for y in x) for x in q):raise ValueError('Quality metadata shape')
        allq+=q
        ep,pre_ex,support,tones=candidate_windows(v,h['schema'])
        spike,spstatus=saturation(v,'spike');lfp,lfstatus=saturation(v,'LFP')
        manualrows=manual['intervals'] if rec=='147463_20191113-probe0' else []
        candidates=[x for x in active if x['attributes'].get('recid')==rec]
        chosen=[x for x in candidates if x['path'].endswith('STATEactive__all.h5')]
        if not chosen:chosen=[x for x in candidates if x['path'].endswith('STATEactive.h5')]
        if len(chosen)!=1:raise ValueError('Ambiguous active member')
        act=chosen[0];validate_intervals(act['tints'])
        source_rows=old['source_table_matches'];quiet={r.get('quietdet_src') for r in source_rows}
        if len(quiet)!=1:raise ValueError('Ambiguous state source table')
        histbasic=old['epoch_audit']['basic_epochs']
        # Original basic rule separately reconstructed, including source-backed NaN-empty handling.
        sb=[[a-1,b+1] for a,b in spike];lb=[[a-1,b+1] for a,b in lfp]
        reconstructed=[e for e in ep if not any(intersects(e,b) for b in sb)]
        if reconstructed!=histbasic:raise ValueError('Historical basic epoch identity changed')
        kept=[];rem=Counter();nonpure=0
        other=[(k,ts) for k,ts in v.items() if re.fullmatch(r'/stimulus/presentation/[^/]+/timestamps',k) and not re.search(r'(?:\d+(?:\.\d+)?khz|puretone)',k,re.I)]
        for e in histbasic:
            reasons=[]
            if any(intersects(e,b,touch=True) for b in manualrows):reasons.append('manual')
            if any(intersects(e,b,touch=True) for b in lb):reasons.append('LFP_plusminus1s')
            # Known other task events are counted, not silently removed as if movement were noise.
            events=[k for k,ts in other if any(isinstance(t,(int,float)) and e[0]<=t<e[1] for t in ts)]
            nonpure+=bool(events)
            match=any(max(abs(e[i]-a[i]) for i in [0,1])<=1e-6 for a in act['tints'])
            for x in reasons:rem[x]+=1
            if not reasons:kept.append(e)
            epochs.append({'recording_id':rec,'start':e[0],'stop':e[1],'historical_basic':True,'refined_A':not reasons,'provider_active_match':match,'excluded_by':';'.join(reasons),'other_event_series':';'.join(events)})
        b=sum(any(max(abs(e[i]-a[i]) for i in [0,1])<=1e-6 for a in act['tints']) for e in histbasic)
        bref=sum(any(max(abs(e[i]-a[i]) for i in [0,1])<=1e-6 for a in act['tints']) for e in kept)
        if b!=old['provider_active_puretone_matches']:raise ValueError('Historical active count changed')
        rows.append({'mouse_id':old['mouse_id'],'raw_subject_id':old['raw_subject_id'],'session_id':old['session_id'],'recording_id':rec,'probe_id':old['probe_id'],
                     'asset_id':h['asset']['asset_id'],'PL_raw_units':npl,'pure_tone_events':tones,'historical_basic':len(histbasic),'historical_active':b,
                     'proposed_A_after_known_masks':len(kept),'active_after_same_masks':bref,'A_potential':npl>=8 and len(kept)>=120,'B_potential':npl>=8 and bref>=120,
                     'spike_saturation_status':spstatus,'spike_saturation_intervals':len(spike),'LFP_saturation_status':lfstatus,'LFP_saturation_intervals':len(lfp),
                     'manual_intervals':len(manualrows),'manual_excluded':rem['manual'],'LFP_excluded':rem['LFP_plusminus1s'],'basic_with_other_task_events':nonpure,
                     'quietdet_src':next(iter(quiet)),'active_creator':act['attributes'].get('githash'),'active_path':act['path'],
                     'support_start_seconds':support[0],'support_stop_seconds':support[1],'initial_support_or_overlap_exclusions':json.dumps(pre_ex,sort_keys=True),
                     'quality_admitted':False,'awake_certified':False,'eligible_mouse_certified':False})
    rows.sort(key=lambda x:x['mouse_id'])
    if len({r['mouse_id'] for r in rows})!=25:raise ValueError('Independent mouse denominator')
    bounds={'historical_raw_PL':sum(r['PL_raw_units']>=8 for r in rows),'historical_basic120':sum(r['PL_raw_units']>=8 and r['historical_basic']>=120 for r in rows),
            'historical_active120':sum(r['PL_raw_units']>=8 and r['historical_active']>=120 for r in rows),
            'refined_A120':sum(r['A_potential'] for r in rows),'refined_B120':sum(r['B_potential'] for r in rows),'actual_QC_eligible_mice':0}
    if [bounds[k] for k in ['historical_raw_PL','historical_basic120','historical_active120']]!=[20,20,15]:raise ValueError('Frozen historical bound mismatch')
    outcome='PROTOCOL_READY_PENDING_NEURAL_QC' if bounds['refined_A120']>=16 else 'DATA_INSUFFICIENT'
    result={'mission':'P13-KI-PL-QUALITY-EPOCH-RESOLUTION-1','scientific_readiness':outcome,'bounds':bounds,
            'records':rows,'quality_metadata':{'units':len(allq),'col0_min':min(x[0] for x in allq),'col0_max':max(x[0] for x in allq),'col0_integer_valued':all(x[0]==int(x[0]) for x in allq),'col1_min':min(x[1] for x in allq),'col1_max':max(x[1] for x in allq),'exact_formula_units_and_exporter':'UNRESOLVED','no_ratio_inferred':True},
            'future_QC':future_qc_contract(),'spike_array_reads':0,'model_fits':0,'M1_M7_started':False,'protocol_activated':False}
    out.mkdir(parents=True,exist_ok=False)
    for name,value in [('audit.json',result),('future_qc.json',future_qc_contract())]:
        (out/name).write_text(json.dumps(value,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    for name,data in [('animal_disposition.csv',rows),('epoch_disposition.csv',epochs)]:
        with (out/name).open('x',encoding='utf8',newline='') as f:
            w=csv.DictWriter(f,fieldnames=list(data[0]));w.writeheader();w.writerows(data)
    print(json.dumps({'readiness':outcome,'bounds':bounds,'saturation':dict(Counter(x['spike_saturation_status'] for x in rows))}))

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);run(ap.parse_args().output)
