"""Saved whitelisted metadata audit; no network, HDF5 or neural-array access."""
import csv, json
from pathlib import Path
import numpy as np
import pandas as pd
from .source_metadata import P, ROOT, read, write, verify_history

TOL=1e-6  # Prospectively fixed serialization comparison, never a clock correction.
TIME_MAP={
    'start_time':'intervals_0','stop_time':'intervals_1',
    'gabor_stimulus_onset_time':'stimOn_times','auditory_cue_time':'goCue_times',
    'wheel_movement_onset_time':'firstMovement_times',
    'choice_registration_time':'response_times','feedback_time':'feedback_times',
    'gabor_stimulus_offset_time':'stimOff_times'}

def numeric(a,b,tolerance=TOL):
    a=np.asarray(a,dtype=float);b=np.asarray(b,dtype=float)
    if a.shape!=b.shape:raise ValueError('Original trial rows cannot be reordered/truncated')
    finite=np.isfinite(a)&np.isfinite(b)
    missing=np.isfinite(a)!=np.isfinite(b)
    bad=missing|(finite&(np.abs(a-b)>tolerance))
    return dict(rows=len(a),mismatches=int(bad.sum()),missingness_mismatches=int(missing.sum()),
                canonical_missing=int((~np.isfinite(a)).sum()),old_missing=int((~np.isfinite(b)).sum()),
                max_abs_difference=float(np.max(np.abs(a[finite]-b[finite]))) if finite.any() else None,
                match=not bool(bad.any())),bad

def categories(a,b):
    if len(a)!=len(b):raise ValueError('Original categorical row count mismatch')
    bad=[x!=y for x,y in zip(a,b)]
    return dict(rows=len(a),mismatches=sum(bad),match=not any(bad))

def bridge_pass(fields,identity):
    # All available curatorial fields and missingness must agree. No best-field subset.
    return bool(identity and fields and all(s['match'] for s in fields.values()))

def run(out):
    verify_history();out=Path(out);out.mkdir(parents=True,exist_ok=True)
    roster=read(P/'SOURCE_AUDIT_ROSTER.json')['records'];r=roster[0]
    v=read(P/'metadata/values'/(r['asset']['asset_id']+'.json'))
    x=v['values'];tp='/intervals/trials/';up='/units/';ep='/general/extracellular_ephys/electrodes/'
    old=pd.read_csv(ROOT/'paper13/metadata/trials_metadata.csv.gz',float_precision='round_trip')
    old=old[old.eid==r['eid']].reset_index(drop=True)
    extra=pd.read_csv(ROOT/'paper14_m0/metadata/IBL_trials_metadata.csv.gz',float_precision='round_trip')
    extra=extra[extra.eid==r['eid']].reset_index(drop=True)
    if len(old)!=len(extra):raise ValueError('Historical behavioral annotation rows inconsistent')
    identity=(v['eid']==r['eid'] and v['asset_id']==r['asset']['asset_id'] and
              v['source_asset_path']==r['asset']['path'] and x['/general/subject/subject_id']==r['canonical_subject'])
    fields={};rows=[]
    for new,name in TIME_MAP.items():
        b=old[name] if name in old else extra[name]
        fields[new],bad=numeric(x[tp+new],b)
        for j in range(len(old)):
            a=x[tp+new][j];z=b.iloc[j]
            rows.append(dict(mouse=r['mouse'],eid=r['eid'],trial_ordinal=j,field=new,
                canonical=a,old=None if pd.isna(z) else float(z),mismatch=bool(bad[j]),
                old_bwm_include=bool(old.bwm_include.iloc[j]),old_saturation_stim_plus06=bool(old.saturation_stim_plus06.iloc[j])))
    fields['probability_left'],_=numeric(x[tp+'probability_left'],old.probabilityLeft,tolerance=0.)
    fields['mouse_wheel_choice']=categories(x[tp+'mouse_wheel_choice'],extra.choice.map({-1.:'counter_clockwise',0.:'none',1.:'clockwise'}).where(extra.choice.notna(),None).tolist())
    fields['is_mouse_rewarded']=categories(x[tp+'is_mouse_rewarded'],extra.feedbackType.eq(1.).tolist())
    fields['reward_volume_uL'],_=numeric(x[tp+'reward_volume_uL'],extra.rewardVolume)
    l=extra.contrastLeft.to_numpy();q=extra.contrastRight.to_numpy()
    if np.any(np.isfinite(l)&np.isfinite(q)):raise ValueError('Ambiguous original stimulus side')
    side=['left' if np.isfinite(a) else 'right' if np.isfinite(b) else None for a,b in zip(l,q)]
    fields['gabor_stimulus_side']=categories(x[tp+'gabor_stimulus_side'],side)
    fields['gabor_stimulus_contrast'],_=numeric(x[tp+'gabor_stimulus_contrast'],np.where(np.isfinite(l),l,q)*100)
    units=pd.read_csv(ROOT/'paper13/metadata/clusters_metadata.csv.gz',float_precision='round_trip')
    units=units[units.eid==r['eid']].set_index('uuids')
    if not units.index.is_unique:raise ValueError('Ambiguous historical unit UUID')
    ids=x[up+'cluster_uuid'];indices=np.asarray(x[up+'max_electrode']);groups=x[ep+'group_name']
    uuid_complete=len(set(ids))==len(ids) and set(ids)==set(units.index)
    inbounds=bool(np.all(indices>=0)&np.all(indices<len(groups))&np.all(indices==indices.astype(int)))
    probe_match=inbounds and all(x[up+'probe_name'][j]==groups[k] for j,k in enumerate(indices.astype(int)))
    qc_equal=uuid_complete and bool(np.allclose(np.asarray(x[up+'ibl_quality_score']),units.loc[ids,'label'],rtol=0,atol=1e-12))
    absent=[n for n in ['bwm_include','saturation_stim_plus06'] if tp+n not in x]
    bridge=bridge_pass(fields,identity)
    result=dict(mission='P14-V2-EXPLORATORY-CONTEXT-DYNAMICS',
        source_compatibility='SOURCE_CONTRACT_INCONCLUSIVE' if absent and not bridge else 'REQUIRES_COMPLETE_SOURCE_REVIEW',
        reason='Canonical required source masks absent; registered full curatorial-event equivalence bridge fails. No mask transfer authorized.' if absent and not bridge else 'No automatic source or scientific PASS.',
        audit_assets_planned=13,audit_assets_completed=1,remaining_assets_not_read=12,
        canonical_cohort_count=None,admitted_canonical_mice=0,physiological_eligible_mice=None,
        original_historical_metadata_candidates=13,mouse=r['mouse'],eid=r['eid'],asset_id=r['asset']['asset_id'],
        subject_asset_session_identity=identity,trial_rows=len(old),fields=fields,
        missing_canonical_masks=absent,annotation_bridge_pass=bridge,
        first_movement_mismatches_old_included=sum(1 for z in rows if z['field']=='wheel_movement_onset_time' and z['mismatch'] and z['old_bwm_include']),
        unit_metadata=dict(rows=len(ids),uuid_set_matches_old=uuid_complete,quality_labels_match_uuid=qc_equal,
            electrode_indices_inbounds=inbounds,unit_electrode_probe_consistent=probe_match,
            anatomical_leaf_translation_and_source_sorting_writer_not_fully_certified=True,
            target_eligibility_counts_not_computed=True),
        no_claim_of_global_source_insufficiency=True,old_mask_values_not_transferred=True,
        neural_values_decoded=False,physiological_qc_executed=False,fits=0,scores=0,late_evaluation_accessed=False)
    write(out/'SOURCE_COMPATIBILITY.json',result)
    with (out/'TRIAL_EVENT_COMPARISON.csv').open('x',encoding='utf8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
    verify_history();return result

if __name__=='__main__':
    import sys
    a=run(Path(sys.argv[1]) if len(sys.argv)>1 else P/'results/source_gate')
    print(json.dumps(a,sort_keys=True))
