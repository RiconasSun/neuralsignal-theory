"""Saved metadata-only identity, population and epoch audit. Never fits models."""
import argparse
from collections import Counter,defaultdict
import csv
import json
import math
import re
from pathlib import Path
from zipfile import ZipFile
import xml.etree.ElementTree as ET
from transport import P,META,POLICY


def record_table():
    """Read only public recording/task/QC metadata columns, using stdlib XML."""
    ns={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
    output=defaultdict(list)
    with ZipFile(META/'code__python__config__datatables__allrecs_allprobes.xlsx') as z:
        strings=[''.join(x.itertext()) for x in ET.fromstring(z.read('xl/sharedStrings.xml'))]
        for name in z.namelist():
            if not re.fullmatch(r'xl/worksheets/sheet\d+\.xml',name):continue
            rows=ET.fromstring(z.read(name)).findall('m:sheetData/m:row',ns)
            headers={}
            for i,row in enumerate(rows):
                values={}
                for c in row:
                    col=re.sub(r'\d+','',c.attrib['r']);v=c.find('m:v',ns)
                    value=v.text if v is not None else ''
                    if c.attrib.get('t')=='s' and value:value=strings[int(value)]
                    if i==0:headers[col]=value
                    elif col in headers and headers[col] in {'recid','usable_gen','quietdet_src','quietdet_quality','use_quiet','exptype','datasetlab','lickdet_src','lickdet_done','lickdet_quality','offdet_src','offdet_q'}:
                        values[headers[col]]=value
                if i and re.fullmatch(r'.+_\d{8}-probe\d+',values.get('recid','')):
                    output[values['recid']].append({'sheet':name,**values})
    return dict(output)


def identity(v):
    raw=v.get('/general/subject/subject_id')
    recid=v.get('/general/session_id') or v.get('/identifier')
    match=re.fullmatch(r'(.+)_(\d{8})-(probe\d+)',recid or '')
    if not raw or not match:raise ValueError('Unresolved subject/session/probe identity')
    animal,date,probe=match.groups()
    compatible=raw==animal or bool(re.fullmatch(re.escape(animal)+r'[_-]\d+',raw))
    if not compatible:raise ValueError('Conflicting subject and original recording identity')
    return {'mouse_id':animal,'raw_subject_id':raw,'session_id':animal+'_'+date,'recording_id':recid,'probe_id':probe,
            'alias':raw!=animal,'identity_basis':'original recording animal/date/probe plus compatible subject; public recid table corroboration required'}


def region(label):
    for r in POLICY['regions']:
        if re.fullmatch(re.escape(r)+r'(?:1|2|3|2/3|4|5|6|6a|6b)?',label or ''):return r
    return None


def interval_valid(pair):
    return len(pair)==2 and all(isinstance(x,(int,float)) and math.isfinite(x) for x in pair) and pair[1]>pair[0]


def overlapping(a,b):return a[0]<b[1] and b[0]<a[1]


def basic_epochs(v,structure):
    tones=[]
    for path,values in v.items():
        if re.fullmatch(r'/stimulus/presentation/[^/]+/timestamps',path) and re.search(r'(?:\d+(?:\.\d+)?khz|puretone)',path,re.I):
            tones.extend(values)
    finite=sorted({float(t) for t in tones if isinstance(t,(int,float)) and math.isfinite(t)})
    epochs=[[t-3.,t] for t in finite]
    start=v.get('/processing/ecephys/LFP/ElectricalSeries/starting_time')
    data=next((x for x in structure if x['path']=='/processing/ecephys/LFP/ElectricalSeries/data'),None)
    clock=next((x for x in structure if x['path']=='/processing/ecephys/LFP/ElectricalSeries/starting_time'),None)
    rate=clock.get('attrs',{}).get('rate') if clock else None
    stop=start+data['shape'][0]/rate if data and isinstance(start,(int,float)) and isinstance(rate,(int,float)) and rate>0 else None
    sat1=v.get('/analysis/spike saturation start/timestamps',[])
    sat2=v.get('/analysis/spike saturation stop/timestamps',[])
    saturation=[[a-1.,b+1.] for a,b in zip(sat1,sat2) if isinstance(a,(int,float)) and isinstance(b,(int,float)) and b>=a]
    saturation_complete=all(k in v for k in ['/analysis/spike saturation start/timestamps','/analysis/spike saturation stop/timestamps']) and len(sat1)==len(sat2) and all(x is not None for x in sat1+sat2)
    kept=[];excluded=Counter()
    for i,ep in enumerate(epochs):
        if start is None or stop is None:excluded['recording_clock_unknown']+=1;continue
        if ep[0]<start or ep[1]>stop:excluded['outside_recording_header_support']+=1;continue
        if (i and overlapping(ep,epochs[i-1])) or (i+1<len(epochs) and overlapping(ep,epochs[i+1])):
            excluded['overlap']+=1;continue
        if any(overlapping(ep,sat) for sat in saturation):excluded['saturation_plusminus1s']+=1;continue
        kept.append(ep)
    return {'pure_tone_events':len(finite),'deduplicated_events':len(tones)-len(finite),'basic_epochs':kept,
            'excluded':dict(excluded),'recording_header_start':start,'recording_header_stop':stop,
            'rate':rate,'saturation_complete':saturation_complete,'sleep_lick_exclusions_complete':False,
            'note':'These are upper bounds before provider active-state/lick/manual masks and quality admission. No raw LFP or spikes read.'}


def interval_members():
    path=META/'provider_active_intervals.json'
    if not path.exists():return {}
    rows=json.loads(path.read_text())['selected_members'];result=defaultdict(list)
    for row in rows:
        recid=row.get('attributes',{}).get('recid')
        if recid:result[recid].append(row)
    return dict(result)


def write_csv(path,rows):
    with path.open('x',encoding='utf8',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)


def run(destination):
    table=record_table();provider_intervals=interval_members()
    files=sorted((META/'headers').glob('*.json'))
    headers=[json.loads(f.read_text()) for f in files]
    expected=sum(json.loads((META/(ds['id']+'_assets_00.json')).read_text())['count'] for ds in POLICY['datasets'])
    if len(headers)!=expected:raise ValueError(f'Incomplete headers: {len(headers)}/{expected}')
    units=[];records=[];all_seen=set();aliases=[];epochrows=[]
    for h in headers:
        a=h['asset'];v=h['decoded_values'];ident=identity(v)
        if a['asset_id'] in all_seen:raise ValueError('Duplicate asset')
        all_seen.add(a['asset_id'])
        source_rows=table.get(ident['recording_id'],[])
        if ident['alias']:
            if not source_rows:raise ValueError('Subject alias lacks public original recid corroboration')
            aliases.append({'asset_id':a['asset_id'],**ident,'source_table_records':source_rows})
        taskset={x.get('exptype','').strip() for x in source_rows if x.get('exptype','').strip()}
        task=next(iter(taskset)) if len(taskset)==1 else 'UNKNOWN'
        description=(v.get('/general/experiment_description') or v.get('/session_description') or '').lower()
        if task=='UNKNOWN':
            if 'passive listening' in description:task='Passive'
            elif 'aversive' in description:task='Aversion'
        if task=='Passive' and 'aversive' in description:raise ValueError('Task source conflict')
        ids=v.get('/units/id',[]);electrodes=v.get('/units/electrodes',[])
        indexes=v.get('/units/electrodes_index');locs=v.get('/general/extracellular_ephys/electrodes/location',[])
        groups=v.get('/general/extracellular_ephys/electrodes/group_name',[])
        q=v.get('/units/quality',[])
        if len(ids)!=len(set(ids)) or (not indexes and len(ids)!=len(electrodes)) or (indexes and len(indexes)!=len(ids)):raise ValueError('Invalid unit identity/electrode mapping')
        counts=Counter();unknown=Counter()
        for i,uid in enumerate(ids):
            ei=electrodes[indexes[i-1] if i else 0:indexes[i]] if indexes else [electrodes[i]]
            if not ei or any(not isinstance(k,int) or k<0 or k>=len(locs) for k in ei):raise ValueError('Electrode row index out of range')
            labels={locs[k] for k in ei};reg={region(label) for label in labels}
            r=next(iter(reg)) if len(reg)==1 else None
            if r:counts[r]+=1
            else:unknown['|'.join(sorted(labels))]+=1
            units.append({'dandiset':a['dandiset'],'version':a['version'],'asset_id':a['asset_id'],**ident,'task':task,'unit_id':uid,
                          'electrode_rows':json.dumps(ei),'provider_anatomical_labels':'|'.join(sorted(labels)),
                          'provider_groups':'|'.join(sorted({groups[k] for k in ei})) if groups else '',
                          'region':r or 'OTHER_OR_AMBIGUOUS','quality_summary':json.dumps(q[i]) if len(q)==len(ids) else 'MISSING',
                          'quality_admitted':False})
        ep=basic_epochs(v,h['schema']);active=provider_intervals.get(ident['recording_id'],[])
        # Match documented active intervals to actual pure-tone endpoints; never
        # treat absent preprocessing members as empty exclusions.
        selected=[r for r in active if r['path'].endswith('STATEactive__all.h5')]
        if not selected:selected=[r for r in active if r['path'].endswith('STATEactive.h5')]
        active_tints=selected[0]['tints'] if len(selected)==1 else []
        valid_tints=[x for x in active_tints if interval_valid(x)]
        matches=[x for x in ep['basic_epochs'] if any(abs(x[0]-t[0])<=1e-6 and abs(x[1]-t[1])<=1e-6 for t in valid_tints)]
        for j,x in enumerate(ep['basic_epochs']):epochrows.append({'asset_id':a['asset_id'],'dandiset':a['dandiset'],**ident,'task':task,'epoch_index':j,'start':x[0],'stop':x[1],'provider_active_match':x in matches,'fully_admitted':False})
        rec={'dandiset':a['dandiset'],'version':a['version'],'asset_id':a['asset_id'],'asset_path':a['path'],**ident,'task':task,
             'units':len(ids),'region_counts':dict(counts),'other_labels':dict(unknown),'quality_present':len(q)==len(ids),
             'quality_semantics':'NWB two-column description ISI violation,false positive rate; no categorical good label; ratio/count meaning not independently resolved',
             'quality_admitted':False,'source_table_matches':source_rows,'epoch_audit':ep,
             'provider_active_member_count':len(active),'provider_active_selected_member_count':len(selected),
             'provider_active_interval_count':len(valid_tints),'provider_active_puretone_matches':len(matches),
             'provider_active_sources':[{'path':r['path'],'attributes':r['attributes']} for r in selected],
             'fully_admitted':False}
        records.append(rec)
    summary={}
    for ds in POLICY['datasets']:
        group=[r for r in records if r['dandiset']==ds['id']]
        strata={}
        for task in sorted({r['task'] for r in group}):
            local=[r for r in group if r['task']==task];regions={}
            for name in POLICY['regions']:
                rr=[r for r in local if r['region_counts'].get(name,0)]
                tiers={}
                for tier in POLICY['screening_tiers']:
                    possible=[r for r in rr if r['region_counts'][name]>=tier]
                    epochs=[r for r in possible if len(r['epoch_audit']['basic_epochs'])>=POLICY['candidate_design_minimum_epochs']]
                    active=[r for r in possible if r['provider_active_puretone_matches']>=POLICY['candidate_design_minimum_epochs']]
                    tiers[str(tier)]={'raw_anatomical_mice':len({r['mouse_id'] for r in possible}),
                                      'raw_probes':len(possible),'raw_sessions':len({r['session_id'] for r in possible}),
                                      'basic_epoch_upper_bound_mice':len({r['mouse_id'] for r in epochs}),
                                      'active_epoch_count_upper_bound_mice':len({r['mouse_id'] for r in active}),
                                      'quality_admitted_mice':0}
                regions[name]={'total_labeled_units':sum(r['region_counts'][name] for r in rr),'anatomical_mice':len({r['mouse_id'] for r in rr}),'tiers':tiers}
            strata[task]={'mice':len({r['mouse_id'] for r in local}),'sessions':len({r['session_id'] for r in local}),'probes':len(local),'regions':regions}
        primary_task='Passive' if ds['id']=='001260' else 'Aversion'
        scope=strata.get(primary_task,{}).get('regions',{})
        max_mice=max((r['tiers']['5']['raw_anatomical_mice'] for r in scope.values()),default=0)
        stratum_verdict='DATA_INSUFFICIENT' if max_mice<16 else 'INCONCLUSIVE_METADATA'
        summary[ds['id']]={'version':ds['version'],'files':len(group),'raw_subject_labels':len({r['raw_subject_id'] for r in group}),
                           'canonical_mice':len({r['mouse_id'] for r in group}),'sessions':len({r['session_id'] for r in group}),
                           'units':sum(r['units'] for r in group),'strata':strata,'primary_task_stratum':primary_task,
                           'single_region_largest_tier5_raw_mouse_upper_bound':max_mice,
                           'upper_bound_scope':primary_task+' task stratum only, not the whole release',
                           'primary_task_stratum_verdict':stratum_verdict,
                           'scientific_verdict':'INCONCLUSIVE_METADATA',
                           'broader_pre_tone_design':'Unassessed multi-context design; no pooling or admission authorized',
                           'fully_admitted_mice':0,'mouse_split_allocated':False}
    dssets=[{r['mouse_id'] for r in records if r['dandiset']==ds['id']} for ds in POLICY['datasets']]
    overlap={'canonical_subjects':sorted(dssets[0]&dssets[1]),'same_session_probe':[]}
    for r in records:
        if any(x['dandiset']!=r['dandiset'] and x['recording_id']==r['recording_id'] for x in records):overlap['same_session_probe'].append(r['recording_id'])
    result={'mission':POLICY['mission'],'candidates':summary,'cross_release_overlap':overlap,'all_records':records,
            'aliases':aliases,'spike_array_reads':0,'model_fits':0,'M1_M7_started':False,
            'all_candidate_verdicts_are_conditional_on_registered_scope':True}
    destination.mkdir(parents=True,exist_ok=True)
    with (destination/'audit.json').open('x',encoding='utf8',newline='\n') as f:f.write(json.dumps(result,indent=2,allow_nan=False)+'\n')
    write_csv(destination/'all_unit_metadata.csv',units)
    write_csv(destination/'all_basic_epoch_identities.csv',epochrows)
    thin=[{k:r[k] for k in ['dandiset','version','asset_id','asset_path','mouse_id','raw_subject_id','session_id','recording_id','probe_id','task','units','quality_present','provider_active_interval_count','provider_active_puretone_matches','fully_admitted']} for r in records]
    write_csv(destination/'all_recording_identities.csv',thin)
    mice=[]
    for ds in POLICY['datasets']:
        for mid in sorted({r['mouse_id'] for r in records if r['dandiset']==ds['id']}):
            rr=[r for r in records if r['dandiset']==ds['id'] and r['mouse_id']==mid]
            mice.append({'dandiset':ds['id'],'mouse_id':mid,'raw_subject_labels':'|'.join(sorted({r['raw_subject_id'] for r in rr})),
                         'sessions':len({r['session_id'] for r in rr}),'probes':len(rr),'tasks':'|'.join(sorted({r['task'] for r in rr})),'fully_admitted':False})
    write_csv(destination/'all_mouse_denominators.csv',mice)
    print(json.dumps({key:{k:v for k,v in value.items() if k!='strata'} for key,value in summary.items()},indent=2))


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,default=P/'results/review1')
    run(ap.parse_args().output)
