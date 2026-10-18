"""Saved-source arithmetic and completeness checks;no real NWB access."""
import csv,gzip,math,re
from collections import Counter
from pathlib import Path
import numpy as np
from .core import *
EXPECTED_FILES = frozenset({'paper16_m0/metadata/allen_aws_registry.json', 'paper16_m0/HISTORICAL_ROADMAP.md', 'paper16_m0/ENVIRONMENT.md', 'paper16_m0/results/ROLE_ALLOCATION.json', 'paper16_m0/.gitignore', 'paper16_m0/code/http_metadata.py', 'paper16_m0/code/core.py', 'paper16_m0/metadata/sdk_license_2_16_2.json', 'paper16_m0/tables/all_mouse_sessions.csv', 'paper16_m0/tables/all_probe_populations.csv', 'paper16_m0/results/COMMON_GRATING_PARAMETER_SUPPORT.json', 'paper16_m0/results/PILOT_ATTEMPT_829720705.json', 'paper16_m0/metadata/sessions_sdk_definition.json', 'paper16_m0/metadata/sdk_tag_2_16_2.json', 'paper16_m0/code/test_core.py', 'paper16_m0/metadata/allen_terms_current.json', 'paper16_m0/metadata/sdk_nwb_api_2_16_2.json', 'paper16_m0/results/PILOT_METADATA_SELECTION.json', 'paper16_m0/metadata/METADATA_INPUTS.json', 'paper16_m0/results/COUNT_EXAMPLES_829720705.json', 'paper16_m0/results/POPULATION_INVENTORY.json', 'paper16_m0/metadata/source_unit_qc.body', 'paper16_m0/code/test_saved_integrity.py', 'paper16_m0/code/test_reader.py', 'paper16_m0/FEASIBILITY_REGISTRATION.md', 'paper16_m0/SOURCE_COMPATIBILITY.md', 'paper16_m0/metadata/VISp_ontology.body', 'paper16_m0/metadata/channels.json', 'paper16_m0/results/FINAL_M0_STATUS.json', 'paper16_m0/tables/stimulus_family_feasibility.csv', 'paper16_m0/results/PILOT_760345702.json', 'paper16_m0/PROPOSED_PRIMARY_QUESTION.md', 'paper16_m0/results/COUNT_EXAMPLES_760345702.json', 'paper16_m0/code/acquire_metadata.py', 'paper16_m0/metadata/sessions_sdk_definition.body', 'paper16_m0/code/access_gate.py', 'paper16_m0/results/PAYLOAD_LEDGER.json', 'paper16_m0/metadata/sessions.body', 'paper16_m0/code/metadata_audit.py', 'paper16_m0/results/PILOT_ATTEMPT_760345702.json', 'paper16_m0/results/TRANSFER_760345702.json', 'paper16_m0/code/test_integration.py', 'paper16_m0/SPIKE_STIMULUS_BEHAVIOR_ALIGNMENT.md', 'paper16_m0/PROPOSED_EVALUATION_STRATEGY.md', 'paper16_m0/requirements.txt', 'paper16_m0/OBSERVATION_AND_ARTIFACT_LIMITATIONS.md', 'paper16_m0/metadata/VISp_ontology.json', 'paper16_m0/results/NATIVE_EVENTS_760345702.npz', 'paper16_m0/metadata/METADATA_ACTIVE_BINDING.json', 'paper16_m0/results/NATIVE_EVENTS_829720705.npz', 'paper16_m0/M1_SCIENTIFIC_HANDOFF.md', 'paper16_m0/code/build_assessment.py', 'paper16_m0/results/PILOT_829720705.json', 'paper16_m0/metadata/sessions.json', 'paper16_m0/metadata/channels.body', 'paper16_m0/metadata/allen_citation_current.json', 'paper16_m0/code/FEASIBILITY_REGISTRATION.json', 'paper16_m0/metadata/sdk_session_2_16_2.json', 'paper16_m0/metadata/sdk_unit_filters_2_16_2.json', 'paper16_m0/results/TRANSFER_829720705.json', 'paper16_m0/code/pilot_transfer.py', 'paper16_m0/metadata/probes.json', 'paper16_m0/metadata/probes.body', 'paper16_m0/reproduce_saved.ps1', 'paper16_m0/FEASIBILITY_REGISTRATION.json', 'paper16_m0/metadata/sdk_cache_2_16_2.json', 'paper16_m0/results/PILOT_OBJECT_FREEZE.json', 'paper16_m0/results/METADATA_SUMMARY.json', 'paper16_m0/SOURCE_RIGHTS_REGISTRY.json', 'paper16_m0/code/saved_reproduce.py', 'paper16_m0/P16_M0_REPORT.md', 'paper16_m0/metadata/source_unit_qc.json', 'paper16_m0/code/pilot_reader.py', 'paper16_m0/code/evidence_checks.py'})

P=Path(__file__).resolve().parents[1];R=P.parent;E=R/'ops/evidence/2026-10-18/p16-visual-cortex-data-first-m0'
FINAL_KEYS={'MISSION_ID','M0_STATUS','SCIENTIFIC_FEASIBILITY_VERDICT','SELECTED_DATASET','SELECTED_SOURCE_VERSION','SOURCE_RIGHTS_PASS','SELECTED_REGION','INDEPENDENT_CANDIDATE_MICE','QUALIFIED_POPULATION_DISTRIBUTION','STIMULUS_COVERAGE','REAL_SPIKE_PILOT_PASS','STIMULUS_SPIKE_ALIGNMENT_PASS','OBSERVATION_CONTRACT','PROPOSED_PRIMARY_QUESTION','PROPOSED_HOLDOUT_DESIGN','KNOWN_LIMITATIONS','PROMPT_2_READY','BUG_COUNT','WARN_COUNT','GIT_COMMIT','REMOTE_VERIFICATION'}

def check_manifest():
    manifest=read_json(P/'SAVED_EVIDENCE_MANIFEST.json')
    actual={f.relative_to(R).as_posix() for f in P.rglob('*') if f.is_file() and 'work' not in f.parts and '__pycache__' not in f.parts and f.name!='SAVED_EVIDENCE_MANIFEST.json'}
    assert set(manifest['files'])==actual==EXPECTED_FILES,'Incomplete/unexpected scientific file set'
    for name,digest in manifest['files'].items():assert sha256(R/name)==digest,name
    return manifest

def csv_rows(name):return list(csv.DictReader((P/'tables'/name).open(encoding='utf-8-sig')))
def csv_strings(row):return {k:'' if v is None else str(v) for k,v in row.items()}

def check_saved():
    check_manifest();checks=['Exact complete mandatory scientific artifact set and every SHA256']
    source={n:read_json(P/'metadata'/f'{n}.body')['msg'] for n in ['sessions','probes','channels','source_unit_qc','sessions_sdk_definition']}
    inventory=metadata_populations(source['sessions'],source['probes'],source['channels'],source['source_unit_qc'])
    assert inventory==read_json(P/'results/POPULATION_INVENTORY.json')
    sm={int(s['id']):s for s in source['sessions']};enriched={int(s['id']):s for s in source['sessions_sdk_definition']}
    roster_path=R/'paper12_curated_v1/replay/mouse_evidence.csv';roster=list(csv.DictReader(roster_path.open(encoding='utf-8-sig')))
    assert len(roster)==26 and len({x['mouse_id'] for x in roster})==26
    for row in roster:assert str(sm[int(row['session_id'])]['specimen_id'])==row['mouse_id']
    protected={x['mouse_id'] for x in roster if x['group']=='final'};assert len(protected)==13
    roles=allocate_roles(inventory['selected'],[x['mouse_id'] for x in roster],protected)
    assert roles==read_json(P/'results/ROLE_ALLOCATION.json')
    populations=inventory['all_populations'];tiers={str(n):{'mice':len({r['mouse_id'] for r in populations if r[f'tier_{n}']}),'sessions':len({r['session_id'] for r in populations if r[f'tier_{n}']}),'populations':sum(r[f'tier_{n}'] for r in populations)} for n in [5,8,12,20]}
    summary=read_json(P/'results/METADATA_SUMMARY.json')
    expected={'source_sessions':len(source['sessions']),'source_mice':inventory['source_mice'],'source_probes':len(source['probes']),'source_channels':len(source['channels']),'source_units':len(source['source_unit_qc']),'anatomical_VISp_mice':len({r['mouse_id'] for r in populations if r['anatomical_units']>0}),'tiers':tiers,'selected_mice':len(roles),'Development':sum(r['group']=='Development' for r in roles),'Final_candidates':sum(r['group']=='Final_candidate' for r in roles),'historical_mouse_overlap':sum(r['historical_source_overlap'] for r in roles),'invalid_probe_rates':sum(not r['source_probe_valid'] for r in populations),'historical_roster_sha256':sha256(roster_path),'role_composition':{g:dict(Counter(r['session_type'] for r in roles if r['group']==g)) for g in ['Development','Final_candidate']}}
    for key,value in expected.items():assert summary[key]==value,('metadata summary',key)
    assert summary['registration_sha256']==sha256(P/'FEASIBILITY_REGISTRATION.json')
    assert summary['source_validity_invalid_metric_counts_all_regions_nonexclusive']=={} # Verified source domains below,not a relaxed missing-data gate.
    for u in source['source_unit_qc']:
        a,p,v=(float(u[k]) for k in ['amplitude_cutoff','presence_ratio','isi_violations']);assert all(math.isfinite(x) for x in [a,p,v]) and a>=0 and 0<=p<=1 and v>=0
    caps=read_json(R/'paper12/metadata/allen_header_capability.json');cap={int(x['session_id']):x for x in caps};sizes={sid:int(x['content_range'].split('/')[1]) for sid,x in cap.items()}
    selected=choose_pilots(roles,sizes,protected);pilots=[]
    for row in selected:
        sid=row['session_id'];files=[f for f in enriched[sid]['well_known_files'] if f['well_known_file_type']['name']=='EcephysNwb'];assert len(files)==1;f=files[0]
        assert int(f['id'])==int(cap[sid]['file_id'])
        pilots.append({**row,'file_id':f['id'],'download_url':'https://api.brain-map.org'+f['download_link'],'declared_bytes':sizes[sid],'prior_etag':cap[sid]['etag']})
    assert pilots==read_json(P/'results/PILOT_METADATA_SELECTION.json')
    assert sum(p['declared_bytes'] for p in pilots)==summary['pilot_bytes_declared']
    freeze=read_json(P/'results/PILOT_OBJECT_FREEZE.json');assert freeze['roles_sha256']==sha256(P/'results/ROLE_ALLOCATION.json') and freeze['metadata_selection_sha256']==sha256(P/'results/PILOT_METADATA_SELECTION.json')
    for obj,p in zip(freeze['objects'],pilots):
        for key,value in p.items():assert obj[key]==value
        assert obj['etag']==p['prior_etag'] and obj['content_length']==p['declared_bytes']
    assert len(freeze['objects'])==len(pilots)==2
    expected_probe=[csv_strings({k:v for k,v in row.items() if k!='qualified_unit_ids'}) for row in populations];assert csv_rows('all_probe_populations.csv')==expected_probe
    actual_mice=csv_rows('all_mouse_sessions.csv');assert len(actual_mice)==len(source['sessions'])
    for row,s in zip(actual_mice,source['sessions']):
        sid=int(s['id']);donor=enriched[sid]['specimen']['donor'];rr=[r for r in populations if r['session_id']==sid];role=next((r for r in roles if r['session_id']==sid),None)
        wanted={'mouse_id':str(s['specimen_id']),'donor_id':donor['id'],'session_id':sid,'session_type':s['stimulus_name'],'sex':donor['sex'],'genotype':donor['full_genotype'],'historical_overlap':str(s['specimen_id']) in {x['mouse_id'] for x in roster},'prior_Final_protected':str(s['specimen_id']) in protected,'anatomical_VISp_units':sum(r['anatomical_units'] for r in rr),'max_sameprobe_qualified_VISp':max(r['qualified_units'] for r in rr),'selected_probe':role['probe_id'] if role else None,'role':role['group'] if role else 'Not_selected','pilot':any(p['session_id']==sid for p in pilots)}
        for key,value in csv_strings(wanted).items():assert row[key]==value,('mouse table',sid,key)
        header=__import__('json').loads(gzip.decompress((R/f'paper12_native_support1/metadata/native_headers/{sid}.json.gz').read_bytes()));assert row['stimulus_families']=='|'.join(header['all_interval_names'])
    checks.append('Recomputed all-source summary,unit/probe tiers,whole-mouse roles,size-selected pilots,and complete mouse/probe tables')
    completed=[];families=[];common=[];execution=[];channel={int(c['id']):c for c in source['channels']};units={int(u['id']):u for u in source['source_unit_qc']}
    for p in pilots:
        sid=p['session_id'];transfer=read_json(P/'results'/f'TRANSFER_{sid}.json');attempt=read_json(P/'results'/f'PILOT_ATTEMPT_{sid}.json');d=read_json(P/'results'/f'PILOT_{sid}.json')
        assert transfer['status']==attempt['status']=='COMPLETE';assert transfer['bytes_written']==p['declared_bytes'];assert transfer['object_freeze_sha256']==sha256(P/'results/PILOT_OBJECT_FREEZE.json')
        assert attempt['result_sha256']==sha256(P/'results'/f'PILOT_{sid}.json') and d['source_sha256']==transfer['sha256'] and re.fullmatch('[0-9a-f]{64}',transfer['sha256'])
        assert d['session_id']==sid and d['mouse_id']==p['mouse_id'] and d['probe_id']==p['probe_id'] and d['group']=='Development'
        assert d['nwb_version']=='2.2.2' and d['clock_reference_equal'] is True and d['event_binary64_roundtrip_pass'] is True and d['no_fits'] is True and d['no_Final_access'] is True
        assert d['selected_unit_ids']==p['qualified_unit_ids'][:8] and len(d['unit_certificates'])==8
        for cert,uid in zip(d['unit_certificates'],d['selected_unit_ids']):
            assert cert['unit_id']==uid and cert['peak_channel_id']==int(units[uid]['ecephys_channel_id'])
            assert int(channel[cert['peak_channel_id']]['ecephys_probe_id'])==p['probe_id'] and cert['structure'] in REGIONS
            assert cert['nonfinite']==cert['decreases']==0 and cert['binary64_roundtrip_pass'] is True
            assert type(cert['spike_count']) is int and cert['spike_count']>=0 and 0<=cert['equal_adjacent']<=max(0,cert['spike_count']-1) and re.fullmatch('[0-9a-f]{64}',cert['binary64_sha256'])
            if cert['spike_count']:assert restore_time(cert['min'])<=restore_time(cert['max'])
        native=P/'results'/f'NATIVE_EVENTS_{sid}.npz';assert sha256(native)==d['events_sha256'];support=set();condition_support=set()
        with np.load(native,allow_pickle=False) as events:
            expected_keys={f['family']+suffix for f in d['families'] for suffix in ['_start','_stop','_id']};assert set(events.files)==expected_keys
            for f in d['families']:
                name=f['family'];a,b,ids=(events[name+suffix] for suffix in ['_start','_stop','_id']);assert a.dtype==b.dtype==np.dtype('float64') and len(a)==len(b)==len(ids)==f['original_presentations']
                assert f['start_stop_sha256']==[__import__('hashlib').sha256(x.astype('<f8').tobytes()).hexdigest() for x in [a,b]]
                for x in [a,b]:assert np.array_equal(x.view('u8'),np.frombuffer(x.tobytes(),dtype=x.dtype).view('u8'))
                valid=np.isfinite(a)&np.isfinite(b)&(a<b);valid &= np.array([observed(x,y,[[x,y]],d['invalid_intervals_applied']) if math.isfinite(x) and math.isfinite(y) and x<y else False for x,y in zip(a,b)])
                assert np.all(np.diff(a[np.isfinite(a)])>=0) and int(valid.sum())==f['valid_presentations'] and int((~valid).sum())==f['invalid_or_nonfinite']
                assert [int(ids[i]) for i in np.flatnonzero(valid)[:64]]==f['first64_original_ids']
                c=f['condition_values_and_repetitions'];ns=[r['n'] for r in c];assert all(type(n) is int and n>0 for n in ns)
                assert sum(ns)==int(valid.sum()) and len(c)==f['distinct_conditions'] and sum(n>=2 for n in ns)==f['repeated_conditions']
                assert min(ns,default=0)==f['condition_repetition_min'] and max(ns,default=0)==f['condition_repetition_max']
                assert f['coverage_gate']==(int(valid.sum())>=20 and sum(n>=2 for n in ns)>=2)
                assert f['positive_interpresentation_gaps']==int((a[1:]-b[:-1]>0).sum()) and f['overlapping_intervals']==int((a[1:]-b[:-1]<0).sum())
                assert f['duration_min']==float(np.min((b-a)[valid])) and f['duration_max']==float(np.max((b-a)[valid]))
                for i in np.flatnonzero(valid)[:64]:
                    for width in [.01,.05]:
                        count=int(math.floor((float(b[i])-float(a[i]))/width));edges=float(a[i])+np.arange(count+1,dtype=np.float64)*width;edges=edges[edges<=float(b[i])]
                        if len(edges)>=2:
                            for uid in d['selected_unit_ids']:support.add((name,int(i),int(ids[i]),uid,width,len(edges)-1))
                if 'drifting_gratings' in name:
                    for r in c:
                        try:v=tuple(float(r['values'][f['condition_columns'].index(k)]) for k in ['orientation','temporal_frequency','spatial_frequency','contrast'])
                        except (ValueError,IndexError):continue
                        if all(math.isfinite(x) for x in v):condition_support.add(v)
                families.append({'session_id':sid,'family':name,'original_presentations':f['original_presentations'],'valid_presentations':f['valid_presentations'],'invalid_presentations':f['invalid_or_nonfinite'],'distinct_conditions':len(c),'repeated_conditions':sum(n>=2 for n in ns),'repetition_min':min(ns,default=0),'repetition_max':max(ns,default=0),'duration_min':f['duration_min'],'duration_max':f['duration_max'],'positive_gaps':f['positive_interpresentation_gaps'],'overlaps':f['overlapping_intervals'],'condition_columns':'|'.join(f['condition_columns']),'pilot_coverage_gate':f['coverage_gate']})
        examples=read_json(P/'results'/f'COUNT_EXAMPLES_{sid}.json');assert len(examples)==d['count_example_rows']==len(support)
        actual_support=set()
        for row in examples:
            key=(row['family'],row['original_ordinal'],row['presentation_id'],row['unit_id'],row['width_illustrative_only'],row['bins']);assert key in support and key not in actual_support;actual_support.add(key)
            assert 0<=row['true_zero_bins']<=row['bins']-row['missing_bins'] and row['total_count']>=row['bins']-row['missing_bins']-row['true_zero_bins']
            assert all(v is None or type(v) is int and v>=0 for v in row['first_bins']) and len(row['first_bins'])==min(5,row['bins'])
            assert row['total_count']>=sum(v for v in row['first_bins'] if v is not None)
        assert actual_support==support
        for key in ['true_zero_bins','missing_bins']:assert sum(x[key] for x in examples)==d[key]
        assert d['coverage_gate']==any(f['coverage_gate'] for f in d['families'])
        common.append(condition_support);completed.append(d);execution.append({'session_id':sid,'mouse_id':p['mouse_id'],'probe_id':p['probe_id'],'declared_bytes':p['declared_bytes'],'transfer_status':transfer['status'],'pilot_status':attempt['status']})
    assert csv_rows('stimulus_family_feasibility.csv')==[csv_strings(row) for row in families]
    shared=read_json(P/'results/COMMON_GRATING_PARAMETER_SUPPORT.json');assert shared['fields']==['orientation','temporal_frequency','spatial_frequency','contrast'];assert shared['shared_parameter_tuples']==[list(v) for v in sorted(common[0]&common[1])];assert shared['phase_at_onset_verified'] is False and shared['Final_outcomes_accessed']==0
    ledger=read_json(P/'results/PAYLOAD_LEDGER.json');metadata=sum(read_json(f).get('bytes',0) for f in (P/'metadata').glob('*.json') if read_json(f).get('url'))
    assert ledger['bytes']==sum(x['bytes'] for x in ledger['events'])==max(20_000_000,metadata)+sum(p['declared_bytes'] for p in pilots)<=6_000_000_000
    checks.append('Recomputed attempt/transfer/certificate links,event identity/validity,condition/repeat arithmetic,count-example structure,stimulus table,common support and conservative payload')
    status=read_json(P/'results/FINAL_M0_STATUS.json');assert FINAL_KEYS<=status.keys()
    valid=len(completed)==2 and all(d['coverage_gate'] and d['clock_reference_equal'] and d['event_binary64_roundtrip_pass'] for d in completed)
    independent=len(roles)>=16 and expected['Development']>=8 and expected['Final_candidates']>=8
    verdict='FEASIBLE_INDEPENDENT_HOLDOUT' if valid and independent else ('FEASIBLE_TEMPORAL_EXPLORATORY' if valid and len(roles)>=4 else 'SOURCE_OR_TIMING_INCONCLUSIVE')
    wanted={'MISSION_ID':MISSION,'SCIENTIFIC_FEASIBILITY_VERDICT':verdict,'INDEPENDENT_CANDIDATE_MICE':len(roles),'QUALIFIED_POPULATION_DISTRIBUTION':tiers,'REAL_SPIKE_PILOT_PASS':valid,'STIMULUS_SPIKE_ALIGNMENT_PASS':valid,'PROMPT_2_READY':valid,'STIMULUS_COVERAGE':{'completed_pilots':len(completed),'families_observed':len(families),'both_pilot_coverage_gates':valid},'execution':execution}
    for key,value in wanted.items():assert status[key]==value,('final scientific status',key)
    assert status['SOURCE_RIGHTS_PASS'] is True and read_json(P/'SOURCE_RIGHTS_REGISTRY.json')['SOURCE_RIGHTS_PASS'] is True
    for k in ['REAL_SPIKE_PILOT_PASS','STIMULUS_SPIKE_ALIGNMENT_PASS','PROMPT_2_READY']:assert type(status[k]) is bool
    for k in ['BUG_COUNT','WARN_COUNT']:assert type(status[k]) is int and status[k]==0
    holdout=status['PROPOSED_HOLDOUT_DESIGN'];assert holdout['Development']==expected['Development'] and holdout['prospective_Final']==expected['Final_candidates'] and holdout['Final_outcomes_accessed']==0
    checks.append('Recomputed all quantitative scientific verdict/status/coverage/holdout gates and required21response fields;no trust in favorable summary flags')
    return checks
