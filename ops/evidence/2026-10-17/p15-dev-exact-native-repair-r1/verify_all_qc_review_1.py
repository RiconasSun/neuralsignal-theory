"""Review-only complete corrected saved A physiology; no raw neural source read."""
import datetime
import hashlib
import re
from pathlib import Path
import numpy as np
from paper15_r1.source import P,R,load_json,dump
from paper15_r1.input_oracle import physiology_reference

E=Path(__file__).resolve().parent
def read(p):return load_json(p.read_text(encoding='utf8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def run():
    target=E/'FULL_NATIVE_QC_REVIEW_RECEIPT_1.json';assert not target.exists()
    gate=read(P/'results/M2_PHYSIOLOGY_GATE.json')
    atlas={int(x['id']):x['acronym'] for x in read(R/'paper13/metadata/atlas.json')['msg']}
    out=[]
    for row in gate['subjects']:
        if not row['admitted']:continue
        s=row['subject'];state=read(P/'metadata'/(s+'_task.json'));qcpath=P/'results'/(s+'_A_QC.json');qc=read(qcpath)
        export=P/'work/A_exports'/(s+'.npz');assert sha(export)==qc['A_export_sha256']
        with np.load(export,allow_pickle=False) as a:
            times,labels,ids,epochs=a['times'],a['labels'],a['trial_ids'],a['epochs']
        expected=[i for i,(a,label) in enumerate(zip(state['native_cluster_atlas'],state['native_provider_labels']))
                  if label==1 and re.fullmatch(r'MOp(?:1|2/3|4|5|6a|6b)?',str(atlas.get(int(a))))]
        assert expected==[x['cluster_id'] for x in qc['physiology']]
        uuids=[state['native_uuid_list'][i] for i in expected]
        stop=state['result']['partitions']['A'][1]
        reference,ranking=physiology_reference(times,labels,expected,uuids,ids,epochs,stop)
        assert len(reference)==len(qc['physiology'])
        for actual,ref in zip(qc['physiology'],reference):
            for key,value in ref.items():assert actual[key]==value,(s,ref['cluster_id'],key)
            rate=ref['A_rate_Hz'];count=ref['A_spikes'];pairs=ref['A_within_epoch_ISI_pairs'];fraction=ref['A_refractory_fraction']
            minexp=min(ref['original_A_quartile_exposures']);minrate=min(ref['original_A_quartile_rates'])
            reasons=[]
            if not .5<=rate<=100:reasons.append('RATE_OUTSIDE_0.5_100_HZ')
            if count<100:reasons.append('SPIKES_LT_100')
            if pairs<99:reasons.append('ISI_PAIRS_LT_99')
            if fraction is None or fraction>.005:reasons.append('ISI_FRACTION_GT_0.005_OR_UNDEFINED')
            if minexp<10:reasons.append('ORIGINAL_A_QUARTILE_EXPOSURE_LT_10_S')
            if minrate<.1:reasons.append('ORIGINAL_A_QUARTILE_RATE_LT_0.1_HZ')
            assert actual['exclusion_reasons']==reasons
            strict=not reasons and 1<=rate<=50 and fraction<=.0025 and minrate>=.2
            assert actual['strict_QC_qualified']==strict
        assert qc['ranking']==[x['cluster_id'] for x in ranking]
        assert qc['selected_unit_ids']==[x['cluster_id'] for x in ranking[:8]]
        assert qc['selected_unit_uuids']==[x['uuid'] for x in ranking[:8]]
        assert qc['qualified_units']==len(ranking)
        ordinal_path=P/'work/A_source_ordinals'/(s+'.npz')
        with np.load(ordinal_path,allow_pickle=False) as o:
            assert len(o['source_row_ordinals'])==len(times)
            assert np.all(np.diff(o['source_row_ordinals'])>0)
            np.testing.assert_array_equal(o['A_role_ordinals'],np.arange(len(times),dtype=np.int64))
        out.append(dict(subject=s,source_target_units=len(reference),qualified=len(ranking),all_QC_metrics_reasons_strict_flags_rank_selected_exact=True,
                        full_saved_A_ordinals_consistent=True,A_export_sha256=qc['A_export_sha256'],QC_sha256=sha(qcpath),ordinals_sha256=sha(ordinal_path)))
        print(s,len(reference),'QC records exact',flush=True)
    assert len(out)==10 and sum(x['source_target_units'] for x in out)==446
    dump(target,dict(time=datetime.datetime.now(datetime.timezone.utc).isoformat(),script_sha256=sha(Path(__file__)),
         input_oracle_sha256=sha(P/'input_oracle.py'),rows=out,QC_units=446,qualified=sum(x['qualified'] for x in out),
         independent_all_QC_verification=True,raw_whole_neural_source_opened=False,B_E_Final_neural_access=False,real_fits=0))

if __name__=='__main__':run()
