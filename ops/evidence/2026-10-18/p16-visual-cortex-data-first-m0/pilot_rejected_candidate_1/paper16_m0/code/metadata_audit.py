"""Saved projected metadata joins only; never opens neural arrays."""
import csv, datetime, gzip, math
from collections import Counter
from pathlib import Path
from .core import *
P=Path(__file__).resolve().parents[1]; R=P.parent
E=R/'ops/evidence/2026-10-18/p16-visual-cortex-data-first-m0'

def csv_out(path,rows):
    with path.open('w',encoding='utf8',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)

def main():
    review=read_json(E/'PREACCESS_PROTOCOL_REVIEW_RECEIPT_2.json')
    if review['open_P0'] or review['open_P1']: raise ValueError('Unresolved preaccess review')
    freeze=read_json(E/'REGISTRATION_RECEIPT_2.json')
    assert freeze['registration_sha256']==sha256(P/'FEASIBILITY_REGISTRATION.json')
    bodies={n:read_json(P/'metadata'/f'{n}.body') for n in ['sessions','probes','channels','source_unit_qc','sessions_sdk_definition']}
    for d in bodies.values(): assert d['success'] and len(d['msg'])==d['total_rows']
    sessions,probes,channels,units=(bodies[n]['msg'] for n in ['sessions','probes','channels','source_unit_qc'])
    sm={int(s['id']):s for s in sessions}; enriched={int(s['id']):s for s in bodies['sessions_sdk_definition']['msg']}
    assert set(sm)==set(enriched)
    # Verify specimen identity including donor uniqueness, not stimulus outcomes.
    donor_mouse={}
    for sid,s in enriched.items():
        assert int(s['specimen_id'])==int(sm[sid]['specimen_id'])==int(s['specimen']['id'])
        donor=int(s['specimen']['donor']['id']); mouse=str(s['specimen_id'])
        if donor in donor_mouse and donor_mouse[donor]!=mouse: raise ValueError('Repeated donor/specimen identity ambiguous')
        donor_mouse[donor]=mouse
    roster_path=R/'paper12_curated_v1/replay/mouse_evidence.csv'
    roster=list(csv.DictReader(roster_path.open(encoding='utf-8-sig')))
    assert len(roster)==26 and len({r['mouse_id'] for r in roster})==26
    for r in roster:
        assert str(sm[int(r['session_id'])]['specimen_id'])==r['mouse_id']
    history={r['mouse_id'] for r in roster}; protected={r['mouse_id'] for r in roster if r['group']=='final'}
    assert len(protected)==13
    inventory=metadata_populations(sessions,probes,channels,units)
    roles=allocate_roles(inventory['selected'],history,protected)
    caps=read_json(R/'paper12/metadata/allen_header_capability.json')
    cap={int(x['session_id']):x for x in caps}; sizes={sid:int(x['content_range'].split('/')[1]) for sid,x in cap.items()}
    for sid,s in enriched.items():
        files=[f for f in s['well_known_files'] if f['well_known_file_type']['name']=='EcephysNwb']
        assert len(files)==1 and int(files[0]['id'])==int(cap[sid]['file_id'])
    pilots=choose_pilots(roles,sizes,protected)
    pilot_rows=[]
    for row in pilots:
        sid=row['session_id']; f=next(f for f in enriched[sid]['well_known_files'] if f['well_known_file_type']['name']=='EcephysNwb')
        pilot_rows.append({**row,'file_id':f['id'],'download_url':'https://api.brain-map.org'+f['download_link'],'declared_bytes':sizes[sid], 'prior_etag':cap[sid]['etag']})
    populations=inventory['all_populations']; tiers={str(n):{'mice':len({r['mouse_id'] for r in populations if r[f'tier_{n}']}),'sessions':len({r['session_id'] for r in populations if r[f'tier_{n}']}),'populations':sum(r[f'tier_{n}'] for r in populations)} for n in [5,8,12,20]}
    disposition=[]
    for s in sessions:
        rows=[r for r in populations if r['session_id']==int(s['id'])]; role=next((r for r in roles if r['session_id']==int(s['id'])),None)
        donor=enriched[int(s['id'])]['specimen']['donor']
        disposition.append({'mouse_id':str(s['specimen_id']),'donor_id':donor['id'],'session_id':s['id'],'session_type':s['stimulus_name'],'sex':donor['sex'],'genotype':donor['full_genotype'],'historical_overlap':str(s['specimen_id']) in history,'prior_Final_protected':str(s['specimen_id']) in protected,'anatomical_VISp_units':sum(r['anatomical_units'] for r in rows),'max_sameprobe_qualified_VISp':max(r['qualified_units'] for r in rows),'selected_probe':role['probe_id'] if role else None,'role':role['group'] if role else 'Not_selected','pilot':any(p['session_id']==int(s['id']) for p in pilots),'stimulus_families':'|'.join(read_json_gz(R/f"paper12_native_support1/metadata/native_headers/{s['id']}.json.gz")['all_interval_names'])})
    reasons=Counter()
    for u in units:
        for key,lower,upper in [('amplitude_cutoff',0,math.inf),('presence_ratio',0,1),('isi_violations',0,math.inf)]:
            try: x=float(u[key]); valid=math.isfinite(x) and lower<=x<=upper
            except (ValueError,TypeError,KeyError): valid=False
            if not valid: reasons[key+'_source_invalid']+=1
    summary={'mission':MISSION,'computed_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'registration_sha256':freeze['registration_sha256'],'source_sessions':len(sessions),'source_mice':inventory['source_mice'],'source_probes':len(probes),'source_channels':len(channels),'source_units':len(units),'anatomical_VISp_mice':len({r['mouse_id'] for r in populations if r['anatomical_units']>0}),'tiers':tiers,'selected_mice':len(roles),'Development':sum(r['group']=='Development' for r in roles),'Final_candidates':sum(r['group']=='Final_candidate' for r in roles),'historical_mouse_overlap':sum(r['historical_source_overlap'] for r in roles),'historical_roster_sha256':sha256(roster_path),'source_validity_invalid_metric_counts_all_regions_nonexclusive':dict(reasons),'invalid_probe_rates':sum(not r['source_probe_valid'] for r in populations),'pilot_bytes_declared':sum(r['declared_bytes'] for r in pilot_rows),'neural_arrays_opened':0,'role_composition':{group:dict(Counter(r['session_type'] for r in roles if r['group']==group)) for group in ['Development','Final_candidate']}}
    dump_json(P/'results/METADATA_SUMMARY.json',summary); dump_json(P/'results/POPULATION_INVENTORY.json',inventory); dump_json(P/'results/ROLE_ALLOCATION.json',roles); dump_json(P/'results/PILOT_METADATA_SELECTION.json',pilot_rows)
    csv_out(P/'tables/all_mouse_sessions.csv',disposition)
    csv_out(P/'tables/all_probe_populations.csv',[{k:v for k,v in r.items() if k!='qualified_unit_ids'} for r in populations])
    dump_json(P/'metadata/METADATA_ACTIVE_BINDING.json',{'registration_sha256':freeze['registration_sha256'],'inputs':{n:sha256(P/'metadata'/f'{n}.body') for n in bodies},'historical_roster':{'path':roster_path.relative_to(R).as_posix(),'sha256':sha256(roster_path)},'prior_object_descriptors':sha256(R/'paper12/metadata/allen_header_capability.json')})
    print(summary); print('PILOTS',[(r['mouse_id'],r['session_id'],r['probe_id'],r['declared_bytes']) for r in pilot_rows])

def read_json_gz(path):
    import json
    return json.loads(gzip.decompress(path.read_bytes()))

if __name__=='__main__': main()

