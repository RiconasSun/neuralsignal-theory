"""Canonical-only saved metadata capacities, with observation UNKNOWN explicit."""
import csv,json,re
from pathlib import Path
import numpy as np
from .source_metadata import P,ROOT,read,write,verify_history,sha
TP='/intervals/trials/';UP='/units/';EP='/general/extracellular_ephys/electrodes/'

def region(x):
    m=re.fullmatch(r'(MOs|ACAd|ACAv|PL|ILA)(?:1|2/3|4|5|6a|6b)?',str(x))
    return m.group(1) if m else None

def task(values):
    names=['start_time','gabor_stimulus_onset_time','auditory_cue_time','feedback_time','stop_time','probability_left','gabor_stimulus_contrast','gabor_stimulus_side']
    if any(TP+n not in values for n in names):raise ValueError('Missing canonical task field')
    n=len(values[TP+'start_time'])
    if any(len(values[TP+k])!=n for k in names):raise ValueError('Task row mismatch')
    a=np.array([values[TP+k] for k in names[:5]],dtype=float).T
    context=np.asarray(values[TP+'probability_left'],dtype=float)
    contrast=np.asarray(values[TP+'gabor_stimulus_contrast'],dtype=float)
    stim=a[:,1];finite=stim[np.isfinite(stim)];chronological=bool(np.all(np.diff(finite)>0))
    reasons=dict(nonfinite_required_event=~np.isfinite(a).all(axis=1),
      invalid_event_order=~((a[:,0]<=a[:,1])&(a[:,1]<=a[:,2])&(a[:,2]<=a[:,3])&(a[:,3]<=a[:,4])&(a[:,0]<a[:,4])),
      stimulus_window_outside_trial=~(stim+.5<=a[:,4]),
      missing_or_invalid_stimulus=~(np.isfinite(contrast)&(contrast>=0)&(contrast<=100)&np.isin(values[TP+'gabor_stimulus_side'],['left','right'])),
      nonprimary_context=~np.isin(context,[.2,.8]))
    valid=~np.logical_or.reduce(list(reasons.values()));runs=[];membership=np.full(n,-1,dtype=int);previous=None;current=None
    for j,c in enumerate(context):
        if c not in [.2,.8]:previous=None;current=None;continue
        if current is None or c!=previous:
            current=dict(run=len(runs),context=float(c),first_trial=j,last_trial=j,raw_trials=0,valid_trials=0);runs.append(current)
        current['last_trial']=j;current['raw_trials']+=1;current['valid_trials']+=int(valid[j]);membership[j]=current['run'];previous=c
    cut=len(runs)//2;usable=np.zeros(n,dtype=bool)
    for r in runs:
        r.update(half='training' if r['run']<cut else 'evaluation',qualifying=r['valid_trials']>=15)
        if r['qualifying']:usable|=(membership==r['run'])&valid
    cells={f'{c}_{h}':sum(r['valid_trials'] for r in runs if r['context']==c and r['half']==h and r['qualifying']) for c in [.2,.8] for h in ['training','evaluation']}
    qualifying={str(c):sum(r['qualifying'] for r in runs if r['context']==c) for c in [.2,.8]}
    eligible=chronological and all(z>=60 for z in cells.values()) and all(z>=2 for z in qualifying.values())
    source_blocks=values.get(TP+'block_index',[None]*n)
    if len(source_blocks)!=n:raise ValueError('Canonical block identity row mismatch')
    rows=[dict(trial_ordinal=j,canonical_block_index=source_blocks[j],context=None if not np.isfinite(context[j]) else float(context[j]),original_run=int(membership[j]),half=('training' if membership[j]<cut else 'evaluation') if membership[j]>=0 else 'nonprimary',event_valid=bool(valid[j]),contributing_task_window=bool(usable[j]),exclusion_reasons=';'.join(k for k,v in reasons.items() if v[j]),neural_observation_validity='UNKNOWN_NOT_TASK_VALIDITY') for j in range(n)]
    return dict(rows=n,chronological=chronological,original_runs=len(runs),original_cut=cut,cell_trials=cells,qualifying_runs=qualifying,potential_task_capacity=bool(eligible),usable_task_windows=int(usable.sum()),exclusions_nonexclusive={k:int(v.sum()) for k,v in reasons.items()}),runs,rows

def units(values,probe):
    ids=values[UP+'id'];n=len(ids)
    if len(set(ids))!=n:raise ValueError('Duplicate canonical unit IDs')
    for name in ['cluster_uuid','probe_name','max_electrode','ibl_quality_score']:
        if len(values[UP+name])!=n:raise ValueError('Canonical unit property length mismatch')
    if len(set(values[UP+'cluster_uuid']))!=n:raise ValueError('Duplicate canonical unit UUID')
    ne=len(values[EP+'id']);groups=values[EP+'group_name'];coords=np.asarray([values[EP+k] for k in ['x','y','z']],dtype=float).T
    if coords.shape!=(ne,3) or len(groups)!=ne:raise ValueError('Electrode metadata mismatch')
    tables=[]
    for base in ['/general/localization','/general/localization/anatomical_coordinates_tables']:
        for name in ['ElectrodesIBLBregma','ElectrodesCCFv3']:
            prefix=base+'/'+name+'/'
            if prefix+'brain_region' in values:
                indices=np.asarray(values[prefix+'localized_entity'],dtype=float);labels=values[prefix+'brain_region'];probes=values[prefix+'probe_name']
                if len(indices)!=len(labels) or len(indices)!=len(probes) or len(set(indices))!=len(indices) or not np.all(np.isfinite(indices)&(indices==indices.astype(int))&(indices>=0)&(indices<ne)):raise ValueError('Invalid localization-to-electrode map')
                table={int(k):(labels[j],probes[j]) for j,k in enumerate(indices)};tables.append(table)
    if not tables:raise ValueError('No canonical acronym localization mapping')
    for table in tables[1:]:
        for k in set(table)&set(tables[0]):
            if table[k]!=tables[0][k]:raise ValueError('Canonical localization table conflict')
    mapping=tables[0];out=[];composition={};selected_probe=probe.casefold()
    quality=np.asarray(values[UP+'ibl_quality_score'],dtype=float)
    for j,k in enumerate(values[UP+'max_electrode']):
        if not isinstance(k,(int,float)) or not np.isfinite(k) or k!=int(k) or not 0<=k<ne:raise ValueError('Invalid max_electrode index')
        k=int(k);p=values[UP+'probe_name'][j]
        if p!=groups[k]:raise ValueError('Unit/electrode probe mismatch')
        if k not in mapping or mapping[k][1]!=p:raise ValueError('Unit/localization probe mismatch')
        leaf=mapping[k][0];parent=region(leaf);target=parent is not None
        good=bool(quality[j]==1. and np.isfinite(coords[k]).all())
        selected=p.casefold()==selected_probe and target and good
        if selected:composition[leaf]=composition.get(leaf,0)+1
        out.append(dict(unit_ordinal=j,unit_id=ids[j],cluster_uuid=values[UP+'cluster_uuid'][j],canonical_probe=p,max_electrode=k,canonical_leaf=leaf,parent=parent,canonical_quality=None if not np.isfinite(quality[j]) else float(quality[j]),finite_coordinates=bool(np.isfinite(coords[k]).all()),target=target,qualified_target_on_frozen_probe=selected))
    qualified=sum(composition.values());mos=sum(v for k,v in composition.items() if region(k)=='MOs')
    return dict(canonical_units=n,canonical_probes=sorted(set(values[UP+'probe_name'])),frozen_probe_present=selected_probe in {x.casefold() for x in values[UP+'probe_name']},provider_quality_available=True,qualified_target_units=qualified,composition=composition,MOs_units=mos,MOs_fraction=mos/qualified if qualified else None,MOs_majority=mos>qualified/2 if qualified else None,exclusively_MOs=mos==qualified if qualified else None,non_MOs_units=qualified-mos,potential_unit_capacity=qualified>=10,unit_mapping='Canonical max_electrode ->localized_entity->brain_region/probe, no oldunit/atlas/QC import'),out

def support_inventory(export):
    values=export['values'];paths=set(values)
    obs=[p for p in paths if p.startswith('/units/obs_intervals') or p.startswith('/intervals/observation_intervals/') or p.startswith('/intervals/valid_times/')]
    artifact=[p for p in paths if any(p.startswith('/intervals/'+t+'/') for t in ['invalid_times','artifact_intervals','bad_intervals','saturation_intervals'])]
    intervals=sorted({p.split('/')[2] for p in paths if p.startswith('/intervals/')})
    return dict(neural_recording_coverage='UNKNOWN' if not obs else 'PRESENT_REQUIRES_SCOPE_CLOCK_COMPLETENESS_REVIEW',
      documented_artifact_validity='UNKNOWN' if not artifact else 'PRESENT_REQUIRES_SCOPE_CLOCK_COMPLETENESS_REVIEW',
      observation_fields=sorted(obs),artifact_fields=sorted(artifact),interval_tables=intervals,
      task_epoch_present='epochs' in intervals,task_epoch_not_neural_coverage=True,
      old_bwm_present=TP+'bwm_include' in paths,old_saturation_present=TP+'saturation_stim_plus06' in paths,
      source_support_eligible=None,reason='No recording/artifact PASS inferred from task epochs, unit quality, absence of annotation, or undocumented empty table. Documentary semantics require independent review.')

def validate_references(export):
    references=[r for r in export['schema'] if r['path']==UP+'max_electrode' or r['path'].endswith('/localized_entity')]
    if not references:raise ValueError('Missing canonical table references')
    for row in references:
        if row.get('attrs',{}).get('table')!=EP.rstrip('/') or row.get('attrs',{}).get('neurodata_type')!='DynamicTableRegion':raise ValueError('Canonical localization/peak electrode references wrong table')

def verify_subject(record,export,official):
    actual=export['values']['/general/subject/subject_id']
    participants={z['identifier'] for z in official['wasAttributedTo'] if z.get('schemaKey')=='Participant'}
    if actual!=record['mouse'] or participants!={actual} or actual.replace('_','-')!=record['canonical_subject']:raise ValueError('Canonical subject / official participant / filename alias mismatch')
    return actual

def csvfile(path,rows):
    with path.open('x',encoding='utf8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)

def run(out):
    verify_history();out=Path(out);out.mkdir(parents=True,exist_ok=True)
    records=read(P/'SOURCE_AUDIT_ROSTER.json')['records'];summaries=[];animalrows=[];trialrows=[];unitrows=[];runrows=[]
    for r in records:
        a=r['asset'];x=read(P/'metadata/values'/(a['asset_id']+'.json'));v=x['values']
        if x['eid']!=r['eid'] or x['asset_id']!=a['asset_id'] or x['source_asset_path']!=a['path']:raise ValueError('Canonical source identity mismatch')
        official=read(P/'sources'/('asset_'+a['asset_id']+'.json'))
        actual_subject=verify_subject(r,x,official)
        if official['identifier']!=a['asset_id'] or official['path']!=a['path'] or official['contentSize']!=a['size'] or official['digest']['dandi:dandi-etag']!=x['etag'].strip('"'):raise ValueError('Official immutable asset metadata/range mismatch')
        if r['eid'] not in {z.get('identifier') for z in official['wasGeneratedBy'] if z.get('schemaKey')=='Session'}:raise ValueError('Canonical session provenance mismatch')
        validate_references(x)
        ts,rs,tr=task(v);us,ur=units(v,r['probe']);ss=support_inventory(x)
        potential=ts['potential_task_capacity'] and us['potential_unit_capacity']
        summaries.append(dict(mouse=r['mouse'],canonical_subject=actual_subject,DANDI_path_subject=r['canonical_subject'],eid=r['eid'],pid=r['pid'],historical_probe=r['probe'],asset_id=a['asset_id'],task=ts,units=us,support=ss,potential_task_anatomy_capacity=potential))
        failure=[]
        if not ts['potential_task_capacity']:failure.append('canonical_task_coverage_failed')
        if not us['potential_unit_capacity']:failure.append('canonical_target_unit_floor_failed')
        if ss['source_support_eligible'] is None:failure.append('neural_observation_and_artifact_validity_UNKNOWN')
        animalrows.append(dict(mouse=r['mouse'],canonical_subject=actual_subject,DANDI_path_subject=r['canonical_subject'],eid=r['eid'],pid=r['pid'],probe=r['probe'],asset_id=a['asset_id'],canonical_units=us['canonical_units'],provider_QC='canonical_ibl_quality_score',qualified_target_units=us['qualified_target_units'],MOs_units=us['MOs_units'],MOs_fraction=us['MOs_fraction'],non_MOs_units=us['non_MOs_units'],leaf_composition=json.dumps(us['composition'],sort_keys=True),**ts['cell_trials'],qualifying_runs_02=ts['qualifying_runs']['0.2'],qualifying_runs_08=ts['qualifying_runs']['0.8'],potential_task_anatomy_capacity=potential,neural_coverage=ss['neural_recording_coverage'],artifact_validity=ss['documented_artifact_validity'],source_support_eligible='UNKNOWN',physiological_eligible='NOT_MEASURED',reason=';'.join(failure)))
        for z in tr:trialrows.append(dict(mouse=r['mouse'],eid=r['eid'],**z))
        for z in ur:unitrows.append(dict(mouse=r['mouse'],eid=r['eid'],**z))
        for z in rs:runrows.append(dict(mouse=r['mouse'],eid=r['eid'],**z))
    if len({r['mouse'] for r in records})!=len(records) or len({r['canonical_subject'] for r in records})!=len(records):raise ValueError('Duplicate independent mouse/canonical subject')
    potential=sum(r['potential_task_anatomy_capacity'] for r in summaries)
    all_unknown=all(r['support']['source_support_eligible'] is None for r in summaries)
    result=dict(mission='P14-V2-CANONICAL-NATIVE-RECOVERY',scientific_decision='SOURCE_CONTRACT_INCONCLUSIVE',
        rationale='Recording coverage and source-defined artifact validity remain unverified; unknown is not zero eligible animals or DATA_INSUFFICIENT.',
        historical_frame_mice=13,canonical_metadata_audited_mice=len(records),previously_unread_sessions_now_audited=12,
        potential_task_anatomy_mice=potential,fully_source_support_certified_mice=0,source_support_eligible_mice=None,
        support_unknown_mice=sum(r['support']['source_support_eligible'] is None for r in summaries),physiological_eligible_mice=None,
        conditional_capacity_label='>=8 potential exploratory capacity' if potential>=8 else '6-7 potential descriptive capacity' if potential>=6 else '<6 task-anatomy capacity within historicalframe only',
        capacity_label_is_not_admission=True,sourcewide_enumeration_activated=False,
        sourcewide_not_activated_reason='Critical observation contract unresolved; source-wide capacity counting cannot supply missing recording/artifact provenance.',
        all_support_unknown=all_unknown,all_old_masks_not_transferred=True,movement_used_for_eligibility_or_models=False,
        movement_independence_claim_permanently_withheld=True,historical_1e_minus6_tolerance_unchanged=True,neural_datasets_or_shapes_opened=False,
        neural_QC=False,model_fits=0,model_selection=False,predictive_scores=0,temporal_evaluations=0,M1_protocol_complete=False,
        recommendation='Archive this P14 route; no automatic source search, bridge-rescue or neural activation.',
        summaries=summaries)
    write(out/'CANONICAL_NATIVE_DECISION.json',result)
    csvfile(out/'ANIMAL_EXCLUSION_MATRIX.csv',animalrows);csvfile(out/'TRIAL_EXCLUSIONS.csv',trialrows);csvfile(out/'CANONICAL_UNIT_MAPPING.csv',unitrows);csvfile(out/'ORIGINAL_BLOCKS.csv',runrows)
    verify_history();return result

if __name__=='__main__':
    import sys
    result=run(Path(sys.argv[1]) if len(sys.argv)>1 else P/'results/audit')
    print(json.dumps({k:v for k,v in result.items() if k!='summaries'},sort_keys=True))
