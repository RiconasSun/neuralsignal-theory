"""M2 read-boundary preflight. Decode schema only, never neural values."""
import ast
import io
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import h5py
import requests
import register as r


def legacy_reader():
    source = r.ROOT / 'paper12/header_metadata.py'
    if r.sha(source) != r.verify()['prior_sha256']['paper12/header_metadata.py']:
        raise RuntimeError('Frozen range transport changed')
    tree = ast.parse(source.read_text(encoding='utf-8'))
    body = [n for n in tree.body if isinstance(n, (ast.ClassDef, ast.FunctionDef)) and
            n.name in ('RangeReader', 'hard_object')]
    namespace = {'io': io, 'requests': requests, 'hashlib': hashlib, 'h5py': h5py}
    exec(compile(ast.Module(body=body, type_ignores=[]), str(source), 'exec'), namespace)
    return namespace['RangeReader'], namespace['hard_object']


def schema(group):
    result = {}
    for name in sorted(group.keys()):
        if not isinstance(group.get(name, getlink=True), h5py.HardLink):
            raise RuntimeError('External/soft link in unit table')
        obj = group[name]
        if isinstance(obj, h5py.Dataset):
            result[name] = {'kind': 'dataset', 'shape': list(obj.shape), 'dtype': str(obj.dtype),
                            'chunks': list(obj.chunks) if obj.chunks else None,
                            'compression': obj.compression, 'decoded_values': False}
        elif isinstance(obj, h5py.Group):
            result[name] = {'kind': 'group', 'children': sorted(obj.keys()), 'decoded_values': False}
        else:
            raise RuntimeError('Unknown unit-table object')
    return result


def classify(columns):
    names = set(columns)
    candidate = [n for n in sorted(names) if any(word in n.lower() for word in
                 ('trial', 'presentation', 'time_index', 'bin_index', 'time_bounds'))]
    if 'spike_times' not in names or 'spike_times_index' not in names:
        return {'format': 'UNKNOWN', 'safe_temporal_selection_established': False,
                'reason': 'No recognized ragged spike table; no values decoded'}
    return {'format': 'RAGGED_UNIT_SPIKE_VECTOR', 'safe_temporal_selection_established': False,
            'candidate_temporal_index_fields': candidate,
            'reason': 'Unit-vector offsets are not a trial-time index. Dataset shape/chunks cannot locate permitted calibration spikes before decoding timestamps. Candidate fields require independent verification, never inferred support.'}


def inspect(item, animal):
    Reader, hard = legacy_reader()
    url = 'https://api.brain-map.org/api/v2/well_known_file_download/' + item['file_id']
    reader = Reader(url, int(item['content_range'].split('/')[-1]), max_bytes=4194304, etag=item['etag'])
    result = {'mission': r.MISSION, 'milestone': 'M2', 'utc': datetime.now(timezone.utc).isoformat(),
              'mouse_id': animal['mouse_id'], 'session_id': animal['session_id'], 'group': animal['group'],
              'url': url, 'etag': item['etag'], 'object_bytes': reader.size,
              'neural_values_decoded': 0, 'final_outcomes_decoded': False,
              'allowed_operation': 'HDF5 hard-link, group names and dataset shape/dtype/chunk/filter metadata only',
              'schema': {}, 'temporal_selection': {'safe_temporal_selection_established': False}}
    try:
        with h5py.File(reader, 'r') as file:
            result['root_names'] = sorted(file.keys())
            if '/units' not in file:
                raise RuntimeError('No root units table; do not switch to physiology decoding')
            result['schema'] = schema(hard(file, '/units'))
            result['temporal_selection'] = classify(result['schema'])
    except Exception as exc:
        result['error'] = type(exc).__name__ + ': ' + str(exc)[:250]
    finally:
        result['ranges'] = reader.ranges
        result['transport_bytes'] = reader.used
        reader.http.close()
    return result


def main():
    r.verify()
    gate = r.load(r.HERE / 'results/M1/gate_result.json')
    if gate['gate'] != 'PASS' or gate['registration_sha256'] != r.sha(r.HERE / 'registration.json'):
        raise RuntimeError('M1 gate not valid')
    items = {x['session_id']: x for x in r.load(r.ROOT / 'paper12/metadata/allen_header_capability.json')}
    animals = r.load(r.HERE / 'locks/animals.json')
    attempt = 'schema_network1' if '--network-retry' in sys.argv else 'schema'
    out = r.HERE / 'results/M2' / attempt
    out.mkdir(parents=True, exist_ok=True)
    # Smoke first, then the complete frozen26-session denominator, no substitutions.
    if '--smoke' in sys.argv:
        animals = animals[:1]
    for animal in animals:
        path = out / (animal['session_id'] + '.json')
        if path.exists():
            saved = r.load(path)
            if saved['mouse_id'] != animal['mouse_id'] or saved['group'] != animal['group'] or saved['etag'] != items[animal['session_id']]['etag']:
                raise RuntimeError('Schema cache identity drift')
            continue
        result = inspect(items[animal['session_id']], animal)
        r.save(path, result, exclusive=True)
        print(json.dumps({'session': animal['session_id'], 'group': animal['group'],
                          'bytes': result['transport_bytes'], 'fields': len(result['schema']),
                          'access': result['temporal_selection'], 'error': result.get('error')}), flush=True)
    r.verify()


if __name__ == '__main__':
    main()
