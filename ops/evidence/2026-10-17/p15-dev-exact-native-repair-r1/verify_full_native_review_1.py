"""Independent input review: Development metadata and saved A streams; no fits."""
import datetime
import hashlib
import math
import struct
from bisect import bisect_left
from pathlib import Path

import numpy as np
import pandas as pd
from one.alf.io import load_file_content

from paper15_r1.source import P, R, dump, load_json
from paper15_r1.metadata_access import local_path
from paper15_r1.input_oracle import masks_reference, counts_reference, nuisance_reference, physiology_reference

E = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return load_json(path.read_text(encoding='utf8'))


def run():
    target = E / 'FULL_NATIVE_INPUT_REVIEW_RECEIPT_1.json'
    assert not target.exists()
    freeze = read(P / 'SOURCE_FILE_FREEZE.json')
    full_path = P / 'results/FULL_A_SOURCE_REVALIDATION.json'
    wheel_path = P / 'results/EXACT_WHEEL_INDEX_VERIFICATION.json'
    audit, wheel_audit = read(full_path), read(wheel_path)
    evidence_hashes = {str(x.relative_to(R)): sha(x) for x in (full_path, wheel_path, P/'READER_GATE.json', P/'results/M2_PHYSIOLOGY_GATE.json')}
    gate = read(P/'READER_GATE.json')
    for rel, identity in gate['hashes'].items():
        assert sha(P/rel) == identity
    roster = read(P/'results/M2_PHYSIOLOGY_GATE.json')
    assert len(roster['subjects']) == 12 and len({x['subject'] for x in roster['subjects']}) == 12
    accepted = {x['subject'] for x in roster['subjects'] if x['admitted']}
    assert len(accepted) == 10 and len({x['lab'] for x in roster['subjects'] if x['admitted']}) == 8
    assert {x['subject'] for x in audit['rows']} == {x['subject'] for x in roster['subjects']}
    atlas = {int(x['id']): x['acronym'] for x in read(R/'paper13/metadata/atlas.json')['msg']}
    rows, witness, total_queries = [], None, 0
    for source in freeze['subjects']:
        if source['allocation'] != 'DEVELOPMENT':
            continue
        subject = source['subject']
        saved = read(P/'metadata'/(subject+'_task.json'))
        record = next(x for x in audit['rows'] if x['subject'] == subject)
        assert sha(P/'metadata'/(subject+'_task.json')) == record['corrected_task_sha256']
        # local_path verifies original receipt/body SHA before any metadata decoder.
        paths = {f['role']: local_path(source, f) for f in source['files'] if f['role'] not in ('times', 'clusters')}
        frame = load_file_content(paths['trials'])
        table, view = saved['native_table'], saved['trials']
        assert table['fields'] == list(frame.columns)
        assert table['row_ordinals'] == list(range(len(frame)))
        assert len(table['index']) == len(frame.index) == len(view)
        finite = 0
        for field in frame.columns:
            assert table['dtypes'][field] == str(frame[field].dtype)
            for i, value in enumerate(frame[field].array):
                cell = table['columns'][field][i]
                if isinstance(value, (float, np.floating)):
                    bits = struct.pack('>d', float(value))
                    assert bytes.fromhex(cell['bits']) == bits
                    if math.isfinite(value):
                        assert cell['classification'] == 'finite'
                        assert struct.pack('>d', float.fromhex(cell['hex'])) == bits == struct.pack('>d', view[i][field])
                        finite += 1
                    elif math.isnan(value):
                        assert cell['classification'] == 'nan' and view[i][field] is None
                    else:
                        assert cell['classification'] == ('positive_infinity' if value > 0 else 'negative_infinity')
                        assert view[i][field] == value
                elif value is None or value is pd.NA:
                    assert view[i][field] is None
                else:
                    assert view[i][field] == value
        assert finite == record['finite_bit_patterns']
        meta = dict(line.split('=', 1) for line in paths['recording_meta'].read_text().splitlines() if '=' in line)
        fs, duration, channels, size = float(meta['imSampRate']), float(meta['fileTimeSecs']), int(meta['nSavedChans']), int(meta['fileSizeBytes'])
        assert fs > 0 and channels > 0 and duration > 0 and size % (2*channels) == 0
        samples = size // (2*channels)
        assert abs(samples/fs-duration) <= 1/fs
        sync = np.load(paths['sync'], allow_pickle=False)
        assert np.isfinite(sync).all() and (np.diff(sync, axis=0) > 0).all()
        bounds = [max(0., float(sync[0, 0])), min(duration, float(sync[-1, 0]))]
        support = np.interp(bounds, sync[:, 0], sync[:, 1])
        np.testing.assert_array_equal(support, saved['result']['recording_sync_support'])
        sat = pd.read_parquet(paths['saturation']).to_numpy(float)
        assert np.isfinite(sat).all() and (sat >= 0).all() and (sat <= samples).all()
        clipped = np.clip(sat/fs, *bounds)
        bad = np.interp(clipped, sync[:, 0], sync[:, 1]); bad = bad[bad[:, 1] > bad[:, 0]]
        np.testing.assert_array_equal(bad.reshape(-1, 2), np.array(saved['selected_probe_saturation_session_seconds']).reshape(-1, 2))
        cc = np.load(paths['cluster_channels'], allow_pickle=False)
        ca = np.load(paths['atlas'], allow_pickle=False)
        metrics = pd.read_parquet(paths['metrics'], columns=['cluster_id', 'label'])
        uuids = pd.read_csv(paths['uuids']).iloc[:, -1].astype(str).tolist()
        assert uuids == saved['native_uuid_list']
        np.testing.assert_array_equal(cc, saved['native_cluster_channel'])
        np.testing.assert_array_equal(ca[cc], saved['native_cluster_atlas'])
        np.testing.assert_array_equal(metrics['label'], saved['native_provider_labels'])
        assert metrics['cluster_id'].tolist() == list(range(len(uuids)))
        wt = np.load(paths['wheel_times'], allow_pickle=False)
        wp = np.load(paths['wheel_position'], allow_pickle=False)
        assert np.isfinite(wt).all() and np.isfinite(wp).all() and (np.diff(wt) > 0).all()
        roles, valid = masks_reference(view, support, bad, wt)
        np.testing.assert_array_equal(roles, saved['roles']); np.testing.assert_array_equal(valid, saved['valid'])
        counts = {role: int(np.sum(valid & (roles == role))) for role in 'ABE'}
        assert counts == saved['result']['structural_eligible_epochs']
        row = dict(subject=subject, finite_numeric_binary64_cells=finite, metadata_source_sha256={k: sha(p) for k,p in paths.items()},
                   task_sha256=sha(P/'metadata'/(subject+'_task.json')), independent_support_anatomy_masks=True, counts=counts)
        if subject not in accepted:
            assert not saved['result']['prephysiology_possible']
            rows.append(row)
            continue
        qc = read(P/'results'/(subject+'_A_QC.json'))
        prep = read(P/'states'/(subject+'_A_PREPROCESSING.json'))
        assert sha(P/'results'/(subject+'_A_QC.json')) == record['A_QC_sha256']
        assert sha(P/'states'/(subject+'_A_PREPROCESSING.json')) == record['preprocessing_sha256']
        assert sha(P/'work/A_exports'/(subject+'.npz')) == qc['A_export_sha256'] == prep['A_export_sha256']
        assert sha(P/'work/A_features'/(subject+'.npz')) == prep['A_features_sha256']
        assert sha(P/'work/A_source_ordinals'/(subject+'.npz')) == record['source_row_ordinals_sha256']
        assert qc['selected_unit_ids'] == prep['units'] and qc['selected_unit_uuids'] == prep['unit_uuids']
        ids = np.flatnonzero(valid & (roles == 'A')); stimuli = np.array([view[i]['stimOn_times'] for i in ids])
        starts = np.array([[s+(j-10)*.05 for j in range(20)] for s in stimuli]); starts[:, 10] = stimuli
        queries = [('bin', starts)] + [('past'+str(lag), starts-lag) for lag in (.05, .1, .25, .5)] + [('epoch', stimuli-.5)]
        query_count = 0; timeline = wt.tolist()
        for _, q in queries:
            index = np.array([bisect_left(timeline, value)-1 for value in q.ravel()]).reshape(q.shape)
            assert (index >= 0).all() and np.all(wt[index] < q)
            assert np.all(wt[np.minimum(index+1, len(wt)-1)] >= q)
            np.testing.assert_array_equal(index, np.searchsorted(wt, q, side='left')-1)
            query_count += q.size
        expected_wheel = next(x for x in wheel_audit['rows'] if x['subject'] == subject)
        assert query_count == sum(expected_wheel['counts'].values())
        total_queries += query_count
        row.update(exact_query_count=int(query_count), saved_A_artifact_hashes_verified=True)
        # All ten A streams: independent source-count/feature oracle and explicit
        # sum/N population scaling, never the production design/fit_scale helper.
        with np.load(P/'work/A_exports'/(subject+'.npz'), allow_pickle=False) as data:
            times, labels, a_ids, epochs = data['times'], data['labels'], data['trial_ids'], data['epochs']
        np.testing.assert_array_equal(a_ids, ids)
        assert np.isfinite(times).all() and np.all(np.diff(times) >= 0)
        assert np.issubdtype(labels.dtype, np.integer)
        np.testing.assert_array_equal(epochs, np.column_stack((stimuli-.5,stimuli+.5)))
        stop = saved['result']['partitions']['A'][1]
        assert times[0] >= view[0]['intervals_0'] and times[-1] < view[stop-1]['intervals_1']
        y,h,b = counts_reference(times, labels, prep['units'], stimuli)
        nx = nuisance_reference(view, ids, b, stimuli-.5, wt, wp)
        raw = np.concatenate((nx,h),axis=-1); score = raw[:,10:].reshape(-1,raw.shape[-1])
        mean = np.sum(score,axis=0)/len(score)
        deviations = score-mean
        sd = np.sqrt(np.sum(deviations*deviations,axis=0)/len(score)); active = sd >= 1e-8
        np.testing.assert_array_equal(mean,prep['scales']['mean']); np.testing.assert_array_equal(sd,prep['scales']['sd'])
        np.testing.assert_array_equal(active,prep['scales']['active'])
        normalized = np.where(active,np.minimum(3.,np.maximum(-3.,(raw-mean)/np.where(active,sd,1.))),0.)
        x = np.concatenate((np.ones((*raw.shape[:2],1)),normalized),axis=-1)
        with np.load(P/'work/A_features'/(subject+'.npz'),allow_pickle=False) as data:
            np.testing.assert_array_equal(data['y'],y);np.testing.assert_array_equal(data['x'],x)
        rates = y/.05; score_rates = rates[:,10:].reshape(-1,8)
        micro_mean = np.sum(score_rates,axis=0)/len(score_rates)
        micro_sd = np.sqrt(np.sum((score_rates-micro_mean)**2,axis=0)/len(score_rates))
        for key, cs in prep['C_scales'].items():
            np.testing.assert_array_equal(cs['micro_scale']['mean'],micro_mean)
            np.testing.assert_array_equal(cs['micro_scale']['sd'],micro_sd)
            np.testing.assert_array_equal(cs['micro_scale']['active'],micro_sd>=1e-8)
        row.update(independent_full_A_targets_history_37_features_and_scalers=True,
                   raw_A_spikes=len(times),scored_rows=len(score),scaler_columns=len(mean),
                   exact_means_and_population_SD=True,exact_active_mask_and_clipped_matrix=True,
                   C_micro_scalers_exact=True,C_other_state_verification='Hash-bound state and unchanged registered mathematical implementation; full production certification remains separate')
        if subject == 'PL033':
            value = float(frame['stimOn_times'].iloc[224]); assert value == view[224]['stimOn_times'] == 1150.1833035011502
            index = bisect_left(timeline, value)-1
            assert index == 394299 and wt[index+1] == value
            witness = dict(subject=subject, trial=224, native_boundary=value, native_boundary_hex=value.hex(),
                           predecessor=index, next_event_equals_boundary=True, rounded_predecessor=bisect_left(timeline,1150.1833035012)-1)
            q_units = [m['cluster_id'] for m in qc['physiology']]
            q_uuids = [m['uuid'] for m in qc['physiology']]
            ref_qc, ranking = physiology_reference(times,labels,q_units,q_uuids,ids,epochs,stop)
            assert len(ref_qc) == len(qc['physiology'])
            for actual, expected in zip(qc['physiology'],ref_qc):
                for key,value in expected.items(): assert actual[key] == value
            assert [m['cluster_id'] for m in ranking] == qc['ranking']
            assert [m['cluster_id'] for m in ranking[:8]] == prep['units']
            with np.load(P/'work/A_source_ordinals/PL033.npz',allow_pickle=False) as ordinals:
                np.testing.assert_array_equal(ordinals['A_role_ordinals'],np.arange(len(times)))
                assert np.all(np.diff(ordinals['source_row_ordinals']) > 0)
                assert len(ordinals['source_row_ordinals']) == len(times)
            row.update(independent_full_PL033_A_recompute=True,A_spikes=len(times),QC_units=len(ref_qc),
                       all_37_features_counts_history_scalers_rank_exact=True,full_A_ordinals_consistent=True)
        rows.append(row)
        print(subject,'metadata/query/hash checks exact',flush=True)
    assert witness and len(rows) == 12 and total_queries == 382487
    finite = sum(x['finite_numeric_binary64_cells'] for x in rows)
    assert finite == 96642
    assert all(sha(R/path) == identity for path, identity in evidence_hashes.items())
    report = dict(time=datetime.datetime.now(datetime.timezone.utc).isoformat(),mission='P15-DEV-EXACT-NATIVE-REPAIR-R1',
                  script_sha256=sha(Path(__file__)),evidence_hashes=evidence_hashes,rows=rows,development_candidates=12,
                  admitted_mice=10,labs=8,finite_numeric_binary64_cells=finite,exact_query_count=total_queries,
                  PL033_native_witness=witness,raw_whole_neural_sources_opened=False,B_E_Final_neural_access=False,
                  A_neural_review_scope='All ten corrected complete saved Development A streams; no raw whole-recording neural source read',
                  real_fits=0,source_or_scientific_policy_changes=False,
                  coverage_limit='QC/ordinal reexecution is PL033 only; all446 source-QC calculations and full raw-source projections reviewed through immutable auditor evidence and code')
    dump(target,report)
    print('Independent full input review receipt saved',flush=True)


if __name__ == '__main__':
    run()
