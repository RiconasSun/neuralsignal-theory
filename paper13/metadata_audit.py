"""Saved metadata admission audit; no spike-array or model-score code paths."""
import argparse
from collections import Counter, defaultdict
import csv
import gzip
import json
import math
import re
from pathlib import Path

HERE=Path(__file__).resolve().parent
POLICY=json.loads((HERE/'M0_REGISTRATION.json').read_text())
REGIONS=POLICY['region_priority']


def region(acronym):
    for name in REGIONS:
        if re.fullmatch(re.escape(name)+r'(?:1|2/3|4|5|6a|6b)?',acronym or ''):
            return name
    return None


def read_csv(path):
    opener=gzip.open if path.suffix=='.gz' else open
    with opener(path,'rt',encoding='utf8',newline='') as f:
        yield from csv.DictReader(f)


def trial_status(row):
    required=['intervals_0','intervals_1','stimOn_times','goCue_times','feedback_times']
    try:
        vals={key:float(row[key]) for key in required}
    except (KeyError,ValueError,TypeError):
        return 'missing_timing'
    if not all(math.isfinite(x) for x in vals.values()): return 'nonfinite_timing'
    start,end=vals['intervals_0'],vals['intervals_1']
    stim,go,feedback=(vals[k] for k in required[2:])
    if not start <= stim <= feedback <= end or not start <= go <= feedback:
        return 'invalid_event_order'
    if end-start<.1: return 'short_interval'
    if str(row.get('bwm_include','')).lower()!='true': return 'provider_excluded'
    # Explicit metadata count, not a neural outcome exclusion. Full temporal mask
    # for the selected scoring window must be fixed in M1 if admission can pass.
    return 'usable'


def audit(fixture, clusters, trials, atlas):
    probes, sessions, subjects={}, {}, set()
    for row in fixture:
        pid,eid=row['pid'],row['eid']
        mouse=row['lab']+'/'+row['subject']
        if pid in probes: raise ValueError('Duplicate fixture probe')
        if eid in sessions and sessions[eid]!=mouse:
            raise ValueError('Conflicting session identity')
        probes[pid]=row; sessions[eid]=mouse; subjects.add(mouse)
    if len(probes)>POLICY['bounds']['probe_records'] or len(sessions)>POLICY['bounds']['sessions']:
        raise ValueError('Registered identity budget exceeded')
    counts=defaultdict(Counter); seen=set(); uuid_seen=set()
    all_good=0; outside=Counter(); unknown=Counter(); unit_rows=[]
    all_regions=Counter()
    for row in clusters:
        pid,eid=row['pid'],row['eid']
        key=(pid,row['cluster_id'])
        if key in seen: raise ValueError('Duplicate cluster identity')
        seen.add(key)
        uuid=row.get('uuids')
        if not uuid or uuid in uuid_seen: raise ValueError('Missing/duplicate cluster UUID')
        uuid_seen.add(uuid)
        if pid not in probes:
            outside['unknown_pid']+=1
            continue
        if probes[pid]['eid']!=eid: raise ValueError('Probe/session aggregate mismatch')
        acronym=atlas.get(str(abs(int(row['atlas_id']))))
        if acronym is None: unknown[row['atlas_id']]+=1
        name=region(acronym)
        good=float(row['label'])==1.
        all_good+=good
        if name:
            counts[pid][name+'_all']+=1
            counts[pid][name+'_good']+=good
            all_regions[name]+=1
            unit_rows.append({**row,'acronym':acronym,'region':name,
                              'mouse_id':sessions[eid],'provider_good':good})
    tc=defaultdict(Counter); saturation=defaultdict(Counter)
    trial_rows=0; trial_eids=set(); outside_trials=0
    for row in trials:
        trial_rows+=1; eid=row['eid']; trial_eids.add(eid)
        if eid not in sessions:
            outside_trials+=1
            continue
        tc[eid]['all']+=1
        tc[eid][trial_status(row)]+=1
        for key,value in row.items():
            if key.startswith('saturation_'):
                saturation[eid][key]+=str(value).lower()=='true'
    output=[]
    for pid,f in sorted(probes.items()):
        for name in REGIONS:
            n=counts[pid][name+'_good']; nall=counts[pid][name+'_all']
            eid=f['eid']; usable=tc[eid]['usable']
            output.append({'region':name,'mouse_id':sessions[eid], 'eid':eid,'pid':pid,
                           'lab':f['lab'],'subject':f['subject'],'probe_name':f['probe_name'],
                           'candidate_units':nall,'provider_good_units':n,
                           'total_trials':tc[eid]['all'],'usable_timing_provider_trials':usable,
                           'unit_count_pass':n>=POLICY['minimum_good_units_single_probe'],
                           'trial_count_pass':usable>=POLICY['minimum_usable_trials'],
                           'count_upper_bound_pass':n>=POLICY['minimum_good_units_single_probe'] and usable>=POLICY['minimum_usable_trials'],
                           'physiologically_admitted':False,
                           'source_timing_support':'CURATED_TASK_EVENT_METADATA_ONLY',
                           'covariates_verified':False})
    summary={}
    for name in REGIONS:
        rows=[r for r in output if r['region']==name]
        eligible=[r for r in rows if r['count_upper_bound_pass']]
        good=[r for r in rows if r['unit_count_pass']]
        potential_mice={r['mouse_id'] for r in eligible}
        summary[name]={
            'all_labeled_units':sum(r['candidate_units'] for r in rows),
            'provider_good_units':sum(r['provider_good_units'] for r in rows),
            'anatomical_mice':len({r['mouse_id'] for r in rows if r['candidate_units']}),
            'anatomical_sessions':len({r['eid'] for r in rows if r['candidate_units']}),
            'anatomical_probes':sum(r['candidate_units']>0 for r in rows),
            'unit_threshold_mice':len({r['mouse_id'] for r in good}),
            'unit_threshold_sessions':len({r['eid'] for r in good}),
            'unit_threshold_probes':len(good),
            'count_upper_bound_mice':len(potential_mice),
            'count_upper_bound_sessions':len({r['eid'] for r in eligible}),
            'count_upper_bound_probes':len(eligible),
            'maximum_possible_smaller_group':len(potential_mice)//2,
            'meets_minimum_upper_bound':len(potential_mice)>=2*POLICY['minimum_mice_per_group'],
            'labs_in_upper_bound':dict(Counter({r['mouse_id']:r['lab'] for r in eligible}.values())),
            'fully_admitted_mice':0}
    denominator={'fixture_mice':len(subjects),'fixture_sessions':len(sessions),'fixture_probes':len(probes),
                 'aggregate_clusters':len(seen),'aggregate_good_in_fixture':all_good,
                 'aggregate_cluster_uuids':len(uuid_seen),'outside_fixture_clusters':dict(outside),
                 'unknown_atlas_ids':dict(unknown),'trial_rows':trial_rows,
                 'trial_sessions':len(trial_eids),'outside_fixture_trials':outside_trials,
                 'fixture_sessions_missing_trials':sorted(set(sessions)-trial_eids),
                 'fixture_probes_missing_clusters':sorted(set(probes)-{p for p,_ in seen})}
    stop=not any(s['meets_minimum_upper_bound'] for s in summary.values())
    report={'stage':'M0','scientific_gate':'FAIL_DATA_INSUFFICIENT' if stop else 'PENDING_ESSENTIAL_METADATA',
            'region_priority':REGIONS,'selected_primary_region':None,'regions':summary,
            'denominator':denominator,
            'development_mice':[],'final_mice':[],
            'development_final_allocation_performed':False,
            'neural_outcome_access':False,'model_fits':0,
            'reason':'No candidate reaches16 independent mice even before full covariate/support and training-only QC gates' if stop else 'Upper bound passes; verify all remaining metadata before region admission',
            'continue_M1':False,'stop_required':stop,
            'saturation_trial_counts':dict(saturation),'trial_status_counts':dict(tc)}
    return report,output,unit_rows


def main(destination):
    atlas_data=json.loads((HERE/'metadata/atlas.json').read_text())
    if not atlas_data['success'] or len(atlas_data['msg'])!=atlas_data['total_rows']:
        raise ValueError('Incomplete atlas dictionary')
    atlas={str(r['id']):r['acronym'] for r in atlas_data['msg']}
    report,probes,units=audit(list(read_csv(HERE/'metadata/fixture.csv')),
                             read_csv(HERE/'metadata/clusters_metadata.csv.gz'),
                             read_csv(HERE/'metadata/trials_metadata.csv.gz'),atlas)
    destination.mkdir(parents=True,exist_ok=True)
    for name,rows in [('all_probe_region_denominators.csv',probes),('all_candidate_unit_identities.csv',units)]:
        with (destination/name).open('x',encoding='utf8',newline='') as f:
            writer=csv.DictWriter(f,fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)
    with (destination/'M0_audit.json').open('x',encoding='utf8') as f:
        f.write(json.dumps(report,indent=2,sort_keys=True)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k not in ('saturation_trial_counts','trial_status_counts')},indent=2))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,default=HERE/'results/M0')
    main(parser.parse_args().output)
