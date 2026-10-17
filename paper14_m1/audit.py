"""Saved source-contract audit. No neural or behavioral-signal sample loader."""
import csv
import datetime
import hashlib
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

from .retrieve import P,ROOT,read,write,digest

NS={'s':'http://s3.amazonaws.com/doc/2006-03-01/'}
STATUSES={'CONFIRMED_AVAILABLE_AND_ALIGNABLE','AVAILABLE_WITH_LIMITATIONS','NOT_RECORDED','UNRESOLVED'}


def verify_inputs():
    for name,h in read(P/'INPUT_FREEZE.json')['hashes'].items():
        if digest((ROOT/name).read_bytes())!=h:raise ValueError('Historical M0 artifact changed: '+name)


def table(path,rows):
    rows=list(rows);path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    if not rows:raise ValueError('No metadata rows')
    with path.open('w',encoding='utf8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)


def cohort():
    with (ROOT/'paper14_m0/results/DR_selected_populations.csv').open(encoding='utf8',newline='') as f:
        rows=[r for r in csv.DictReader(f) if r['region']=='mPFC_composite' and r['metadata_eligible']=='True']
    if len(rows)!=18 or len({r['mouse'] for r in rows})!=18:raise ValueError('Original18animal denominator changed')
    return rows


def allocation(rows):
    if len(rows)!=18 or len({r['mouse'] for r in rows})!=18:raise ValueError('Allocation requires original18unique animals')
    ordered=sorted(rows,key=lambda r:hashlib.sha256(('P14-V1|'+r['mouse']).encode('ascii')).hexdigest())
    return [dict(mouse=r['mouse'],session=r['session'],probe=r['probe'],rank=i+1,allocation_sha256=hashlib.sha256(('P14-V1|'+r['mouse']).encode('ascii')).hexdigest(),arm='development' if i<9 else 'final',physiological_eligibility='UNMEASURED',activation_authorized=False) for i,r in enumerate(ordered)]


def xml_objects(path):
    root=ET.fromstring(Path(path).read_bytes())
    return {c.findtext('s:Key',namespaces=NS):{'ETag':c.findtext('s:ETag',namespaces=NS),'bytes':int(c.findtext('s:Size',namespaces=NS)),'last_modified':c.findtext('s:LastModified',namespaces=NS)} for c in root.findall('s:Contents',NS)},root.findtext('s:IsTruncated',namespaces=NS)=='true'


def canonical_sid(name):
    m=re.match(r'^ecephys_(\d+_\d{4}-\d{2}-\d{2})_',str(name))
    return m.group(1) if m else None


def canonical_version289(record):
    return any(d.get('process_type')=='File format conversion' and d.get('code',{}).get('version')=='0.0.289' for d in record.get('processing',{}).get('data_processes',[]))


def tracked_rows(data):
    if isinstance(data,dict):
        for k,v in data.items():
            if str(k).startswith('//allen/') and isinstance(v,dict):yield str(k),v
            else:yield from tracked_rows(v)
    elif isinstance(data,list):
        for v in data:yield from tracked_rows(v)


def metadata_path_match(path,sid):
    mouse,date=sid.split('_')
    return bool(re.search(r'(?<!\d)'+re.escape(mouse)+r'_(?:'+re.escape(date)+r'|'+date.replace('-','')+r')(?!\d)',path))


def descriptor_presence(descriptor):
    metadata=descriptor.get('metadata',{})
    # Keys/attributes/shape only. No values from data or timestamps arrays.
    return {'running':any(k.startswith('processing/behavior/running_speed/') for k in metadata),
        'licks':any(k.startswith('processing/behavior/licks/') for k in metadata),
        'pupil':any(k.startswith('processing/behavior/eye_tracking/pupil_area/') for k in metadata),
        'behavior_shapes':{k:v.get('shape') for k,v in metadata.items() if k.endswith('/.zarray') and k.startswith('processing/behavior/') and ('running_speed/' in k or 'eye_tracking/pupil_area/' in k or '/licks/timestamps/' in k)}}


def collect_metadata_rates(node,prefix=''):
    """Source configured rate fields, not measured sample intervals."""
    found={}
    if isinstance(node,dict):
        for k,v in node.items():
            path=prefix+'.'+k if prefix else k
            if k in {'sampling_rate','sample_rate','frame_rate','sampling_frequency'} and isinstance(v,(str,int,float)):found[path]=v
            else:found.update(collect_metadata_rates(v,path))
    elif isinstance(node,list):
        for i,v in enumerate(node):found.update(collect_metadata_rates(v,prefix+f'[{i}]'))
    return found


def activation_gate(*,rights_all18,clock_all18,protocol_complete,independent_ready_review,neural_owner_authorization=False):
    # A specification oracle, not a production security or data-release controller.
    return all([rights_all18,clock_all18,protocol_complete,independent_ready_review,neural_owner_authorization])


def run(out=None):
    verify_inputs();out=P/'results' if out is None else Path(out);out.mkdir(parents=True,exist_ok=True)
    c=cohort();table(out/'RESERVED_ALLOCATION_9_9.csv',allocation(c))
    sources=P/'sources';objects,truncated=xml_objects(sources/'scratch_nwb_v289_listing.xml')
    if truncated:raise ValueError('ScratchNWBlisting truncated; cannot infer missing objects')
    canonical=read(sources/'all_selected_subjects_v289_query.json')
    if len(canonical)>=100:raise ValueError('Version-specific canonical query may be truncated')
    if not all(canonical_version289(r) for r in canonical):raise ValueError('Canonical conversion version differs')
    bysid={}
    for r in canonical:bysid.setdefault(canonical_sid(r['name']),[]).append(r)
    tracked=list(tracked_rows(yaml.safe_load((sources/'tracked_sessions.yaml').read_text(encoding='utf8'))))
    sessions=pd.read_csv(ROOT/'paper14_m0/metadata/session_metadata.csv.gz',dtype={'session_id':str})
    trials=pd.read_csv(ROOT/'paper14_m0/metadata/trials_metadata.csv.gz',dtype={'session_id':str},float_precision='round_trip')
    masks=pd.read_csv(ROOT/'paper14_m0/results/DR_trial_metadata_masks.csv.gz')
    known=read(sources/'canonical_known3_query.json');descriptor={}
    for i,r in enumerate(known):descriptor[canonical_sid(r['name'])]=descriptor_presence(read(sources/f'canonical_mapping{i+1}_descriptor.json'))
    coverage=[];rights=[];missing_responses=[]
    for r in c:
        sid=r['session'];key='dynamic-routing/cache/nwb/v0.0.289/'+sid+'.nwb'
        if key not in objects:raise ValueError('Frozen candidate NWBobject not listed: '+sid)
        sr=sessions[sessions.session_id==sid]
        if len(sr)!=1:raise ValueError('Ambiguous original session identity')
        x=trials[trials.session_id==sid].merge(masks[masks.session==sid][['trial_index','usable_primary_metadata']],on='trial_index',validate='one_to_one')
        x=x[x.usable_primary_metadata];response=x.is_response.astype('string').str.lower().eq('true');reward=x.is_rewarded.astype('string').str.lower().eq('true')
        rt=pd.to_numeric(x.response_time,errors='coerce');wt=pd.to_numeric(x.reward_time,errors='coerce')
        missing_responses.extend({'mouse':r['mouse'],'session':sid,'probe':r['probe'],'trial_index':int(t.trial_index),'context':t.rewarded_modality,'is_response':True,'response_time':'MISSING_NOT_IMPUTED'} for t in x[response&~np.isfinite(rt)].itertuples())
        matches=[(k,v) for k,v in tracked if metadata_path_match(k,sid)]
        flags=[v.get('session_kwargs',{}) for _,v in matches]
        original_records=read(sources/(sid+'_canonical_metadata.json'))
        rates={}
        for rec in original_records:
            if re.fullmatch(r'ecephys_\d+_\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}',rec['name']):rates.update(collect_metadata_rates(rec.get('acquisition',{})))
        d=descriptor.get(sid)
        coverage.append({'mouse':r['mouse'],'session':sid,'probe':r['probe'],'provider_supported_metadata_units':int(r['qualified_metadata_units']),
            'scratch_nwb_object_listed':True,'scratch_bytes':objects[key]['bytes'],'scratch_ETag':objects[key]['ETag'],
            'running_target_scratch_status':'UNRESOLVED','pupil_target_scratch_status':'UNRESOLVED',
            'lick_response_status':'AVAILABLE_WITH_LIMITATIONS','usable_trials_original_mask':len(x),'response_events':int(response.sum()),'response_true_missing_time':int((response&~np.isfinite(rt)).sum()),
            'reward_events':int(reward.sum()),'reward_true_missing_time':int((reward&~np.isfinite(wt)).sum()),
            'provider_session_start':sr.iloc[0].session_start_time,'provider_timestamps_reference_time':sr.iloc[0].timestamps_reference_time,
            'behavior_ephys_clock_status':'UNRESOLVED','clock_contract':'npc_sessions0.0.289 sync-dependent conversion; per-probe realized mapping/residuals not verified',
            'observations_status':'AVAILABLE_WITH_LIMITATIONS','observation_evidence':'M0provider obs_intervals contain allretainedwindows; not packet-integrity or clock-quality proof',
            'current_tracking_matches':len(matches),'current_tracking_kwargs':json.dumps(flags,sort_keys=True),
            'interruption_status':'UNRESOLVED','tracking_notes':json.dumps([v for _,v in matches],sort_keys=True),
            'configured_rate_metadata_only':json.dumps(rates,sort_keys=True),'measured_running_pupil_sampling_Hz':'UNRESOLVED',
            'same_session_canonical_v289_assets':len(bysid.get(sid,[])),
            'canonical_counterpart_descriptor_only':json.dumps(d,sort_keys=True) if d else 'NOT_EXAMINED_OR_NO_EXACT_COUNTERPART; not NOT_RECORDED',
            'source_revision_warning':'Currenttracking is not the frozen conversion runtime; canonicalZarr is not proven identical to scratchHDF5; no data samples read'})
        rights.append({'mouse':r['mouse'],'session':sid,'scratch_uri':'s3://aind-scratch-data/'+key,'scratch_ETag':objects[key]['ETag'],
            'canonical_same_session_v289':';'.join(v['name'] for v in bysid.get(sid,[])),
            'canonical_licenses':';'.join(sorted({v.get('data_description',{}).get('license','UNKNOWN') for v in bysid.get(sid,[])})),
            'scratch_rights_status':'UNRESOLVED','canonical_to_scratch_applicability_proven':False})
    table(out/'SESSION_COVERAGE_18.csv',coverage);table(out/'SOURCE_RIGHTS_18.csv',rights)
    table(out/'MISSING_RESPONSE_TIME_EVENTS.csv',missing_responses)
    table(out/'CANONICAL_VERSION289_ASSETS.csv',[{'name':r['name'],'session':canonical_sid(r['name']),'location':r['location'],'license':r.get('data_description',{}).get('license','UNKNOWN'),'matches_original_selected_session':canonical_sid(r['name']) in {q['session'] for q in c}} for r in canonical])
    logs=[json.loads(x) for x in (sources/'access.jsonl').read_text(encoding='utf8').splitlines()]
    decision={'mission':'P14-M1-SOURCE-CONTRACT-AND-PROTOCOL-FREEZE','scientific_decision':'SOURCE_RIGHTS_BLOCKED',
        'scratch_rights_verified_sessions':0,'candidate_mice':18,'physiologically_eligible_mice':None,
        'same_subject_canonical_v289_records':len(canonical),'same_selected_session_canonical_v289':sum(bool(bysid.get(r['session'])) for r in c),
        'different_session_date_records':sum(canonical_sid(r['name']) not in {q['session'] for q in c} for r in canonical),
        'movement_pupil_scratch_sessions_confirmed':0,'confirmed_not_recorded_sessions':0,'actual_clock_quality_verified':0,
        'task_response_missing_timestamps':sum(r['response_true_missing_time'] for r in coverage),'task_reward_missing_timestamps':sum(r['reward_true_missing_time'] for r in coverage),
        'allocation_identity_reservation':[9,9],'allocation_active_protocol':False,'scientific_protocol_frozen':False,
        'source_and_alignment_stops_preserved':True,'Prompt3_eligible_for_owner_consideration':False,
        'raw_neural_values_or_raw_behavior_signals_read':0,'real_model_fits':0,'neural_scores':0,'final_assessments':0,'external_correspondence_sent':False,
        'scripted_http_attempts':len(logs),'scripted_response_bytes':sum(r['bytes'] for r in logs),'browser_discovery_transport_bytes':'UNOBSERVABLE_NOT_INCLUDED',
        'M0_verdict_unchanged':'INCONCLUSIVE_METADATA','next_step':'Unsent data-owner rights/provenance inquiry; remaining M1protocol phases held, not M2'}
    write(out/'M1_DECISION.json',decision);verify_inputs();return decision


if __name__=='__main__':print(json.dumps(run(),sort_keys=True))
