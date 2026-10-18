"""Nonpredictive, selected Development VISp rows only; official PyNWB lazy NWB interface."""
import datetime, hashlib, math
from collections import Counter
from pathlib import Path
import numpy as np
import h5py
from pynwb import NWBHDF5IO
from .core import *
from .pilot_transfer import approved_pilots,claim_attempt
from .access_gate import verify_access_approval
EXPECTED_NWB_VERSION="2.2.2"
P=Path(__file__).resolve().parents[1]; R=P.parent
E=R/'ops/evidence/2026-10-18/p16-visual-cortex-data-first-m0'

def digest_array(a): return hashlib.sha256(np.asarray(a,dtype='<f8').tobytes()).hexdigest()

def invalid_for_probe(rows,probe_id,probe_name,all_probes):
    bad=[]
    for row in rows:
        tags=row.get('tags',[])
        if isinstance(tags,str): tags=[tags]
        tags=set(map(str,tags))
        if not tags: raise ValueError('Invalid interval scope absent')
        global_tags={'EcephysSession','Stimulus','stimulus','all_probes'}
        if tags & global_tags:
            if tags-global_tags: raise ValueError('Unknown global invalid tags')
            applies=True
        elif 'EcephysProbe' in tags:
            ids=tags-{'EcephysProbe'}
            matches=[pid for pid,name in all_probes.items() if ids <= {str(pid),name} and ids]
            if len(matches)!=1: raise ValueError('Invalid probe tag ambiguous')
            applies=matches[0]==probe_id
        else: raise ValueError('Unknown invalid tags')
        interval=intervals([[row['start_time'],row['stop_time']]])[0]
        if applies: bad.append(interval)
    return intervals(bad)

def fast_counts(spikes, edges, support, invalid):
    # Spike order/finite values are verified once before this hot loop.
    values=np.diff(np.searchsorted(spikes,edges,side='left')).tolist()
    return [v if observed(float(a),float(b),support,invalid) else None for a,b,v in zip(edges[:-1],edges[1:],values)]

def validate_access(session_id):
    rows=[r for r in approved_pilots() if r['session_id']==session_id]
    if len(rows)!=1: raise ValueError('Session is not a frozen Development pilot')
    return rows[0]

def main():
    freeze=read_json(P/'results/PILOT_OBJECT_FREEZE.json')
    verify_access_approval(R)
    channel={int(r['id']):r for r in read_json(P/'metadata/channels.body')['msg']}
    unit={int(r['id']):r for r in read_json(P/'metadata/source_unit_qc.body')['msg']}
    probe_rows=read_json(P/'metadata/probes.body')['msg']
    for desc in freeze['objects']:
        sid=desc['session_id']; p=validate_access(sid)
        output=P/'results'/f'PILOT_{sid}.json'; attempt=P/'results'/f'PILOT_ATTEMPT_{sid}.json'
        if attempt.exists() or output.exists(): raise FileExistsError('No neural pilot retry permitted')
        path=P/'work'/f'session_{sid}.nwb'; transfer=read_json(P/'results'/f'TRANSFER_{sid}.json')
        assert transfer['status']=='COMPLETE' and sha256(path)==transfer['sha256']
        claim_attempt(attempt,{'status':'STARTED','session_id':sid,'time':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source_sha256':transfer['sha256'],'reader_sha256':sha256(Path(__file__))})
        try:
            with h5py.File(path,'r') as header:
                actual_version=str(header.attrs['nwb_version'])
                if actual_version!=EXPECTED_NWB_VERSION: raise ValueError('Unreviewed NWB generation')
            with NWBHDF5IO(str(path),'r',load_namespaces=True) as io:
                n=io.read()
                if int(n.identifier)!=sid: raise ValueError('NWB identifier mismatch')
                if n.session_start_time!=n.timestamps_reference_time: raise ValueError('Source time reference contradiction')
                # Lazy Units columns: only eight registered VISp rows load spike ragged payloads.
                ids=list(map(int,n.units.id[:])); index={v:i for i,v in enumerate(ids)}
                chosen=p['qualified_unit_ids'][:8]
                arrays={}; certificates=[]
                for uid in chosen:
                    i=index[uid]; peak=int(n.units['peak_channel_id'][i]); expected=int(unit[uid]['ecephys_channel_id'])
                    if peak!=expected or int(channel[peak]['ecephys_probe_id'])!=p['probe_id'] or channel[peak]['structure_acronym'] not in REGIONS: raise ValueError('Unit anatomy/probe mismatch')
                    spikes=np.asarray(n.units['spike_times'][i]); ordered_finite(spikes)
                    if spikes.dtype!=np.dtype('float64'): raise ValueError('Unexpected source timestamp precision')
                    encoded=spikes.astype('<f8',copy=False).tobytes(); restored=np.frombuffer(encoded,dtype='<f8')
                    assert np.array_equal(spikes.view('u8'),restored.view('u8'))
                    arrays[uid]=spikes
                    certificates.append({'unit_id':uid,'peak_channel_id':peak,'structure':channel[peak]['structure_acronym'],'spike_count':len(spikes),'nonfinite':int((~np.isfinite(spikes)).sum()),'decreases':int((np.diff(spikes)<0).sum()),'equal_adjacent':int((np.diff(spikes)==0).sum()),'binary64_sha256':digest_array(spikes),'binary64_roundtrip_pass':True,'min':native_time(spikes[0]) if len(spikes) else None,'max':native_time(spikes[-1]) if len(spikes) else None})
                bad_rows=[] if n.invalid_times is None else n.invalid_times.to_dataframe().reset_index().to_dict('records')
                current_probes={int(r['id']):r['name'] for r in probe_rows if int(r['ecephys_session_id'])==sid}
                invalid=invalid_for_probe(bad_rows,p['probe_id'],p['probe_name'],current_probes)
                families=[]; event_arrays={}; examples=[]
                for name,table in sorted(n.intervals.items()):
                    if not name.endswith('_presentations'): continue
                    frame=table.to_dataframe(); starts=np.asarray(frame['start_time'],dtype='<f8'); stops=np.asarray(frame['stop_time'],dtype='<f8'); native_ids=np.asarray(frame.index)
                    valid=np.isfinite(starts)&np.isfinite(stops)&(starts<stops)
                    if np.any(np.diff(starts[np.isfinite(starts)])<0): raise ValueError('Presentation order invalid')
                    valid &= np.array([observed(a,b,[[a,b]],invalid) if math.isfinite(a) and math.isfinite(b) and a<b else False for a,b in zip(starts,stops)])
                    # Full original native time arrays and IDs persisted losslessly; no rounded JSON construction.
                    event_arrays[name+'_start']=starts; event_arrays[name+'_stop']=stops; event_arrays[name+'_id']=native_ids
                    candidates=[c for c in frame.columns if c not in ['start_time','stop_time','tags','timeseries']]
                    condition_columns=[c for c in candidates if c not in ['stimulus_name','stimulus_block','stimulus_index']]
                    conditions=Counter(tuple(str(frame.iloc[i][c]) for c in condition_columns) for i in np.flatnonzero(valid))
                    repeated=sum(v>=2 for v in conditions.values())
                    first=np.flatnonzero(valid)[:64]
                    gaps=starts[1:]-stops[:-1]
                    families.append({'family':name,'original_presentations':len(frame),'valid_presentations':int(valid.sum()),'invalid_or_nonfinite':int((~valid).sum()),'source_parameter_columns':candidates,'condition_columns':condition_columns,'condition_values_and_repetitions':[{'values':list(key),'n':value} for key,value in sorted(conditions.items())],'condition_values_encoding':'Source scalar str including NaN/blank;not time serialization. Native timestamps separately lossless npz.','distinct_conditions':len(conditions),'repeated_conditions':repeated,'condition_repetition_min':min(conditions.values()) if conditions else 0,'condition_repetition_max':max(conditions.values()) if conditions else 0,'first64_original_ids':[int(native_ids[i]) for i in first],'start_stop_sha256':[digest_array(starts),digest_array(stops)],'positive_interpresentation_gaps':int((gaps>0).sum()),'overlapping_intervals':int((gaps<0).sum()),'duration_min':float(np.min((stops-starts)[valid])) if valid.any() else None,'duration_max':float(np.max((stops-starts)[valid])) if valid.any() else None,'coverage_gate':int(valid.sum())>=20 and repeated>=2})
                    for i in first:
                        a,b=float(starts[i]),float(stops[i]); support=[[a,b]]
                        for width in [.01,.05]:
                            count=int(math.floor((b-a)/width)); edges=a+np.arange(count+1,dtype=np.float64)*width; edges=edges[edges<=b]
                            if len(edges)<2: continue
                            for uid in chosen:
                                counts=fast_counts(arrays[uid],edges,support,invalid)
                                examples.append({'family':name,'original_ordinal':int(i),'presentation_id':int(native_ids[i]),'unit_id':uid,'width_illustrative_only':width,'bins':len(counts),'true_zero_bins':sum(x==0 for x in counts),'missing_bins':sum(x is None for x in counts),'total_count':sum(x for x in counts if x is not None),'first_bins':counts[:5]})
                event_path=P/'results'/f'NATIVE_EVENTS_{sid}.npz'; np.savez_compressed(event_path,**event_arrays)
                with np.load(event_path,allow_pickle=False) as saved:
                    for key,a in event_arrays.items(): assert saved[key].dtype==a.dtype and saved[key].tobytes()==a.tobytes()
                running=n.processing.get('running'); behavior={}
                if running is not None:
                    speed=running['running_speed']; start=np.asarray(speed.timestamps[:]); end=np.asarray(running['running_speed_end_times'].timestamps[:]); velocity=np.asarray(speed.data[:]); ordered_finite(start); ordered_finite(end)
                    if not(len(start)==len(end)==len(velocity)) or np.any(end<=start): raise ValueError('Running source intervals invalid')
                    behavior['running']={'samples':len(start),'nonfinite_values':int((~np.isfinite(velocity)).sum()),'start':native_time(start[0]),'stop':native_time(end[-1]),'native_time_hashes':[digest_array(start),digest_array(end)],'gap_count':int((start[1:]>end[:-1]).sum()),'strict_past_last_sample_before_first_stimulus':strict_past_index(start,float(min(f['start_time'].min() for name,f in [(k,v.to_dataframe()) for k,v in n.intervals.items() if k.endswith('_presentations')])))}
                else: behavior['running']={'available':False}
                eye=n.processing.get('eye_tracking'); gaze=n.processing.get('raw_gaze_mapping')
                if eye is not None and gaze is not None:
                    times=np.asarray(gaze['eye_area'].timestamps[:]); ordered_finite(times); fits=eye['pupil_ellipse_fits'].to_dataframe()
                    if len(times)!=len(fits): raise ValueError('Pupil time/value alignment')
                    behavior['pupil']={'samples':len(times),'nonfinite_values_by_column':{c:int((~np.isfinite(np.asarray(fits[c],dtype=float))).sum()) for c in fits.columns},'native_time_sha256':digest_array(times),'start':native_time(times[0]),'stop':native_time(times[-1]),'source_fail_eye_tracking':p['fail_eye_tracking']}
                else: behavior['pupil']={'available':False,'source_fail_eye_tracking':p['fail_eye_tracking']}
                result={'mission':MISSION,'session_id':sid,'mouse_id':p['mouse_id'],'group':'Development','probe_id':p['probe_id'],'source_sha256':transfer['sha256'],'nwb_version':actual_version,'reader':'PyNWB3.1.3 official NWB interface; AllenSDK2.16.2 source definitions pinned,SDK not executed','selected_unit_ids':chosen,'unit_certificates':certificates,'families':families,'behavior':behavior,'invalid_intervals_applied':invalid,'observation_contract':'Source-curated original scheduled presentation intervals on documented common session clock,minus known global/selected-probe invalid intervals. Not raw/APpacket continuity. No support inferred from spike extrema.','clock_reference_equal':True,'event_binary64_roundtrip_pass':True,'events_sha256':sha256(event_path),'coverage_gate':any(x['coverage_gate'] for x in families),'no_fits':True,'no_Final_access':True,'count_example_rows':len(examples),'true_zero_bins':sum(x['true_zero_bins'] for x in examples),'missing_bins':sum(x['missing_bins'] for x in examples)}
                dump_json(P/'results'/f'COUNT_EXAMPLES_{sid}.json',examples); dump_json(output,result)
                dump_json(attempt,{'status':'COMPLETE','session_id':sid,'time':datetime.datetime.now(datetime.timezone.utc).isoformat(),'result_sha256':sha256(output),'eight_selected_VISp_units_only':True})
                print('PILOT COMPLETE',sid,result['coverage_gate'],len(examples),flush=True)
        except Exception as exc:
            dump_json(attempt,{'status':'FAILED','session_id':sid,'time':datetime.datetime.now(datetime.timezone.utc).isoformat(),'error_type':type(exc).__name__,'error':str(exc),'no_retry':True})
            raise

if __name__=='__main__': main()
