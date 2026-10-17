"""Recompute source/identity/anatomy upper bounds from saved metadata only."""
import collections
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path
import pandas as pd
from .retrieve import P,read,write,sha
from .inventory import selected,session,versions,public
from .columns import decode,region

R=P.parent
NS={'s':'http://s3.amazonaws.com/doc/2006-03-01/'}

def csv(out,name,rows):
    pd.DataFrame(rows).to_csv(out/name,index=False,lineterminator='\n')

def verify_history():
    hashes=read(P/'INPUT_FREEZE.json')['hashes']
    for path,h in hashes.items():
        if sha((R/path).read_bytes())!=h:raise ValueError('Historical evidence changed: '+path)
    return len(hashes)

def catalog_pages():
    pages=[read(P/'sources/dynamic_routing_public_all_assets.json'),read(P/'sources/dynamic_routing_public_all_assets_skip500.json')]
    if len(pages[0])!=500 or not isinstance(pages[1],list) or len(pages[1])>=500:raise ValueError('Incomplete public metadata pagination')
    rows=pages[0]+pages[1]
    if len({a['_id'] for a in rows})!=len(rows):raise ValueError('Duplicate paginated assets')
    if not all(public(a) for a in rows):raise ValueError('Unexpected bucket/license or asset identity')
    repeat=read(P/'sources/public_catalog_sorted_skip0.json')+read(P/'sources/public_catalog_sorted_skip500.json')
    if len(repeat)!=len(rows) or {a['_id'] for a in repeat}!={a['_id'] for a in rows}:raise ValueError('Independent sorted catalog changed')
    # Five historical descriptions use the literal absence marker "None".
    # No other free-text restriction is treated as empty or waived.
    if any(a['data_description'].get('restrictions') not in (None,'None') for a in rows):raise ValueError('License restriction conflict')
    return rows

def listing(sid):
    root=ET.fromstring((P/'sources'/f'{sid}_listing.xml').read_bytes())
    return [v.text for v in root.findall('.//s:Key',NS)],root.find('s:IsTruncated',NS).text=='true'

def conservative_mouse_upper(rows):
    states=collections.defaultdict(list)
    for row in rows:states[row['mouse']].append(row['anatomy_status'])
    return sum(any(s!='FAIL_REGISTERED_ANATOMY_QC' for s in items) for items in states.values())

def run(out=None):
    verify_history();out=Path(out) if out else P/'results';out.mkdir(parents=True,exist_ok=True)
    allrows=catalog_pages();nwb=read(P/'sources/dynamic_routing_nwb_catalog.json')
    publicnwb=[a for a in nwb if public(a)]
    if {a['_id'] for a in publicnwb}!={a['_id'] for a in allrows if '_nwb_' in a['name']}:raise ValueError('Independent catalog projections disagree')
    csv(out,'PUBLIC_ASSET_INVENTORY.csv',[dict(asset_id=a['_id'],mouse=a['data_description']['subject_id'],name=a['name'],location=a['location'],license=a['data_description']['license'],level=a['data_description']['data_level'],modalities=';'.join(v['abbreviation'] for v in a['data_description']['modalities']),source_data=json.dumps(a['data_description'].get('source_data')),selected_for_neural_access=False) for a in allrows])
    originals=pd.read_csv(R/'paper14_m0/results/DR_selected_populations.csv',dtype={'mouse':str}).query("region=='mPFC_composite' and metadata_eligible==True")
    matching=[]
    for old in originals.itertuples():
        same=[a for a in allrows if a['name'].startswith('ecephys_') and a['data_description']['subject_id']==old.mouse]
        exact=[a for a in same if a['name'].startswith('ecephys_'+old.session+'_')]
        exactnwb=[a for a in exact if '_nwb_' in a['name']]
        matching.append(dict(mouse=old.mouse,original_session=old.session,original_probe=old.probe,status='EXACT_SESSION_MATCH' if exact else ('SAME_MOUSE_DIFFERENT_SESSION' if same else 'NO_VERIFIED_MATCH'),match_basis='subject/date acquisition-name match; not byte/UUID/probe equivalence' if exact else 'no selected-date match in retrieved complete public project catalog',canonical_exact_asset_ids=';'.join(a['_id'] for a in exact),canonical_exact_NWB_asset_ids=';'.join(a['_id'] for a in exactnwb),other_session_dates=';'.join(sorted({a['name'].split('_')[2] for a in same if a not in exact})),canonical_rights='CC-BY-4.0' if exact else 'NO_SELECTED_OBJECT',scratch_rights_status='RIGHTS_UNRESOLVED_PRESERVED',scratch_canonical_equivalence='NOT_ESTABLISHED',probe_equivalence='NOT_ESTABLISHED',original_metadata_masks_transferred=False))
    csv(out,'ORIGINAL18_CANONICAL_MATCHES.csv',matching)
    descriptors={d['session']:d for d in read(P/'DESCRIPTOR_PATHS.json')}
    anatomy=[];probes=[];timing=[];procrows=[]
    for a in selected():
        sid=session(a);mouse=sid.split('_')[0];keys,trunc=listing(sid)
        hdf=[k for k in keys if k.endswith('.nwb')];status='UNRESOLVED_HDF5_NOT_READ';maximum=None
        counts={};rawcounts={};leaves={}
        if sid in descriptors:
            structures=decode(sid,'units/structure');groups=decode(sid,'units/electrode_group_name');ids=decode(sid,'units/unit_id');qc=decode(sid,'units/is_qc_pass')
            if not len(structures)==len(groups)==len(ids)==len(qc) or len(set(ids.tolist()))!=len(ids):raise ValueError('Canonical unit row identity mismatch')
            for group in sorted(set(str(v) for v in groups)):
                mask=[str(g)==group and region(s) is not None for s,g in zip(structures,groups)]
                rawcounts[group]=sum(mask);counts[group]=sum(bool(m and q) for m,q in zip(mask,qc))
                leaves[group]={leaf:sum(bool(str(g)==group and region(s)==leaf and q) for s,g,q in zip(structures,groups,qc)) for leaf in ['ACAd','ACAv','PL','ILA']}
                probes.append(dict(mouse=mouse,session=sid,asset_id=a['_id'],probe=group,raw_target_rows=rawcounts[group],provider_QC_target_rows=counts[group],**leaves[group],units_with_finite_CCF_and_all_windows_support='NOT_MEASURED',physiological_QC='NOT_RUN'))
            maximum=max(counts.values(),default=0);status='POTENTIAL_ANATOMY_ONLY' if maximum>=10 else 'FAIL_REGISTERED_ANATOMY_QC'
        anatomy.append(dict(mouse=mouse,session=sid,asset_id=a['_id'],location=a['location'],processing_version=versions(a)[0],format='ZARR' if sid in descriptors else ('HDF5' if hdf else 'UNRESOLVED'),anatomy_status=status,max_same_probe_provider_QC_target=maximum,metadata_eligible='NOT_ESTABLISHED',actual_physiological_QC='NOT_RUN',object_listing_truncated=trunc))
        meta=read(P/'sources'/f'{sid}_zmetadata.json')['metadata'] if sid in descriptors else {}
        def descriptor(label):
            candidates=[(k,v) for k,v in meta.items() if k.endswith('/.zarray') and label in k.lower()]
            return json.dumps([dict(path=k,shape=v['shape']) for k,v in candidates],sort_keys=True)
        acq=read(P/'sources'/f'{sid}_acquisition.json')
        if str(acq.get('subject_id'))!=mouse:raise ValueError('Acquisition subject mismatch')
        devices=sorted({z for stream in acq.get('data_streams',[]) for z in stream.get('active_devices',[]) if any(token in z.lower() for token in ['sync','camera','taskcontrol','camstim'])})
        timing.append(dict(mouse=mouse,session=sid,acquisition_start=acq.get('acquisition_start_time'),acquisition_stop=acq.get('acquisition_end_time'),declared_clock_devices=';'.join(devices),running_descriptor=descriptor('running'),lick_descriptor=descriptor('lick'),pupil_descriptor=descriptor('pupil'),trial_schema='PRESENT_NOT_VALUES_READ' if any(k.startswith('intervals/trials/') for k in meta) else 'UNRESOLVED',response_missingness='NOT_MEASURED_CANONICAL_VALUES_NOT_READ',response_handling='Prospective entire-trial exclusion for flagged nonfinite event; never impute',raw_samples_read=False,actual_clock_residuals='UNVERIFIED',realized_sampling_quality='UNVERIFIED',saturation_and_interruptions='UNVERIFIED',physiological_recording_support='UNVERIFIED',activation='STOP_NO_COMPLETE_COHORT'))
        proc=read(P/'sources'/f'{sid}_processing.json')
        for z in proc.get('data_processes',[]):
            if any(t in z.get('process_type','').lower() for t in ['sort','curat','format','annotation']):
                code=z.get('code') or {};procrows.append(dict(mouse=mouse,session=sid,process=z.get('process_type'),url=code.get('url'),version=code.get('version'),start=z.get('start_date_time'),stop=z.get('end_date_time'),source='Released processing.json; missing version is unresolved, not inferred from old scratch'))
    csv(out,'CANONICAL_SESSION_SCREEN.csv',anatomy);csv(out,'CANONICAL_PROBE_ANATOMY_QC.csv',probes);csv(out,'TIMING_BEHAVIOR_23.csv',timing);csv(out,'PROCESSING_PROVENANCE.csv',procrows)
    other=[]
    for d in read(P/'SORTED_DESCRIPTOR_PATHS.json'):
        meta=read(P/'sources'/d['saved_as']).get('metadata',{})
        other.append(dict(key=d['key'],metadata_only=True,unit_array_descriptors=sum(k.startswith('units/') and k.endswith('.zarray') for k in meta),target_structure_field='units/structure/.zarray' in meta,CCF_fields=all('units/'+k+'/.zarray' in meta for k in ['ccf_ap','ccf_dv','ccf_ml']),trial_event_table=any(k.startswith('intervals/trials/') for k in meta),alignment='UNRESOLVED_NO_JOINED_TASK_ANATOMY_CONTRACT',primary_eligible='NOT_ESTABLISHED',descriptor_complete=True,root_listing_complete=False))
    csv(out,'OTHER_SORTED_ROUTE_GAPS.csv',other)
    stats=collections.Counter(r['status'] for r in matching)
    upper=conservative_mouse_upper(anatomy)
    result=dict(mission='P14-M1-OPEN-RELEASE-RECOVERY',scientific_decision='SOURCE_OR_TIMING_INCONCLUSIVE',open_release_license_verified=True,license_scope='Registered aind-open-data asset locations plus CC-BY-4.0 asset declarations and AWS dataset entry; never scratch',original_M0='INCONCLUSIVE_METADATA',original_M1='SOURCE_RIGHTS_BLOCKED',historical_files_verified=verify_history(),public_asset_records=len(allrows),public_ecephys_assets=sum(a['name'].startswith('ecephys_') for a in allrows),public_ecephys_mouse_inventory=len({a['data_description']['subject_id'] for a in allrows if a['name'].startswith('ecephys_')}),raw_inventory_not_cohort=True,canonical_NWB_records=len(publicnwb),canonical_NWB_mice=len({session(a).split('_')[0] for a in publicnwb}),canonical_selected_sessions=len(anatomy),exact_original_date_any_release=stats['EXACT_SESSION_MATCH'],exact_original_date_NWB=sum(bool(r['canonical_exact_NWB_asset_ids']) for r in matching),original_match_status_counts=dict(stats),new_Zarr_anatomy_sessions=len(descriptors),HDF5_sessions_unread=len(anatomy)-len(descriptors),NWB_anatomical_potential_mouse_upper=upper,minimum_independent_total=16,NWB_route_minimum_capacity=upper>=16,NWB_upper_includes_every_unread_session=True,fully_qualified_metadata_mice=None,actual_physiological_QC_mice=None,development_final_allocation=None,scientific_protocol_frozen=False,Prompt3_eligible=False,other_public_raw_sorted_routes='UNRESOLVED_NOT_PROVEN_INSUFFICIENT; no joined independently verified target-unit/context/timing cohort',additional_datasets_screened=1,additional_IBL='Explicitly licensed, but documented left/right visual-prior blocks do not supply frozen auditory-reward vs visual-reward contrast. No IBL unit counts or new neural values.',all18_scratch_recovered=False,neural_values_read=0,raw_behavior_samples_read=0,neural_fits=0,neural_scores=0,final_assessments=0,external_messages=0,stop='Completed bounded source-recovery diagnosis; no executable M1 freeze, no Prompt3, no automatic new search mission')
    write(out/'RECOVERY_DECISION.json',result)
    return result

if __name__=='__main__':print(json.dumps(run(),indent=2))
