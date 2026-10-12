"""Physical stimulus sync vs saved NWB timing; no analog/behavior values."""
import ast
import functools
import importlib.util
import importlib.machinery
import json
import sys
from pathlib import Path
import h5py
import numpy as np
from register import HERE,ROOT,sha,verify
from digital import unwrap,old,acquire
from analysis import excluded,affected
from header_metadata import hard_object
from storage import load

def engine():
    r=json.loads((HERE/'visual_registration.json').read_text())
    for p,d in r['sha256'].items():
        if sha(HERE/p)!=d:raise RuntimeError('Visual protocol/source drift')
    loader=importlib.machinery.SourceFileLoader('pinned_stimulus_sync',str(HERE/'metadata/sdk_stimulus_sync_source.receipt'))
    spec=importlib.util.spec_from_loader(loader.name,loader);module=importlib.util.module_from_spec(spec)
    exec(compile(loader.get_source(loader.name),loader.path,'exec'),module.__dict__)
    return module

def zero_frame_correction(times):
    d=np.diff(times);a=np.where(d<.01)[0];b=np.where((d>.018)&(d<.1))[0];ft=d.copy()
    for index in a:
        prior=b[b<index]
        if len(prior) and prior[-1]-index>-100:
            ft[prior[-1]]=np.median(d);ft[index]=np.median(d)
    return np.r_[np.min(times),np.cumsum(ft)+np.min(times)]

def reconstruct(vsync,photodiode):
    m=engine();vs=m.trim_discontiguous_vsyncs(vsync)
    vcs,pds=m.separate_vsyncs_and_photodiode_times(vs,photodiode,60)
    all_times=[]
    for vc,pd in zip(vcs,pds):
        pd=m.trim_border_pulses(pd,vc);pd=m.correct_on_off_effects(pd);pd=m.fix_unexpected_edges(pd,cycle=60)
        duration=m.estimate_frame_duration(pd,cycle=60)
        _,starts,_=m.compute_frame_times(pd,duration,len(vc),cycle=60,
                        irregular_interval_policy=functools.partial(m.allocate_by_vsync,np.diff(vc)))
        all_times.append(starts)
    return zero_frame_correction(np.concatenate(all_times))

def nearest(frame_times,targets):
    frames=np.sort(np.asarray(frame_times));targets=np.asarray(targets)
    if not len(frames):raise RuntimeError('No reconstructed frame times')
    index=np.searchsorted(frames,targets);lo=np.clip(index-1,0,len(frames)-1);hi=np.clip(index,0,len(frames)-1)
    return np.minimum(np.abs(frames[lo]-targets),np.abs(frames[hi]-targets))

def main(output=None):
    verify();engine()
    directory=Path(output) if output else HERE/'metadata/visual_clock_code1';directory.mkdir(exist_ok=True,parents=True)
    inventory={r['session_id']:r['objects'] for r in old('allen_raw_inventory.json')}
    for session in sorted(old('allen_sessions.receipt')['msg'],key=lambda r:r['id']):
        sid=session['id'];output=directory/(sid+'.json')
        if output.exists():continue
        result={'session_id':sid,'pass':False,'behavioral_bits_decoded':False,'analog_values_decoded':False}
        try:
            item=next(o for o in inventory[sid] if o['key'].endswith('/sync.h5'))
            path=acquire(item,sid+'_sync',25000000,offline=True)
            with h5py.File(path,'r') as file:
                meta=ast.literal_eval(hard_object(file,'/meta')[()].decode());labels=meta['line_labels']
                def label(keys):
                    matches=[labels.index(k) for k in keys if k in labels]
                    if len(matches)!=1:raise RuntimeError('Missing/ambiguous visual sync label')
                    return matches[0]
                fi=label(('frames','stim_vsync','vsync_stim'));pi=label(('photodiode','stim_photodiode'))
                data=hard_object(file,'/data')
                if data.dtype!=np.dtype('uint32') or data.ndim!=2 or data.shape[1]!=2:raise RuntimeError('Digital schema changed')
                sample,_=unwrap(data[:,0]);times=sample/float(meta['ni_daq']['counter_output_freq'])
                bits=np.asarray(data[:,1]);fb=(bits&(1<<fi))!=0;pb=(bits&(1<<pi))!=0
                fdelta=np.r_[0,np.diff(fb.astype(int))];pdelta=np.r_[0,np.diff(pb.astype(int))]
                vs=times[fdelta==-1];pd=times[pdelta!=0]
            frame=reconstruct(vs,pd)
            header=load(HERE/'metadata/native_headers'/(sid+'.json'));targets=[];known=[];table_ranges={}
            invalid=excluded(header['tables'].get('invalid_times',{}))
            registry={p['id']:p['name'] for p in old('allen_probes.receipt')['msg'] if p['ecephys_session_id']==sid}
            for name,table in header['tables'].items():
                if name=='invalid_times':continue
                first=len(targets)
                for start,stop in zip(table['start_time'],table['stop_time']):
                    targets.append(start)
                    if any(affected(r['tags'],'__none__','__none__',registry) is None for r in invalid):
                        raise RuntimeError('Unknown exclusion tag entity; no silent global masking')
                    known.append(any(affected(r['tags'],'__none__','__none__',registry) is True and start<r['stop'] and stop>r['start'] for r in invalid))
                table_ranges[name]=(first,len(targets))
            error=nearest(frame,targets);clean=error[~np.asarray(known,bool)]
            per_table={}
            for name,(a,b) in table_ranges.items():
                part=error[a:b][~np.asarray(known[a:b],bool)]
                per_table[name]={'targets':b-a,'clean_targets':len(part),
                                  'max_seconds':float(np.max(part)) if len(part) else None,
                                  'p95_seconds':float(np.quantile(part,.95)) if len(part) else None,
                                  'above5ms':int(np.sum(part>.005))}
            result.update({'raw_vsync_edges':len(vs),'raw_photodiode_edges':len(pd),'reconstructed_frames':len(frame),
                           'frame_min_seconds':float(frame.min()),'frame_max_seconds':float(frame.max()),
                           'target_presentation_starts':len(targets),'known_global_invalid_targets':sum(known),
                           'all_error_max_seconds':float(np.max(error)),'clean_error_max_seconds':float(np.max(clean)),
                           'clean_error_p95_seconds':float(np.quantile(clean,.95)),'clean_targets_above5ms':int(np.sum(clean>.005)),
                           'clean_targets_outside_frame_envelope':int(np.sum((np.asarray(targets)[~np.asarray(known,bool)]<frame.min())|
                                                                          (np.asarray(targets)[~np.asarray(known,bool)]>frame.max()))),
                           'frame_array_sha256':__import__('hashlib').sha256(frame.tobytes()).hexdigest(),
                           'sync_object_sha256':sha(path),'per_table':per_table})
            limits=json.loads((HERE/'VISUAL_CLOCK_PROTOCOL.json').read_text())['registered_limits_seconds']
            result['pass']=bool(result['clean_error_p95_seconds']<=limits['p95'] and result['clean_error_max_seconds']<=limits['maximum'])
        except Exception as exc:result['error']=type(exc).__name__+': '+str(exc)[:300]
        output.write_text(json.dumps(result,indent=2,sort_keys=True))
        print(json.dumps({'session':sid,'pass':result['pass'],'error':result.get('error'),'max_seconds':result.get('clean_error_max_seconds')}),flush=True)

if __name__=='__main__':main()
