"""Non-predictive two-session spike feasibility audit; no fit/score code."""
import datetime,gc,json,hashlib
from pathlib import Path
import numpy as np
import pandas as pd
from one.alf.io import load_file_content
from .coverage import P,R,dump,region_of,trial_mask
from .numerics import map_clock,overlap,count_bins

def run():
    freeze=json.loads((P/'PILOT_FILE_FREEZE.json').read_text(encoding='utf8'))
    ids=json.loads((P/'PILOT_IDENTITY_FREEZE.json').read_text(encoding='utf8'))['pilots']
    receipts=json.loads((P/'results/FILE_RECEIPTS.json').read_text(encoding='utf8'))
    assert len(ids)<=2 and all(x['allocation']=='DEVELOPMENT' for x in ids)
    assert all(any(r['key']==x['key'] and r['status']=='COMPLETE' for r in receipts) for x in freeze['files'])
    atlas={int(a['id']):a['acronym'] for a in json.loads((R/'paper13/metadata/atlas.json').read_text(encoding='utf8'))['msg']}
    oldunits=pd.read_csv(R/'paper13/metadata/clusters_metadata.csv.gz')
    oldtrials=pd.read_csv(R/'paper13/metadata/trials_metadata.csv.gz')
    out=[]
    for p in ids:
        records=[r for r in freeze['files'] if r['eid']==p['eid']]
        paths={r['role']:P/'work/native'/r['eid']/Path(r['key']).name for r in records}
        # All arrays are from the original provider reader; no manual binary decoding.
        d={k:load_file_content(v) for k,v in paths.items() if k!='recording_meta'}
        t=d['times'];lab=d['clusters'];metrics=d['metrics'];cc=d['cluster_channels'];ca=d['atlas'][cc]
        assert np.isfinite(t).all() and (np.diff(t)>=0).all() and len(t)==len(lab)
        assert np.issubdtype(lab.dtype,np.integer) and lab.min()>=0 and lab.max()<len(metrics)
        assert np.array_equal(metrics.cluster_id.to_numpy(),np.arange(len(metrics)))
        assert np.issubdtype(cc.dtype,np.integer) and cc.min()>=0 and cc.max()<len(d['atlas'])
        a=[atlas.get(int(z)) for z in ca]
        target=np.array([region_of(z,['MOp'])=='MOp' for z in a]); good=metrics.label.eq(1).to_numpy()
        units=np.flatnonzero(target&good);assert len(units)>=8
        uu=d['uuids'];uu=uu.iloc[:,-1].astype(str).to_numpy() if isinstance(uu,pd.DataFrame) else uu.astype(str).to_numpy()
        old=oldunits[oldunits.pid.eq(p['pid'])].sort_values('cluster_id')
        # Version bridge assessed explicitly, never inferred from matching file names.
        bridge=dict(native_clusters=len(metrics),aggregate_clusters=len(old),
            uuid_order_equal=bool(len(old)==len(uu) and np.array_equal(uu,old.uuids.astype(str).to_numpy())),
            label_equal=bool(len(old)==len(metrics) and np.array_equal(metrics.label.to_numpy(),old.label.to_numpy())),
            atlas_equal=bool(len(old)==len(ca) and np.array_equal(ca,old.atlas_id.to_numpy())))
        meta=dict(z.split('=',1) for z in paths['recording_meta'].read_text(encoding='utf8').splitlines() if '=' in z)
        fs=float(meta['imSampRate']);duration=float(meta['fileTimeSecs']);nchan=int(meta['nSavedChans'])
        expected_samples=int(meta['fileSizeBytes'])/(2*nchan)
        assert abs(expected_samples/fs-duration)<1/fs
        sync=d['sync'];support=map_clock(sync,np.array([0.,duration]));assert support[1]>support[0]
        assert t[0]>=support[0]-.001 and t[-1]<=support[1]+.001
        sat=d['saturation'];assert list(sat.columns)==['start_sample','stop_sample']
        rawbad=sat.to_numpy(float);assert np.isfinite(rawbad).all() and (rawbad[:,1]>rawbad[:,0]).all()
        assert (rawbad>=0).all() and (rawbad<=expected_samples).all()
        bad=map_clock(sync,rawbad/fs)
        tr=d['trials'];native=tr.copy();native['bwm_include']=True;native['saturation_stim_plus06']=False
        structural=trial_mask(native)
        starts=tr.stimOn_times.to_numpy(float);stops=starts+.5
        covered=(starts>=support[0])&(stops<=support[1]);badtrial=overlap(starts,stops,bad)
        usable=structural&covered&~badtrial
        cut=len(tr)//2;halves=[int(usable[:cut].sum()),int(usable[cut:].sum())]
        assert usable.sum()>=100 and min(halves)>=40
        wt=d['wheel_times'];wp=d['wheel_position']
        assert len(wt)==len(wp) and np.isfinite(wt).all() and np.isfinite(wp).all() and (np.diff(wt)>0).all()
        wheel_covered=(starts>=wt[0])&(stops<=wt[-1])
        assert wheel_covered[usable].all()
        # Do not use interpolated future movement values; demonstration is a backward lookup only.
        backward=np.searchsorted(wt,starts[usable],side='left')-1
        assert (backward>=0).all() and (wt[backward]<starts[usable]).all()
        prior=oldtrials[oldtrials.eid.eq(p['eid'])]
        diff={}
        if len(prior)==len(tr):
            for k in ['stimOn_times','goCue_times','feedback_times','firstMovement_times','intervals_0','intervals_1']:
                x=prior[k].to_numpy(float);y=tr[k].to_numpy(float);finite=np.isfinite(x)&np.isfinite(y)
                diff[k]=dict(finite_disagreements=int(np.sum(np.isfinite(x)!=np.isfinite(y))),
                    unequal_gt_1us=int(np.sum(np.abs(x[finite]-y[finite])>1e-6)),max_abs_s=float(np.max(np.abs(x[finite]-y[finite]))) if finite.any() else None)
        examples=[];fragments=[]
        for i in np.flatnonzero(usable)[:10]:
            edges=starts[i]+np.arange(11)*.05
            lo,hi=np.searchsorted(t,[edges[0],edges[-1]],side='left')
            st=t[lo:hi];sl=lab[lo:hi];take=np.isin(sl,units);st=st[take];sl=sl[take]
            counts,valid=count_bins(st,sl,units,edges,bad)
            assert valid.all()
            examples.append(dict(trial=int(i),edges=edges.tolist(),counts=counts.tolist(),valid=valid.tolist()))
            fragments.append(dict(trial=int(i),times=st.tolist(),labels=sl.tolist()))
        target_map=pd.DataFrame(dict(cluster_id=units,uuid=uu[units],channel=cc[units],atlas_id=ca[units],acronym=[a[i] for i in units],label=metrics.label.to_numpy()[units]))
        target_map.to_csv(P/'results'/(p['subject']+'_UNIT_MAP.csv'),index=False,lineterminator='\n')
        demo=dict(subject=p['subject'],eid=p['eid'],units=units.tolist(),bad_intervals=bad.tolist(),support=support.tolist(),examples=examples,fragments=fragments,
            purpose='Small non-predictive counting fixture from ten prespecified eligible development trials. Not a predictive result.',license='IBL BWM CC BY 4.0; attribution official dataset registry and source UUID inventory')
        dump(P/'results'/(p['subject']+'_COUNT_DEMO.json'),demo)
        nzero=sum(int((np.asarray(e['counts'])==0).sum()) for e in examples)
        result=dict(subject=p['subject'],eid=p['eid'],pid=p['pid'],probe=p['probe_name'],region='MOp',allocation='DEVELOPMENT',
            sorting_revision='2024-05-06',trial_revision='2025-03-03',actual_spikes=len(t),nonfinite_spikes=0,unordered_transitions=0,
            simultaneous_native_clusters=len(metrics),MOp_labeled_units=int(target.sum()),MOp_provider_good_units=len(units),metadata_good_units=p['good_units'],
            unit_bridge=bridge,recording_duration_s=duration,recording_samples=int(expected_samples),fs=fs,session_clock_support=support.tolist(),
            spike_range_s=[float(t[0]),float(t[-1])],sync_points=len(sync),sync_end_probe_s=float(sync[-1,0]),
            sync_extrapolated_tail_s=float(max(0.,duration-sync[-1,0])),saturation_intervals=len(bad),known_saturation_duration_s=float(np.sum(bad[:,1]-bad[:,0])),
            native_trials=len(tr),structural_trials=int(structural.sum()),recording_covered_structural=int((structural&covered).sum()),
            saturation_overlap_structural=int((structural&covered&badtrial).sum()),usable_trials=int(usable.sum()),usable_trials_halves=halves,usable_window_seconds=float(.5*usable.sum()),
            native_aggregate_trial_comparison=diff,old_mask_transfer=False,wheel_samples=len(wt),wheel_range_s=[float(wt[0]),float(wt[-1])],
            wheel_covered_usable_trials=int((usable&wheel_covered).sum()),strict_past_wheel_lookup_pass=True,
            movement_onset_finite=int(np.isfinite(tr.firstMovement_times).sum()),response_finite=int(np.isfinite(tr.response_times).sum()),
            demo_trials=len(examples),demo_unit_bins=len(examples)*10*len(units),demo_zero_unit_bins=nzero,demo_invalid_bins=sum(int((~np.array(e['valid'])).sum()) for e in examples),
            observation_contract='Conventional curated ALF; AP recorded duration + monotone provider sync + native task windows, known saturation intervals masked; unknown other artifact burden retained as limitation.',
            pass_=True,predictive_fits=0,model_scores=0,final_neural_access=False)
        out.append(result);dump(P/'results/PILOT_RESULTS.json',out)
        print(json.dumps(result,indent=2),flush=True)
        del d,t,lab,metrics,cc,ca;gc.collect()
    dump(P/'results/PILOT_RUN_RECEIPT.json',dict(completed_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),pilots=len(out),
        reader='ONE-api 3.6.1 one.alf.io.load_file_content',all_pass=all(x['pass_'] for x in out),predictive_fits=0,final_neural_access=False,
        program_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()))
if __name__=='__main__':run()
