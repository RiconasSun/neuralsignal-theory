"""Frozen M1 Final-native task/observation screens; never read spike arrays."""
from .source import load_json
import json
import re
import numpy as np
import pandas as pd
from .source import P, R, dump, roster
from .metadata_access import local_path
from .native_table import encode_table,records,verify_native


def partition(n, development):
    cuts = [0, int(.6*n), int(.8*n), n] if development else [0, int(.6*n), n]
    names = ['A', 'B', 'E'] if development else ['C', 'D']
    roles = np.empty(n, dtype='<U1'); guard = np.ones(n, bool)
    for name, lo, hi in zip(names, cuts[:-1], cuts[1:]):
        roles[lo:hi] = name
    for cut in cuts[1:-1]:
        guard[max(0, cut-1):min(n, cut+1)] = False
    return roles, guard, dict(zip(names, zip(cuts[:-1], cuts[1:])))


def task_masks(tr, support, bad, development, wheel=None):
    n = len(tr); roles, guard, cuts = partition(n, development)
    a,s,g,f,z = [tr[k].to_numpy(float) for k in ['intervals_0','stimOn_times','goCue_times','feedback_times','intervals_1']]
    finite = np.isfinite(np.column_stack((a,s,g,f,z))).all(axis=1)
    order = finite & (a<=s) & (s<=f) & (f<=z) & (a<=g) & (g<=f)
    lo, hi = s-.5, s+.5
    within_trial = (lo>=a) & (hi<=z)
    observed = (lo>=support[0]) & (hi<=support[1])
    behavioral = (s-1>=support[0]) & (hi<=support[1])
    overlap = np.zeros(n, bool)
    for b,e in bad:
        overlap |= (s-1<e) & (hi>b)  # Full behavioral plus neural support.
    nonoverlap = np.ones(n, bool)
    for i in range(1,n):
        if np.isfinite(s[i-1:i+1]).all() and lo[i]<hi[i-1]:
            nonoverlap[i-1:i+1] = False
    left,right = [tr[k].to_numpy(float) for k in ['contrastLeft','contrastRight']]
    contrast = (~(np.isnan(left)&np.isnan(right)) & (np.isnan(left)|((left>=0)&(left<=1)))
                & (np.isnan(right)|((right>=0)&(right<=1))))
    role_support = np.zeros(n, bool)
    for name,(start,stop) in cuts.items():
        if stop>start and np.isfinite([a[start],z[stop-1]]).all():
            role_support[start:stop] = (s[start:stop]-1>=a[start]) & (hi[start:stop]<=z[stop-1])
    wheel_support = np.ones(n, bool)
    if wheel is not None:
        wt,wp = wheel
        assert len(wt)==len(wp) and len(wt)>1
        assert np.isfinite(wt).all() and np.isfinite(wp).all() and (np.diff(wt)>0).all()
        wheel_support = (s-1>wt[0]) & (hi<=wt[-1])
    checks = dict(event_order=order, neural_epoch_inside_trial=within_trial,
        recording_sync_support=observed, behavioral_support=behavioral,
        no_known_saturation=~overlap, no_overlapping_epoch=nonoverlap,
        essential_contrast=contrast, role_support=role_support, boundary_guard=guard,
        wheel_support=wheel_support)
    mask = np.logical_and.reduce(list(checks.values()))
    return roles, mask, checks, cuts


def annotation_audit(entry):
    selected=next(x for x in entry['files'] if x['role']=='saturation')['key']
    probe=entry['files'][0]['probe']
    for item in entry['additional_annotation_catalog']:
        key=item['key']
        if '/raw_ephys_data/' in key and '/raw_ephys_data/'+probe+'/' not in key:continue
        if key!=selected:raise ValueError('Unresolved additional selected-probe/session invalid annotation: '+key)


def run():
    from one.alf.io import load_file_content
    freeze = load_json((P/'SOURCE_FILE_FREEZE.json').read_text(encoding='utf8'))
    assert freeze['all_inventory_pass']
    atlas = {int(x['id']):x['acronym'] for x in load_json((R/'paper13/metadata/atlas.json').read_text(encoding='utf8'))['msg']}
    old = pd.read_csv(R/'paper13/metadata/clusters_metadata.csv.gz', usecols=['pid','cluster_id','uuids','label','atlas_id'])
    rows = {x['eid']:x for x in roster()}; out=[]
    for entry in freeze['subjects']:
        row = rows[entry['eid']]; dev = row['allocation']=='DEVELOPMENT'
        assert not dev, 'Only the eight Final-reserved sources'
        annotation_audit(entry)
        paths = {f['role']:local_path(entry,f) for f in entry['files']
                 if f['role'] not in ('times','clusters')}
        # Provider metrics contain neural summaries: only decode id/label columns.
        metrics = pd.read_parquet(paths['metrics'], columns=['cluster_id','label'])
        cc = np.load(paths['cluster_channels'], allow_pickle=False)
        ca = np.load(paths['atlas'], allow_pickle=False)
        uuids = pd.read_csv(paths['uuids']).iloc[:,-1].astype(str).to_numpy()
        assert np.issubdtype(cc.dtype,np.integer) and len(cc)==len(metrics)==len(uuids)
        assert (cc>=0).all() and (cc<len(ca)).all() and len(set(uuids))==len(uuids)
        assert np.array_equal(metrics.cluster_id.to_numpy(),np.arange(len(metrics)))
        aid = ca[cc]; acr = [atlas.get(int(x)) for x in aid]
        target = np.array([bool(re.fullmatch(r'MOp(?:1|2/3|4|5|6a|6b)?',str(x))) for x in acr])
        good = target & metrics.label.eq(1).to_numpy()
        prior = old[old.pid.eq(row['pid'])].sort_values('cluster_id')
        assert len(prior)==len(metrics) and np.array_equal(prior.uuids.astype(str).to_numpy(),uuids), 'Cluster UUID/source identity contradiction'
        mapping = dict(native_clusters=len(metrics),uuid_order_equal=True,
            label_disagreements=int(np.sum(prior.label.to_numpy()!=metrics.label.to_numpy())),
            atlas_disagreements=int(np.sum(prior.atlas_id.to_numpy()!=aid)),
            native_MOp_provider_good=int(good.sum()))
        meta = dict(line.split('=',1) for line in paths['recording_meta'].read_text(encoding='utf8').splitlines() if '=' in line)
        fs=float(meta['imSampRate']); duration=float(meta['fileTimeSecs']); nc=int(meta['nSavedChans']); size=int(meta['fileSizeBytes'])
        assert fs>0 and duration>0 and nc>0 and size%(2*nc)==0
        samples=size//(2*nc); assert abs(samples/fs-duration)<=1/fs
        sync=np.load(paths['sync'],allow_pickle=False)
        assert sync.ndim==2 and sync.shape[1]==2 and len(sync)>=2
        assert np.isfinite(sync).all() and (np.diff(sync,axis=0)>0).all()
        probe_support=[max(0.,float(sync[0,0])),min(duration,float(sync[-1,0]))]
        assert probe_support[1]>probe_support[0]
        support=np.interp(probe_support,sync[:,0],sync[:,1])
        sat=pd.read_parquet(paths['saturation']); assert list(sat.columns)==['start_sample','stop_sample']
        badraw=sat.to_numpy(float); assert np.isfinite(badraw).all() and (badraw>=0).all() and (badraw<=samples).all()
        assert (badraw[:,1]>badraw[:,0]).all()
        # Clip known bad intervals to supported domain; no extrapolated scored epoch.
        clipped=np.clip(badraw/fs,*probe_support)
        bad=np.interp(clipped,sync[:,0],sync[:,1]); bad=bad[bad[:,1]>bad[:,0]]
        tr=load_file_content(paths['trials'])
        wheel_available=all(paths[k].exists() for k in ('wheel_times','wheel_position'))
        wheel=(np.load(paths['wheel_times'],allow_pickle=False),np.load(paths['wheel_position'],allow_pickle=False)) if wheel_available else None
        roles,mask,checks,cuts=task_masks(tr,support,bad,dev,wheel)
        counts={r:int(np.sum(mask&(roles==r))) for r in cuts}
        floors=dict(A=80,B=40,E=40) if dev else dict(C=80,D=60)
        trial_pass=all(counts[r]>=minimum for r,minimum in floors.items())
        native_table=encode_table(tr);task_records=records(native_table)
        native_verification=verify_native(tr,native_table,task_records)
        result=dict(subject=row['subject'],eid=row['eid'],pid=row['pid'],lab=row['lab'],allocation=row['allocation'],
            original_native_trials=len(tr),partitions={r:list(v) for r,v in cuts.items()},
            structural_eligible_epochs=counts,trial_floor_pass=trial_pass,source_mapping=mapping,
            fs=fs,AP_samples=samples,AP_duration_seconds=duration,recording_sync_support=support.tolist(),
            known_saturation_intervals=len(bad),native_sorting_revision='2024-05-06',native_task_revision='2025-03-03',
            per_check_counts={k:int(v.sum()) for k,v in checks.items()},
            prephysiology_possible=trial_pass and int(good.sum())>=8,
            physiology_computed=False,neural_arrays_accessed=False,
            wheel_coverage='VERIFIED_VALID_EPOCH_SUPPORT' if wheel_available else 'NOT_EVALUATED_METADATA_ONLY',
            artifact_limit='Known selected-probe saturation only; unannotated artifact burden unknown')
        dump(P/'metadata'/(row['subject']+'_task.json'),dict(trials=task_records,native_table=native_table,native_verification=native_verification,roles=roles.tolist(),valid=mask.tolist(),
            check_masks={k:v.tolist() for k,v in checks.items()},selected_probe_saturation_session_seconds=bad.tolist(),
            native_uuid_list=uuids.tolist(),native_cluster_channel=cc.tolist(),native_cluster_atlas=aid.tolist(),
            native_provider_labels=metrics.label.to_list(),result=result))
        out.append(result)
        print(row['subject'],counts,'native good',int(good.sum()),'trial gate',trial_pass,flush=True)
    dump(P/'results/METADATA_QC.json',out)
    possible=[x for x in out if x['prephysiology_possible']]
    dump(P/'results/FINAL_METADATA_GATE.json',dict(final_candidates=8,
        final_metadata_examined=len(out),possible_subjects=[x['subject'] for x in possible],
        final_trial_anatomy_upper_bound=len(possible),final_lab_upper_bound=len({x['lab'] for x in possible}),
        source_metadata_complete=len(out)==8,minimum_descriptive_mice=6,minimum_primary_mice=8,
        at_least_six_metadata_possible=len(possible)>=6,Final_C_neural_access=False,
        Final_D_scientific_access=False,real_fits=0))


if __name__=='__main__':run()
