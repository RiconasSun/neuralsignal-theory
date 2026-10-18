"""Independent non-neural native source comparison; no reader.run/fits/prediction."""
import json, math, struct, datetime, re
import numpy as np
import pandas as pd
from one.alf.io import load_file_content
from paper15_final1.source import R,P,E,read,sha,source_rows
from paper15_final1.metadata_access import local_path

candidate=read(P/'C_READER_CANDIDATE.json')
for rel,h in candidate['hashes'].items():assert sha(P/rel)==h,rel
preserved=read(E/'METADATA_INTERRUPTION_PRESERVATION.json')
for n,h in preserved['completed_state_sha256'].items():assert sha(P/'metadata'/n)==h,n
gate=read(P/'results/FINAL_METADATA_GATE.json')
assert len(gate['subjects'])==8 and gate['source_exclusions']==['NYU-21']
assert len(gate['possible_subjects'])==7 and not gate['all_eight_source_pass'] and not gate['primary_eight_mouse_gate_possible']
assert not (P/'metadata/NYU-21_task.json').exists()
atlas={int(x['id']):x['acronym'] for x in read(R/'paper13/metadata/atlas.json')['msg']}
out=[]
for row in source_rows():
    if row['subject']=='NYU-21':continue
    state=read(P/'metadata'/(row['subject']+'_task.json'))
    paths={f['role']:local_path(row,f) for f in row['files'] if f['role'] not in ('times','clusters')}
    tr=load_file_content(paths['trials']); n=len(tr); cut=int(.6*n)
    assert state['result']['partitions']=={'C':[0,cut],'D':[cut,n]}
    assert state['result']['original_native_trials']==n
    table=state['native_table'];assert table['row_ordinals']==list(range(n)) and table['fields']==list(tr.columns)
    finite_bits=0
    for f in tr.columns:
        for i,v in enumerate(tr[f].array):
            cell=table['columns'][f][i]
            if isinstance(v,(float,np.floating)):
                assert cell['kind']=='binary64' and cell['bits']==struct.pack('>d',float(v)).hex()
                if math.isfinite(v):
                    assert struct.pack('>d',float(state['trials'][i][f]))==struct.pack('>d',float(v));finite_bits+=1
    meta=dict(line.split('=',1) for line in paths['recording_meta'].read_text().splitlines() if '=' in line)
    fs=float(meta['imSampRate']); duration=float(meta['fileTimeSecs']);channels=int(meta['nSavedChans']);size=int(meta['fileSizeBytes'])
    assert size%(2*channels)==0 and abs(size/(2*channels*fs)-duration)<=1/fs
    sync=np.load(paths['sync'],allow_pickle=False);assert np.isfinite(sync).all() and np.all(np.diff(sync,axis=0)>0)
    probe_support=[max(0.,float(sync[0,0])),min(duration,float(sync[-1,0]))]
    support=np.interp(probe_support,sync[:,0],sync[:,1])
    assert np.array_equal(support,state['result']['recording_sync_support'])
    sat=pd.read_parquet(paths['saturation']).to_numpy(float)
    assert np.isfinite(sat).all() and np.all(sat[:,1]>sat[:,0])
    bad=np.interp(np.clip(sat/fs,*probe_support),sync[:,0],sync[:,1]);bad=bad[bad[:,1]>bad[:,0]]
    assert np.array_equal(bad,np.asarray(state['selected_probe_saturation_session_seconds']).reshape(-1,2))
    wt=np.load(paths['wheel_times'],allow_pickle=False);wp=np.load(paths['wheel_position'],allow_pickle=False)
    assert len(wt)==len(wp) and np.isfinite(wt).all() and np.isfinite(wp).all() and np.all(np.diff(wt)>0)
    checks={k:[] for k in state['check_masks']}
    for i,r in tr.iterrows():
        a,s,g,f,z=[float(r[k]) for k in ['intervals_0','stimOn_times','goCue_times','feedback_times','intervals_1']]
        left,right=float(r['contrastLeft']),float(r['contrastRight'])
        role_lo,role_hi=(0,cut) if i<cut else (cut,n)
        first=float(tr.iloc[role_lo]['intervals_0']);last=float(tr.iloc[role_hi-1]['intervals_1'])
        vals=dict(event_order=all(math.isfinite(v) for v in (a,s,g,f,z)) and a<=s<=f<=z and a<=g<=f,
          neural_epoch_inside_trial=s-.5>=a and s+.5<=z,
          recording_sync_support=s-.5>=support[0] and s+.5<=support[1],
          behavioral_support=s-1>=support[0] and s+.5<=support[1],
          no_known_saturation=not any(s-1<e and s+.5>b for b,e in bad),
          no_overlapping_epoch=True,
          essential_contrast=not(math.isnan(left) and math.isnan(right)) and (math.isnan(left) or 0<=left<=1) and (math.isnan(right) or 0<=right<=1),
          role_support=math.isfinite(first) and math.isfinite(last) and s-1>=first and s+.5<=last,
          boundary_guard=i not in (cut-1,cut),wheel_support=s-1>wt[0] and s+.5<=wt[-1])
        for j in (i-1,i+1):
            if 0<=j<n:
                other=float(tr.iloc[j]['stimOn_times'])
                if math.isfinite(s) and math.isfinite(other) and abs(s-other)<1:vals['no_overlapping_epoch']=False
        for k,v in vals.items():checks[k].append(bool(v))
    for k,v in checks.items():assert v==state['check_masks'][k],(row['subject'],k)
    valid=np.logical_and.reduce([np.array(v) for v in checks.values()]);assert valid.tolist()==state['valid']
    assert state['roles']==['C']*cut+['D']*(n-cut)
    counts={'C':int(valid[:cut].sum()),'D':int(valid[cut:].sum())};assert counts==state['result']['structural_eligible_epochs']
    cc=np.load(paths['cluster_channels'],allow_pickle=False);ca=np.load(paths['atlas'],allow_pickle=False)
    assert np.array_equal(cc,state['native_cluster_channel']) and np.array_equal(ca[cc],state['native_cluster_atlas'])
    metrics=pd.read_parquet(paths['metrics'],columns=['cluster_id','label'])
    assert metrics.label.to_list()==state['native_provider_labels'] and np.array_equal(metrics.cluster_id,np.arange(len(metrics)))
    uuids=pd.read_csv(paths['uuids']).iloc[:,-1].astype(str).tolist();assert uuids==state['native_uuid_list']
    good=sum(label==1 and bool(re.fullmatch(r'MOp(?:1|2/3|4|5|6a|6b)?',str(atlas.get(int(a))))) for a,label in zip(ca[cc],metrics.label))
    assert good==state['result']['source_mapping']['native_MOp_provider_good']
    out.append(dict(subject=row['subject'],trials=n,counts=counts,native_good=good,native_finite_bits_verified=finite_bits,metadata_sha256=sha(P/'metadata'/(row['subject']+'_task.json'))))
result=dict(time=datetime.datetime.now(datetime.timezone.utc).isoformat(),mission='P15-M6-INDEPENDENT-FINAL-VALIDATION',scope='Non-neural cache/raw task and native wheel metadata only',subjects=out,original_six_hashes_unchanged=True,all_seven_masks_exact=True,source_controller_exclusions_preserved=True,actual_neural_arrays_read=False,C_fits=0,D_access=False,candidate_sha256=sha(P/'C_READER_CANDIDATE.json'),hashes=candidate['hashes'])
(E/'C_READER_INDEPENDENT_SOURCE_CHECKS_1.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
print(json.dumps(dict(mice=len(out),finite_binary64_cells=sum(x['native_finite_bits_verified'] for x in out),all_masks_exact=True,neural_arrays_read=False)))
