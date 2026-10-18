"""End-to-end original native Development input validation, never fitting/scoring."""
import math,struct,datetime,json
from pathlib import Path
import numpy as np
import pandas as pd
from one.alf.io import load_file_content
from .source import P,R,dump,load_json
from .training import sha
from .metadata_access import local_path
from .input_oracle import nuisance_reference,counts_reference,masks_reference,physiology_reference
from .features import nuisance,observed_arrays,design

def run():
    freeze=load_json((P/'SOURCE_FILE_FREEZE.json').read_text());rows=[]
    for entry in freeze['subjects']:
        if entry['allocation']!='DEVELOPMENT':continue
        subject=entry['subject'];state=load_json((P/'metadata'/(subject+'_task.json')).read_text())
        paths={f['role']:local_path(entry,f) for f in entry['files'] if f['role'] in ('trials','wheel_times','wheel_position')}
        frame=load_file_content(paths['trials']);canonical=state['native_table'];table=state['trials'];finite=0;missing=0
        assert canonical['fields']==list(frame.columns) and canonical['row_ordinals']==list(range(len(frame)))
        source_records=[]
        for i in range(len(frame)):
            row={}
            for field in frame.columns:
                value=frame[field].array[i];cell=canonical['columns'][field][i]
                if isinstance(value,(float,np.floating)):
                    raw=struct.pack('>d',float(value));assert bytes.fromhex(cell['bits'])==raw
                    if math.isfinite(float(value)):
                        assert struct.pack('>d',float.fromhex(cell['hex']))==raw==struct.pack('>d',table[i][field]);finite+=1
                        row[field]=float(value)
                    elif math.isnan(float(value)):
                        assert cell['classification']=='nan' and table[i][field] is None;missing+=1;row[field]=None
                    else:
                        assert table[i][field]==float(value);row[field]=float(value)
                elif value is None or value is pd.NA:
                    assert table[i][field] is None;missing+=1;row[field]=None
                else:
                    row[field]=value.item() if isinstance(value,np.generic) else value;assert row[field]==table[i][field]
            source_records.append(row)
        wt=np.load(paths['wheel_times'],allow_pickle=False);wp=np.load(paths['wheel_position'],allow_pickle=False)
        roles,valid=masks_reference(source_records,state['result']['recording_sync_support'],state['selected_probe_saturation_session_seconds'],wt)
        np.testing.assert_array_equal(roles,state['roles']);np.testing.assert_array_equal(valid,state['valid'])
        hist=load_json((R/'paper15_dev/metadata'/(subject+'_task.json')).read_text())
        record=dict(subject=subject,original_trial_rows=len(frame),finite_bit_patterns=finite,missing_values=missing,
            all_native_bits_verified=True,independent_role_and_mask_agreement=True,mask_changes_vs_history=int(np.sum(valid!=hist['valid'])),
            source_sha256={k:sha(p) for k,p in paths.items()},corrected_task_sha256=sha(P/'metadata'/(subject+'_task.json')),
            prephysiology_possible=state['result']['prephysiology_possible'],new_fits=0,Final_access=False)
        if not state['result']['prephysiology_possible']:
            record.update(A_neural_reconstruction='NOT_ADMITTED_BY_ORIGINAL_METADATA_RULES',reason=state['result']['structural_eligible_epochs'])
            rows.append(record);continue
        qc=load_json((P/'results'/(subject+'_A_QC.json')).read_text());prep=load_json((P/'states'/(subject+'_A_PREPROCESSING.json')).read_text())
        # Decode only original Development sources inside this trusted A projector.
        files={r['role']:R/r['original_path'] for r in qc['files']}
        rawtimes=np.load(files['times'],mmap_mode='r',allow_pickle=False);rawlabels=np.load(files['clusters'],mmap_mode='r',allow_pickle=False)
        stop=state['result']['partitions']['A'][1];lo=source_records[0]['intervals_0'];hi=source_records[stop-1]['intervals_1']
        pieces=[];indices=[]
        for start in range(0,len(rawtimes),1000000):
            chunk=np.asarray(rawtimes[start:start+1000000]);assert np.isfinite(chunk).all()
            take=np.flatnonzero((chunk>=lo)&(chunk<hi));indices.append(start+take);pieces.append(chunk[take])
        source_indices=np.concatenate(indices);times=np.concatenate(pieces);labels=np.asarray(rawlabels[source_indices])
        with np.load(P/'work/A_exports'/(subject+'.npz'),allow_pickle=False) as saved:
            np.testing.assert_array_equal(times,saved['times']);np.testing.assert_array_equal(labels,saved['labels'])
            ids=saved['trial_ids'];epochs=saved['epochs']
        np.testing.assert_array_equal(ids,np.flatnonzero(valid&(roles=='A')))
        stimuli=np.array([source_records[i]['stimOn_times'] for i in ids]);np.testing.assert_array_equal(epochs,np.column_stack([stimuli-.5,stimuli+.5]))
        ordinal_path=P/'work/A_source_ordinals'/(subject+'.npz');ordinal_path.parent.mkdir(parents=True,exist_ok=True);assert not ordinal_path.exists()
        np.savez_compressed(ordinal_path,source_row_ordinals=source_indices,A_role_ordinals=np.arange(len(times),dtype=np.int64))
        y,h,b=counts_reference(times,labels,prep['units'],stimuli)
        py,ph,pb,_,warm=observed_arrays(times,labels,prep['units'],stimuli)
        np.testing.assert_array_equal(y,py);np.testing.assert_array_equal(h,ph);np.testing.assert_array_equal(b,pb)
        reference=nuisance_reference(source_records,ids,b,stimuli-.5,wt,wp);production=nuisance(table,ids,pb,stimuli-.5,wt,wp)
        np.testing.assert_array_equal(reference,production)
        x,scales,active=design(reference,h,warm)
        assert scales==prep['scales'];np.testing.assert_array_equal(active,prep['active'])
        with np.load(P/'work/A_features'/(subject+'.npz'),allow_pickle=False) as arrays:
            np.testing.assert_array_equal(y,arrays['y']);np.testing.assert_array_equal(x,arrays['x'])
        units=[m['cluster_id'] for m in qc['physiology']];uuids=[m['uuid'] for m in qc['physiology']]
        metrics,ranked=physiology_reference(times,labels,units,uuids,ids,epochs,stop)
        for m,actual in zip(metrics,qc['physiology']):
            for key,value in m.items():assert value==actual[key],(subject,m['cluster_id'],key)
        assert [m['cluster_id'] for m in ranked]==qc['ranking']
        assert [m['uuid'] for m in ranked[:8]]==qc['selected_unit_uuids']
        oldqc=load_json((R/'paper15_dev/results'/(subject+'_A_QC.json')).read_text())
        with np.load(R/'paper15_dev/work/A_exports'/(subject+'.npz'),allow_pickle=False) as old:
            same_stream=np.array_equal(times,old['times']) and np.array_equal(labels,old['labels'])
        with np.load(R/'paper15_dev/work/A_features'/(subject+'.npz'),allow_pickle=False) as old:
            target_difference=int(np.sum(y!=old['y'])) if y.shape==old['y'].shape else None
            x_difference=float(np.max(np.abs(x-old['x']))) if x.shape==old['x'].shape else None
        record.update(A_source_exact_full_role=True,A_source_spikes=len(times),source_row_ordinals_sha256=sha(ordinal_path),
            source_order_per_unit_S07='All A-role source events retained in original source order, including events outside eligible epochs; unit-local ordinals follow this full stream',
            native_role_boundaries=[lo,hi],original_source_hashes={r['role']:r['sha256'] for r in qc['files']},
            historical_A_stream_identical=same_stream,historical_target_cells_changed=target_difference,historical_corrected_X_max_absolute=x_difference,
            selected_UUIDs_changed=oldqc['selected_unit_uuids']!=qc['selected_unit_uuids'],
            all_37_nuisance_columns_exact_independent=True,all_targets_histories_edges_exact_independent=True,
            independently_checked_QC_units=len(metrics),all_QC_ranks_exact=True,all_A_scalers_exact=True,
            preprocessing_sha256=sha(P/'states'/(subject+'_A_PREPROCESSING.json')),A_QC_sha256=sha(P/'results'/(subject+'_A_QC.json')))
        rows.append(record);print(subject,'native37/counts/history/QC/scalers/source-ordinals exact',flush=True)
    target=P/'results/FULL_A_SOURCE_REVALIDATION.json';assert not target.exists()
    dump(target,dict(mission='P15-DEV-EXACT-NATIVE-REPAIR-R1',time=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        rows=rows,candidates=12,EXACT_NATIVE_REPAIR_PASS=True,NATIVE_TIME_BITWISE_VERIFICATION=True,
        STRICT_PAST_WHEEL_GATE=True,FULL_A_SOURCE_REVALIDATION=True,real_fits=0,B_E_neural_export=False,Final_access=False))

if __name__=='__main__':run()
