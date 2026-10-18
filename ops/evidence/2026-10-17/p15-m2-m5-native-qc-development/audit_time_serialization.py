"""Read-only native task versus saved JSON timing audit using existing A exports."""
import json
import datetime
import numpy as np
import pandas as pd
from one.alf.io import load_file_content
from paper15_dev.source import P,R,dump
from paper15_dev.training import admitted,sha
from paper15_dev.metadata_access import local_path
from paper15_dev.metadata_qc import task_masks
from paper15_dev.features import observed_arrays,nuisance,design


def main():
    source=json.loads((P/'SOURCE_FILE_FREEZE.json').read_text());rows=[]
    for subject in admitted():
        row=next(x for x in source['subjects'] if x['subject']==subject);assert row['allocation']=='DEVELOPMENT'
        metadata=json.loads((P/'metadata'/(subject+'_task.json')).read_text());stored=metadata['trials']
        task=next(x for x in row['files'] if x['role']=='trials');native=load_file_content(local_path(row,task))
        native_records=native.astype(object).where(pd.notnull(native),None).to_dict('records')
        fields={}
        for field in native.columns:
            try:a=native[field].to_numpy(float);b=np.array([np.nan if r[field] is None else r[field] for r in stored],float)
            except (TypeError,ValueError):continue
            finite=np.isfinite(a)&np.isfinite(b)
            fields[field]=dict(changed=int(np.sum(a[finite]!=b[finite])),max_absolute=float(np.max(np.abs(a[finite]-b[finite]),initial=0.)))
        wp={f['role']:local_path(row,f) for f in row['files'] if f['role'] in ('wheel_times','wheel_position')}
        wt=np.load(wp['wheel_times'],allow_pickle=False);wheel=np.load(wp['wheel_position'],allow_pickle=False)
        _,native_mask,_,_=task_masks(native,metadata['result']['recording_sync_support'],metadata['selected_probe_saturation_session_seconds'],True,(wt,wheel))
        _,rounded_mask,_,_=task_masks(pd.DataFrame(stored),metadata['result']['recording_sync_support'],metadata['selected_probe_saturation_session_seconds'],True,(wt,wheel))
        ids=np.flatnonzero(np.asarray(metadata['valid'])&(np.asarray(metadata['roles'])=='A'))
        state=json.loads((P/'states'/(subject+'_A_PREPROCESSING.json')).read_text())
        with np.load(P/'work/A_exports'/(subject+'.npz'),allow_pickle=False) as data:times=data['times'];labels=data['labels']
        ns=native.stimOn_times.to_numpy(float)[ids];rs=np.array([stored[i]['stimOn_times'] for i in ids])
        ny,nh,nb,_,warm=observed_arrays(times,labels,state['units'],ns)
        ry,rh,rb,_,_=observed_arrays(times,labels,state['units'],rs)
        nn=nuisance(native_records,ids,nb,ns-.5,wt,wheel);rn=nuisance(stored,ids,rb,rs-.5,wt,wheel)
        nx,_,_=design(nn,nh,warm,state['scales']);rx,_,_=design(rn,rh,warm,state['scales'])
        record=dict(subject=subject,source_task_sha256=sha(local_path(row,task)),saved_task_sha256=sha(P/'metadata'/(subject+'_task.json')),
            serialized_field_errors=fields,native_mask_vs_frozen=int(np.sum(native_mask!=metadata['valid'])),
            recomputed_rounded_mask_vs_frozen=int(np.sum(rounded_mask!=metadata['valid'])),
            A_target_count_cells_changed=int(np.sum(ny!=ry)),A_target_count_absolute_difference=int(np.abs(ny-ry).sum()),
            A_history_cells_changed=int(np.sum(nh!=rh)),A_history_max_absolute=float(np.max(np.abs(nh-rh),initial=0.)),
            A_nuisance_columns_max_absolute=np.max(np.abs(nn-rn),axis=(0,1)).tolist(),
            A_transformed_X_max_absolute=float(np.max(np.abs(nx-rx),initial=0.)),
            A_nuisance_cells_absolute_difference_ge_0_5=int(np.sum(np.abs(nn-rn)>=.5)))
        rows.append(record);print(subject,'target cells',record['A_target_count_cells_changed'],'history',record['A_history_cells_changed'],'Xmax',record['A_transformed_X_max_absolute'],flush=True)
    folder=R/'ops/evidence/2026-10-17/p15-m2-m5-native-qc-development';target=folder/'TIME_SERIALIZATION_AUDIT_1.json';assert not target.exists()
    dump(target,dict(time=datetime.datetime.now(datetime.timezone.utc).isoformat(),scope='Native task metadata/current saved A export only; no B/E neural/Final access, no optimization or source repair',
        rows=rows,real_fits=0,B_E_neural_access=False,Final_access=False,acceptance_threshold_added=False))


if __name__=='__main__':main()
