"""Saved Development A task/wheel metadata only; never opens neural arrays."""
import datetime
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from one.alf.io import load_file_content
from paper15_dev.metadata_access import local_path


ROOT = Path(__file__).resolve().parents[4]
P = ROOT / 'paper15_dev'
E = Path(__file__).resolve().parent


def read(path):
    return json.loads(path.read_text(encoding='utf8'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def bins(stimuli):
    edges = stimuli[:, None] + (np.arange(21)[None, :] - 10) * .05
    edges[:, 10] = stimuli
    edges[:, -1] = stimuli + .5
    return edges[:, :-1]


def main():
    target = E / 'TIME_INDEX_AUDIT_1.json'
    assert not target.exists(), 'Preserve original diagnostics; no overwrite'
    audit_path = E / 'TIME_SERIALIZATION_AUDIT_1.json'
    audit_hash = sha(audit_path)
    audit = read(audit_path)
    source = read(P / 'SOURCE_FILE_FREEZE.json')
    production = read(P / 'PRODUCTION_GATE.json')
    wheels = {x['key']: x for x in read(P / 'results/DEVELOPMENT_WHEEL_BODY_READBACK.json')['files']}
    rows = []
    for old in audit['rows']:
        subject = old['subject']
        row = next(x for x in source['subjects'] if x['subject'] == subject)
        assert row['allocation'] == 'DEVELOPMENT'
        saved_path = P / 'metadata' / (subject + '_task.json')
        assert sha(saved_path) == old['saved_task_sha256']
        saved = read(saved_path)
        tf = next(x for x in row['files'] if x['role'] == 'trials')
        task_path = local_path(row, tf)
        assert sha(task_path) == old['source_task_sha256']
        native = load_file_content(task_path)
        ids = np.flatnonzero(np.asarray(saved['valid']) & (np.asarray(saved['roles']) == 'A'))
        native_stim = native['stimOn_times'].to_numpy(float)[ids]
        rounded_stim = np.array([saved['trials'][i]['stimOn_times'] for i in ids])
        paths = {x['role']: local_path(row, x) for x in row['files'] if x['role'] in ('wheel_times', 'wheel_position')}
        wheel_hashes = {}
        for f in row['files']:
            if f['role'] in paths:
                wheel_hashes[f['role']] = sha(paths[f['role']])
                assert wheel_hashes[f['role']] == wheels[f['key']]['sha256']
        wt = np.load(paths['wheel_times'], allow_pickle=False)
        wp = np.load(paths['wheel_position'], allow_pickle=False)
        assert np.isfinite(wt).all() and np.isfinite(wp).all() and (np.diff(wt) > 0).all()
        nb, rb = bins(native_stim), bins(rounded_stim)
        queries = [('bin_start', nb, rb), ('epoch_start', (native_stim - .5)[:, None], (rounded_stim - .5)[:, None])]
        queries += [(f'past_{h}', nb - h, rb - h) for h in (.05, .1, .25, .5)]
        indices = {}
        comparisons = []
        for name, nq, rq in queries:
            ni = np.searchsorted(wt, nq, side='left') - 1
            ri = np.searchsorted(wt, rq, side='left') - 1
            assert (ni >= 0).all() and (ri >= 0).all()
            indices[name] = (ni, ri)
            changed = ni != ri
            value_changed = wp[ni] != wp[ri]
            witnesses = []
            # Keep an exact representative of both directions, where present.
            for direction in (-1, 1):
                candidates = np.argwhere(changed & (np.sign(ri - ni) == direction) & value_changed)
                if not len(candidates):
                    candidates = np.argwhere(changed & (np.sign(ri - ni) == direction))
                if len(candidates):
                    i, j = map(int, candidates[0])
                    newer = max(int(ni[i, j]), int(ri[i, j]))
                    witnesses.append(dict(trial_id=int(ids[i]), bin_index=None if name == 'epoch_start' else j,
                        native_stim=float(native_stim[i]), rounded_stim=float(rounded_stim[i]),
                        native_query=float(nq[i, j]), rounded_query=float(rq[i, j]),
                        native_query_hex=float(nq[i, j]).hex(), rounded_query_hex=float(rq[i, j]).hex(),
                        native_index=int(ni[i, j]), rounded_index=int(ri[i, j]),
                        native_position=float(wp[ni[i, j]]), rounded_position=float(wp[ri[i, j]]),
                        crossed_event_time=float(wt[newer]), crossed_event_hex=float(wt[newer]).hex(),
                        native_event_available=bool(wt[newer] < nq[i, j]),
                        rounded_event_available=bool(wt[newer] < rq[i, j])))
            comparisons.append(dict(query=name, evaluated_indices=int(ni.size), changed_indices=int(changed.sum()),
                changed_held_positions=int(value_changed.sum()), max_index_difference=int(np.abs(ni-ri).max(initial=0)), witnesses=witnesses))
        absolute = np.r_[0., np.cumsum(np.abs(np.diff(wp)))]
        wheel_columns = []
        for side in (0, 1):
            now = indices['bin_start'][side]
            epoch = indices['epoch_start'][side]
            displacements = [wp[now] - wp[indices[f'past_{h}'][side]] for h in (.05, .1, .25, .5)]
            totals = [absolute[now] - absolute[indices[f'past_{h}'][side]] for h in (.05, .1, .25, .5)]
            squares = [(d/h)**2 for d, h in zip(displacements, (.05, .1, .25, .5))]
            wheel_columns.append(np.stack([wp[now]-wp[epoch], *displacements, *totals, *squares, np.abs(displacements[0])>.001], axis=-1))
        raw_error = np.max(np.abs(wheel_columns[0]-wheel_columns[1]), axis=(0, 1))
        # Compare to the preserved audit; this tolerance is only equality of two
        # independent floating arithmetic reports, never a scientific gate.
        assert np.allclose(raw_error, old['A_nuisance_columns_max_absolute'][23:37], rtol=0, atol=1e-12)
        state_rel = f'states/{subject}_A_PREPROCESSING.json'
        state_path = P / state_rel
        assert sha(state_path) == production['hashes'][state_rel]
        scales = read(state_path)['scales']
        mean = np.array(scales['mean'][23:37]); sd = np.array(scales['sd'][23:37]); active = np.array(scales['active'][23:37])
        transformed = [np.where(active, np.clip((x-mean)/np.where(active, sd, 1.), -3, 3), 0.) for x in wheel_columns]
        rows.append(dict(subject=subject, A_trials=len(ids), source_task_sha256=old['source_task_sha256'],
            saved_task_sha256=old['saved_task_sha256'], wheel_sha256=wheel_hashes, A_preprocessing_sha256=sha(state_path),
            query_comparisons=comparisons, total_changed_indices=sum(x['changed_indices'] for x in comparisons),
            wheel_column_max_absolute=raw_error.tolist(), transformed_wheel_X_max_absolute=float(np.max(np.abs(transformed[0]-transformed[1]), initial=0.)),
            matches_primary_audit_wheel_columns=True))
    assert sha(audit_path) == audit_hash
    result = dict(time=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        scope='Development A task/wheel and saved scaler metadata only; no neural arrays, B/E outcomes, Final arrays or optimization',
        primary_audit_sha256=audit_hash, diagnostic_script_sha256=sha(Path(__file__)),
        source_freeze_sha256=sha(P/'SOURCE_FILE_FREEZE.json'), production_gate_sha256=sha(P/'PRODUCTION_GATE.json'),
        python=sys.version, numpy=np.__version__, pandas=pd.__version__,
        changed_mice=sum(x['total_changed_indices']>0 for x in rows),
        total_changed_indices=sum(x['total_changed_indices'] for x in rows), rows=rows,
        changed_index_rule='Exact integer predecessor-index inequality; no magnitude threshold',
        epoch_query_counting='Epoch-start predecessor evaluated once per retained A trial; other queries once per warm/scored bin',
        neural_arrays_read=False, B_E_neural_access=False, Final_access=False, real_fits=0,
        scientific_acceptance_threshold_added=False)
    target.write_text(json.dumps(result, indent=2, sort_keys=True, allow_nan=False)+'\n', encoding='utf8')
    print(json.dumps(dict(changed_mice=result['changed_mice'], total_changed_indices=result['total_changed_indices'], rows=len(rows))))


if __name__ == '__main__':
    main()
