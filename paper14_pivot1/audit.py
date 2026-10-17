"""Preregistered atlas/quality/task metadata screening, never neural prediction."""
import collections,gzip,hashlib,json,re
from pathlib import Path
import pandas as pd
from .retrieve import P,read,write,sha
R=P.parent
LEAVES=('MOs','ACAd','ACAv','PL','ILA')
def verify():
    hashes=read(P/'INPUT_FREEZE.json')['hashes']
    for name,h in hashes.items():
        if sha((R/name).read_bytes())!=h:raise ValueError('Historical input changed: '+name)
    return len(hashes)
def region(label):
    m=re.fullmatch(r'(MOs|ACAd|ACAv|PL|ILA)(?:1|2/3|4|5|6a|6b)?',str(label));return m[1] if m else None
def table(out,name,rows):
    f=rows if isinstance(rows,pd.DataFrame) else pd.DataFrame(rows)
    raw=f.to_csv(index=False,lineterminator='\n').encode();(out/name).write_bytes(gzip.compress(raw,mtime=0) if name.endswith('.gz') else raw)
def asset_metadata():
    allrows=[]
    for i in range(1,4):
        x=read(P/'sources'/f'assets_page{i}.json');allrows+=x['results']
        # The API supplies the total on page1 and null on subsequent pages.
        if (i==1 and x['count']!=2048) or (i>1 and x['count'] not in (None,2048)):raise ValueError('Unexpected release count; preserve and review')
    if len(allrows)!=2048 or len({a['asset_id'] for a in allrows})!=2048:raise ValueError('Missing/duplicate asset page')
    if read(P/'sources/assets_page3.json')['next'] is not None:raise ValueError('Incomplete release pagination')
    version=read(P/'sources/release.json')
    if version['identifier']!='DANDI:000409' or version['version']!='0.260309.1324' or version['license']!=['spdx:CC-BY-4.0']:raise ValueError('Wrong source license/version')
    if version['access'][0]['status']!='dandi:OpenAccess':raise ValueError('Nonpublic source')
    return allrows
def subject_crosswalk(fixture,processed):
    """Observed UUID-bound bijection, independently supported by converter source.

    Subject string normalization alone never authorizes joining two animals.
    """
    procmap=collections.defaultdict(list)
    for a in processed:procmap[a['eid']].append(a)
    forward={};reverse={};rows=[]
    for f in fixture.drop_duplicates('eid').itertuples():
        matches=procmap.get(f.eid,[])
        if len(matches)!=1:raise ValueError('Missing/duplicate processed session UUID')
        a=matches[0];canonical=a['subject']
        if canonical!=f.subject.replace('_','-'):raise ValueError('Source-unsupported subject mapping')
        if f.subject in forward and forward[f.subject]!=canonical:raise ValueError('Ambiguous animal alias')
        if canonical in reverse and reverse[canonical]!=f.subject:raise ValueError('Canonical name collision; no animal merge')
        forward[f.subject]=canonical;reverse[canonical]=f.subject
        rows.append(dict(mouse=f.subject,canonical_DANDI_subject=canonical,eid=f.eid,lab=f.lab,processed_asset_count=1,literal_subject_match=canonical==f.subject,match='EXACT_SESSION_UUID_SOURCE_VERIFIED_SUBJECT_BIJECTION',asset_ids=a['asset_id'],unit_QC_version_equivalence='NOT_ESTABLISHED_BY_IDENTITY_JOIN',no_NWB_values_read=True))
    if set(procmap)!={r['eid'] for r in rows}:raise ValueError('Extra DANDI processed session outside registered fixture')
    return rows,[dict(IBL_subject=k,DANDI_subject=v,method='Observed exact-sessionUUID-bijection plus pinned converter underscore-to-hyphen rule') for k,v in sorted(forward.items())]
def run(out=None):
    history=verify()
    # Package files are hash-verified above before importing the frozen policy.
    from paper14_m0.audit import session_blocks
    out=Path(out) if out else P/'results';out.mkdir(parents=True,exist_ok=True)
    fixture=pd.read_csv(R/'paper13/metadata/fixture.csv',dtype=str)
    if fixture.pid.duplicated().any() or fixture.groupby('eid').subject.nunique().max()!=1:raise ValueError('Probe/session identity ambiguity')
    clusters=pd.read_csv(R/'paper13/metadata/clusters_metadata.csv.gz',dtype={'pid':str,'eid':str,'uuids':str})
    if clusters[['pid','cluster_id']].duplicated().any() or clusters.uuids.duplicated().any():raise ValueError('Duplicate unit identities')
    atlas={int(a['id']):a['acronym'] for a in read(R/'paper13/metadata/atlas.json')['msg']}
    clusters['leaf']=clusters.atlas_id.map(atlas).map(region)
    trial=pd.read_csv(R/'paper13/metadata/trials_metadata.csv.gz',float_precision='round_trip')
    if not set(clusters.pid)<=set(fixture.pid) or not set(trial.eid)<=set(fixture.eid):raise ValueError('Unregistered trial/probe source')
    context=[];masks=[];blocks=[];summaries={}
    for eid,f in trial.groupby('eid',sort=True):
        summary,runs,usable=session_blocks(f);summaries[eid]=summary
        for r in runs:blocks.append(dict(eid=eid,**r))
        for j,u in enumerate(usable):masks.append(dict(eid=eid,trial_ordinal=j,usable=bool(u)))
        for ctx,c in summary['counts'].items():context.append(dict(eid=eid,probabilityLeft=ctx,eligible=summary['eligible'],chronological=summary['chronological'],**c))
    counts={}
    for pid,f in clusters.groupby('pid',sort=False):
        counts[pid]={leaf:int((f.leaf.eq(leaf)&f.label.eq(1)).sum()) for leaf in LEAVES}
    probes=[]
    for f in fixture.itertuples():
        s=summaries[f.eid];c=counts.get(f.pid,dict.fromkeys(LEAVES,0));total=sum(c.values());strict=total-c['MOs'];cell=min(z[k] for z in s['counts'].values() for k in ['calibration_trials','scoring_trials'])
        probes.append(dict(mouse=f.subject,lab=f.lab,eid=f.eid,pid=f.pid,probe=f.probe_name,date=f.date,**c,expanded_good_units=total,strict_good_units=strict,MOs_fraction=c['MOs']/total if total else None,MOs_dominated=bool(total and c['MOs']/total>.5),minimum_context_half_trials=cell,context_metadata_pass=s['eligible'],expanded_metadata_eligible=bool(total>=10 and s['eligible']),strict_metadata_eligible=bool(strict>=10 and s['eligible']),unit_screen='Provider label==1; not A/Cphysiology',support='Curated task/saturation metadata only; actual neural support/clock still separate',exclusion_reasons=';'.join(([ 'fewer_than10_same_probe_provider_good_target_units'] if total<10 else [])+(['context_half_run_or_clock_metadata_failure'] if not s['eligible'] else []))))
    pf=pd.DataFrame(probes)
    rank=pf.sort_values(['expanded_metadata_eligible','expanded_good_units','minimum_context_half_trials','eid','pid'],ascending=[False,False,False,True,True])
    chosen=rank.drop_duplicates('mouse').sort_values('mouse');eligible=chosen[chosen.expanded_metadata_eligible]
    old=read(R/'paper14_m0/results/IBL_AUDIT.json')['regions']['mPFC_composite'];strict_ids=sorted(pf.loc[pf.strict_metadata_eligible,'mouse'].unique())
    if strict_ids!=sorted(old['selected_eligible_mice']) or len(strict_ids)!=8:raise ValueError('Historical strict8 not reproduced; stop')
    assets=asset_metadata();dandi=[]
    for a in assets:
        match=re.search(r'(?:^|/)sub-([^/]+)_ses-([0-9a-f-]{36})_',a['path'])
        if match:
            dandi.append(dict(subject=match[1],eid=match[2],asset_id=a['asset_id'],path=a['path'],size=a['size'],neural_values_read=False))
    processed=[a for a in dandi if a['path'].endswith('_desc-processed_behavior+ecephys.nwb')]
    joins,crosswalk=subject_crosswalk(fixture,processed)
    canonical={r['IBL_subject']:r['DANDI_subject'] for r in crosswalk}
    chosen=chosen.assign(canonical_DANDI_subject=chosen.mouse.map(canonical))
    eligible=chosen[chosen.expanded_metadata_eligible]
    table(out,'ALL_PROBE_COMPOSITION.csv',pf);table(out,'SELECTED_MOUSE_PROBES.csv',chosen);table(out,'EXPANDED_METADATA_CANDIDATES.csv',eligible)
    table(out,'CONTEXT_HALF_COVERAGE.csv',context);table(out,'ORIGINAL_BLOCKS.csv',blocks);table(out,'TRIAL_METADATA_MASKS.csv.gz',masks)
    table(out,'DANDI_SESSION_IDENTITY_JOIN.csv',joins);table(out,'DANDI_RELEASE_ASSET_IDENTITIES.csv',dandi);table(out,'SUBJECT_IDENTITY_CROSSWALK.csv',crosswalk)
    support=[]
    for f in eligible.itertuples():
        t=trial[trial.eid.eq(f.eid)];s=summaries[f.eid]
        support.append(dict(mouse=f.mouse,canonical_DANDI_subject=canonical[f.mouse],eid=f.eid,pid=f.pid,trial_rows=len(t),first_movement_field_present='firstMovement_times' in t,response_field_present='response_times' in t,missing_first_movement=int(t.firstMovement_times.isna().sum()),missing_response_time=int(t.response_times.isna().sum()),original_finite_stimulus_order_verified=s['chronological'],retained_windows_pass_frozen_event_order=s['eligible'],curated_task_and_saturation_screen=s['eligible'],provider_neural_QC='label1 externally curated full-session frame, not A/Cphysiology',wheel='Official converter event-driven encoder position and wheel-movement interfaces; actual per-session sampling/availability not read',lick='Official converter video/pose-derived Events; actual availability/alignment not measured',movement='Discrete firstMovement_times present; current/future choice/reward never causal pre-event predictors',timebase='Provider synchronized ephys-clock documentation; no independent per-session residual or packet-loss verification',observation_support='Curated within-trial window/saturation metadata, not a neural observation-interval or packet completeness certificate',release_equivalence='Session/animal identity proved; unit/QC/trial version equality NOT proved',new_mask_or_imputation=False))
    table(out,'SOURCE_TIMING_BEHAVIOR_MATRIX.csv',support)
    anatomical_good=int(pf.loc[pf.expanded_good_units>=10,'mouse'].nunique());n=int(len(eligible));mice=len(chosen)
    result=dict(mission='P14-M1-BOUNDED-CONTEXT-PIVOT',scientific_decision='DATA_INSUFFICIENT' if n<16 else 'FEASIBLE_BUT_PROTOCOL_INCOMPLETE',decision_scope='Prospectively fixed reused2024_Q2IBL metadata screening route; not a global claim for every DANDI processed-unit version',new_context='probabilityLeft0.2vs0.8; scheduled prior, not beliefs',target='medial frontal cortex MOs+ACAd+ACAv+PL+ILA, same probe',source='DANDI000409/0.260309.1324; reused IBL2024_Q2aggregate compatibility audit',all_source_mice=mice,all_source_probes=len(pf),strict_historical_candidates=8,strict_historical_mouse_ids=strict_ids,expanded_mice_with10_good_units=anatomical_good,expanded_context_metadata_candidates=n,expanded_mouse_ids=eligible.mouse.tolist(),expanded_MOs_dominated_mice=int(eligible.MOs_dominated.sum()),expanded_without_MOs_still10_units=int((eligible.strict_good_units>=10).sum()),minimum_total=16,metadata_capacity_8_plus_8=n>=16,actual_development_final_allocation=None,actual_physiological_QC=None,source_processed_assets=len(processed),source_session_subject_UUID_matches=len(joins),source_literal_subject_matches=sum(r['literal_subject_match'] for r in joins),canonical_independent_subjects=len(crosswalk),source_unit_QC_version_equivalence=False,full_M1_protocol_frozen=False,Prompt3_eligible=False,neural_arrays_read=0,raw_behavior_values_read=0,model_fits=0,predictive_scores=0,final_evaluations=0,historical_hashes=history,archive_recommendation=n<16)
    write(out/'PIVOT_DECISION.json',result);return result
if __name__=='__main__':print(json.dumps(run(),indent=2))
