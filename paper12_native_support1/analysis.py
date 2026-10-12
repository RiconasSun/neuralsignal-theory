"""Saved evidence only: complete native-support/anatomy/trial denominator."""
import csv
import json
from collections import Counter,defaultdict
from datetime import datetime
from pathlib import Path
import numpy as np
from register import HERE,ROOT,verify,sha
from storage import load,logical_paths

def region(label):
    if label in ('CA1','CA3','DG'):return label
    if label in ('DG-mo','DG-po','DG-sg'):return 'DG'
    return None
def old_table(name):return json.loads((ROOT/'paper12/metadata'/('allen_'+name+'.receipt')).read_text())['msg']
def number(value):
    try:x=float(value);return x if np.isfinite(x) else None
    except (TypeError,ValueError):return None
def write_csv(path,rows):
    with path.open('w',newline='',encoding='utf-8') as out:
        writer=csv.DictWriter(out,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)

def excluded(table):
    starts=table.get('start_time',[]);stops=table.get('stop_time',[])
    tags=table.get('tags',[]);indices=table.get('tags_index',[])
    if not(len(starts)==len(stops)==len(indices)):raise RuntimeError('Invalid interval tag cardinality')
    rows=[];offset=0
    for start,stop,end in zip(starts,stops,indices):
        end=int(end);labels=tags[offset:end];offset=end
        if not np.isfinite(start) or not np.isfinite(stop) or stop<=start:raise RuntimeError('Invalid known exclusion bounds')
        rows.append({'start':start,'stop':stop,'tags':labels})
    if offset!=len(tags):raise RuntimeError('Unconsumed exclusion tags')
    return rows

def affected(tags,pid,name,probe_registry=None):
    if 'EcephysProbe' in tags:
        registry=probe_registry or {str(pid):name}
        tokens=[x for x in tags if x!='EcephysProbe']
        matches={key for key,value in registry.items() if key in tokens or value in tokens}
        known=set(registry)|set(registry.values())
        if len(matches)!=1 or any(x not in known for x in tokens):return None
        return str(pid) in matches
    if any(x in tags for x in ('EcephysSession','Stimulus','stimulus','all_probes')):return True
    return None

def presentation_trials(table,kind):
    a=np.asarray(table.get('start_time',[]),float);b=np.asarray(table.get('stop_time',[]),float)
    if len(a)!=len(b):raise RuntimeError('Presentation boundary mismatch')
    if not np.all(np.isfinite(a)) or not np.all(np.isfinite(b)) or np.any(b<=a):raise RuntimeError('Undefined presentation intervals')
    if kind=='grating':
        if np.any(a[1:]<b[:-1]-.001):raise RuntimeError('Grating presentation intervals overlap or reorder')
        fields=('orientation','contrast','temporal_frequency')
        if any(len(table.get(f,[]))!=len(a) for f in fields):raise RuntimeError('Missing grating condition metadata')
        rows=[]
        for i,(start,stop) in enumerate(zip(a,b)):
            condition=tuple(number(table[f][i]) for f in fields)
            if None in condition:raise RuntimeError('Undefined grating condition')
            rows.append({'start':float(start),'stop':float(stop),'condition':str(condition),'frames':None})
        return rows,{'presentation_rows':len(a),'genuine_trials':len(rows),'conditions':dict(Counter(r['condition'] for r in rows)),
                     'unit_of_repetition':'one grating presentation; repetitions are not independent animals'}
    frames=np.asarray(table.get('frame',[]),float);blocks=np.asarray(table.get('stimulus_block',[]),float)
    if len(frames)!=len(a) or len(blocks)!=len(a) or not np.all(np.isfinite(frames)) or not np.all(np.isfinite(blocks)):
        raise RuntimeError('Missing movie frame/block metadata')
    cuts=np.r_[0,np.where((np.diff(frames)!=1)|(np.diff(blocks)!=0))[0]+1,len(a)]
    rows=[];incomplete=0
    expected=np.arange(900)
    for start,end in zip(cuts[:-1],cuts[1:]):
        if end-start!=900 or not np.array_equal(frames[start:end],expected):incomplete+=1;continue
        if np.any(a[start+1:end]<b[start:end-1]-.001):raise RuntimeError('Movie frame intervals overlap materially')
        rows.append({'start':float(a[start]),'stop':float(b[end-1]),'condition':'natural_movie_one_900_frames',
                     'frames':900,'block':float(blocks[start])})
    return rows,{'presentation_rows':len(a),'genuine_trials':len(rows),'incomplete_runs':incomplete,
                 'expected_frames_per_cycle':900,'unit_of_repetition':'one complete non-overlapping900frame movie cycle; not each frame'}

def native_clock_for_trial(probe,start,stop,invalid,probe_registry=None):
    if any(affected(r['tags'],probe['probe_id'],probe['name'],probe_registry) is None for r in invalid):return False
    for r in invalid:
        if affected(r['tags'],probe['probe_id'],probe['name'],probe_registry) and start<r['stop'] and stop>r['start']:return False
    return any(s['pass'] and start>=s['master_anchor_min_seconds'] and stop<=s['master_anchor_max_seconds']
               for s in probe.get('segments',[]))

def channel_distances(rows):
    positions=np.asarray([number(r['probe_vertical_position']) if number(r['probe_vertical_position']) is not None else np.nan for r in rows])
    labels=np.asarray([r['structure_acronym'] for r in rows],dtype=object)
    allowed=(labels[:,None]!=labels[None,:])&np.asarray([v is not None for v in labels])[None,:]
    allowed &= np.isfinite(positions)[:,None]&np.isfinite(positions)[None,:]
    distance=np.min(np.where(allowed,np.abs(positions[:,None]-positions[None,:]),np.inf),axis=1)
    return {r['id']:float(x) if np.isfinite(x) else None for r,x in zip(rows,distance)}

def main(output=None):
    verify();out=Path(output) if output else HERE/'results';out.mkdir(exist_ok=True,parents=True)
    sessions=old_table('sessions');probes=old_table('probes');units=old_table('units');original={r['id']:r for r in old_table('channels')}
    channels=[]
    for path in logical_paths(HERE/'metadata','channel_anatomy_page_*.receipt'):
        channels+=load(path)['msg']
    c={r['id']:r for r in channels}
    if len(c)!=len(channels) or set(c)!=set(original):raise RuntimeError('Anatomy full denominator mismatch')
    for cid,row in c.items():
        for field in ('ecephys_probe_id','structure_id','structure_acronym'):
            if row[field]!=original[cid][field]:raise RuntimeError('Anatomy label/identity drift')
    geometry=defaultdict(list)
    for r in channels:geometry[r['ecephys_probe_id']].append(r)
    distances={}
    for pid,rows in geometry.items():
        distances.update(channel_distances(rows))
    counts=defaultdict(Counter);sensitivity=defaultdict(lambda:defaultdict(Counter));anatomy_rows=[]
    for unit in units:
        ch=c[unit['ecephys_channel_id']];pid=ch['ecephys_probe_id'];label=region(ch['structure_acronym'])
        if not label:continue
        coordinates=[number(ch[f]) for f in ('anterior_posterior_ccf_coordinate','dorsal_ventral_ccf_coordinate','left_right_ccf_coordinate')]
        finite=all(x is not None for x in coordinates);distance=distances[ch['id']]
        counts[pid][label]+=1
        for cutoff in (0,20,40):
            if finite and (cutoff==0 or distance is not None and distance>cutoff):sensitivity[pid][cutoff][label]+=1
        anatomy_rows.append({'unit_id':unit['id'],'channel_id':ch['id'],'probe_id':pid,'subfield':label,
                             'finite_CCF_coordinates':finite,'nearest_other_channel_label_vertical_um':distance,
                             'independent_histology_confirmed':False})
    write_csv(out/'unit_anatomy_uncertainty.csv',anatomy_rows)
    probe_rows=[];session_rows=[];trial_summary=[];invalid_rows=[];trial_rows=[]
    eligible=Counter();curated=Counter();geometry_totals=Counter()
    for session in sorted(sessions,key=lambda r:r['id']):
        sid=session['id'];header_path=HERE/'metadata/native_headers'/(sid+'.json')
        digital_path=HERE/'results/digital_code2'/(sid+'.json')
        if not (header_path.exists() or Path(str(header_path)+'.gz').exists()) or not digital_path.exists():raise RuntimeError('Full audit denominator incomplete')
        header=load(header_path);digital=json.loads(digital_path.read_text())
        native=digital.get('master',{});invalid=excluded(header['tables'].get('invalid_times',{}))
        for r in invalid:invalid_rows.append({'session_id':sid,'start':r['start'],'stop':r['stop'],'tags':json.dumps(r['tags'])})
        ps=digital['probes'];types=Counter()
        registry={p['id']:p['name'] for p in probes if p['ecephys_session_id']==sid}
        if {p['probe_id']:p['name'] for p in ps}!=registry:raise RuntimeError('Frozen session probe identity mismatch')
        for p in ps:
            row={'session_id':sid,'probe_id':p['probe_id'],'probe_name':p['name'],'clock_diagnostic_pass':p['clock_pass'],
                 'segments':len(p.get('segments',[])),'failed_segments':sum(not s['pass'] for s in p.get('segments',[])),
                 'native_observation_certified':False,'continuity_certified':False,
                 'known_exclusions':sum(affected(r['tags'],p['probe_id'],p['name'],registry) is True for r in invalid),
                 'unknown_exclusion_tags':sum(affected(r['tags'],p['probe_id'],p['name'],registry) is None for r in invalid),
                 'api_sampling_rate_hz':p['api_sampling_rate_hz'],'conditional_serialized_duration_seconds':p.get('conditional_serialized_duration_seconds'),
                 '100ms_expected_nominal_samples':3000,'error':p.get('error',''),
                 **{label+'_candidate_units':counts[p['probe_id']][label] for label in ('CA1','DG','CA3')}}
            probe_rows.append(row)
            types.update(counts[p['probe_id']])
        potential=types['CA1']>=5 and types['DG']>=5
        fc=session['stimulus_name']=='functional_connectivity'
        if fc and potential:eligible['functional_connectivity_potential_mice']+=1
        epoch_mismatch=None
        if native.get('sync_metadata',{}).get('start_time') and '/session_start_time' in header:
            rawdate=datetime.fromisoformat(native['sync_metadata']['start_time']).date()
            nwbdate=datetime.fromisoformat(header['/session_start_time']).date()
            epoch_mismatch=rawdate!=nwbdate
        row={'session_id':sid,'mouse_id':session['specimen_id'],'protocol':session['stimulus_name'],
             'CA1_candidate_units':types['CA1'],'DG_candidate_units':types['DG'],'CA3_candidate_units':types['CA3'],
             'atlas_paired_potential':potential,'probe_count':len(ps),'clock_pass_probes':sum(p['clock_pass'] for p in ps),
             'known_invalid_intervals':len(invalid),'sync_NWB_calendar_date_disagree':epoch_mismatch,
             'native_observation_certified':False,'original_M0_pass':False,'header_error':header.get('error','')}
        for kind,name in [('grating','drifting_gratings_75_repeats_presentations' if fc else 'drifting_gratings_presentations'),
                          ('movie','natural_movie_one_more_repeats_presentations' if fc else 'natural_movie_one_presentations')]:
            if name not in header['tables']:
                row[kind+'_genuine_trials']=0;row[kind+'_clock_bracketed_paired_trials']=0;continue
            try:
                trials,summary=presentation_trials(header['tables'][name],kind)
            except Exception as exc:
                row[kind+'_genuine_trials']=0;row[kind+'_clock_bracketed_paired_trials']=0;row[kind+'_error']=str(exc);continue
            paired=0;paired_sensitivity=Counter()
            for i,trial in enumerate(trials):
                supported=Counter();sensitive=defaultdict(Counter)
                for p in ps:
                    if native_clock_for_trial(p,trial['start'],trial['stop'],invalid,registry):
                        supported.update(counts[p['probe_id']])
                        for cutoff in (0,20,40):sensitive[cutoff].update(sensitivity[p['probe_id']][cutoff])
                good=supported['CA1']>=5 and supported['DG']>=5
                paired+=good
                for cutoff in (0,20,40):paired_sensitivity[cutoff]+=sensitive[cutoff]['CA1']>=5 and sensitive[cutoff]['DG']>=5
                if fc:trial_rows.append({'session_id':sid,'kind':kind,'trial_index':i,'start':trial['start'],'stop':trial['stop'],
                                         'condition':trial['condition'],'CA1_clock_bracketed_potential_units':supported['CA1'],
                                         'DG_clock_bracketed_potential_units':supported['DG'],'paired_potential':good,
                                         'certified_neural_observation':False})
            row[kind+'_genuine_trials']=len(trials);row[kind+'_clock_bracketed_paired_trials']=paired
            for cutoff in (0,20,40):row[kind+'_geometry_'+str(cutoff)+'um_paired_trials']=paired_sensitivity[cutoff]
            trial_summary.append({'session_id':sid,'protocol':session['stimulus_name'],'kind':kind,**summary,
                                  'clock_bracketed_paired_trials':paired})
        if fc and row.get('grating_clock_bracketed_paired_trials',0)>0:curated['functional_connectivity_clock_bracketed_grating_mice']+=1
        if fc and row.get('movie_clock_bracketed_paired_trials',0)>0:curated['functional_connectivity_clock_bracketed_movie_mice']+=1
        session_rows.append(row)
    allfields=sorted({k for r in session_rows for k in r});session_rows=[{k:r.get(k) for k in allfields} for r in session_rows]
    write_csv(out/'session_evidence_matrix.csv',session_rows);write_csv(out/'probe_evidence_matrix.csv',probe_rows)
    if invalid_rows:write_csv(out/'known_invalid_intervals.csv',invalid_rows)
    if trial_rows:write_csv(out/'functional_connectivity_trial_inventory.csv',trial_rows)
    (out/'trial_conditions.json').write_text(json.dumps(trial_summary,indent=2,sort_keys=True))
    summary={'sessions':len(session_rows),'mice':len({r['mouse_id'] for r in session_rows}),'probes':len(probe_rows),
             'channels':len(channels),'unit_identities':len(units),'subfield_unit_identities':len(anatomy_rows),
             'whole_probe_clock_diagnostic_pass':sum(r['clock_diagnostic_pass'] for r in probe_rows),
             'known_invalid_intervals':len(invalid_rows),'calendar_epoch_disagreements':sum(r['sync_NWB_calendar_date_disagree'] is True for r in session_rows),
             'original_admitted_mice':0,**eligible,**curated,
             'finite_coordinate_subfield_units':sum(r['finite_CCF_coordinates'] for r in anatomy_rows),
             'within20um_other_channel_label_units':sum(r['nearest_other_channel_label_vertical_um'] is not None and r['nearest_other_channel_label_vertical_um']<=20 for r in anatomy_rows),
             'within40um_other_channel_label_units':sum(r['nearest_other_channel_label_vertical_um'] is not None and r['nearest_other_channel_label_vertical_um']<=40 for r in anatomy_rows),
             'independent_histological_unit_confirmations':0}
    (out/'summary.json').write_text(json.dumps(summary,indent=2,sort_keys=True))
    print(json.dumps(summary,indent=2));return summary

if __name__=='__main__':main()
