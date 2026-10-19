"""Logical selected-unit-only HDF5 reads and native A-only export."""
import contextlib
import hashlib
import h5py
import numpy as np
from .core import SourceStop, ResourceStop, array_id, validate_item, observation_mask, coverage, extract_a, qc_a

SCALARS = ('/identifier', '/session_start_time', '/timestamps_reference_time')
REQUIRED = (*SCALARS, '/units/id', '/units/peak_channel_id', '/units/spike_times_index', '/units/spike_times')
OPTIONAL = ('/units/obs_intervals_index', '/units/obs_intervals')
ALLOWED = frozenset((*REQUIRED, *OPTIONAL))


def resolve(file, path, audit):
    if path not in ALLOWED: raise SourceStop('Unregistered neural/behavior path denied before lookup')
    node = file; prefix = ''
    for part in path.strip('/').split('/'):
        if not isinstance(node, h5py.Group): raise SourceStop('Unexpected source path container')
        link = node.get(part, getlink=True); prefix += '/'+part
        audit.append({'requested_path': path, 'component': prefix, 'link_class': type(link).__name__})
        if not isinstance(link, h5py.HardLink): raise SourceStop('Missing/soft/external source link denied')
        node = node[part]
        if node.file.id != file.id: raise SourceStop('Cross-file source object denied')
    if not isinstance(node, h5py.Dataset): raise SourceStop('Expected registered dataset')
    return node


def metadata(ds):
    return {'shape': list(ds.shape), 'dtype': ds.dtype.str, 'address': int(h5py.h5o.get_info(ds.id).addr),
            'chunks': list(ds.chunks) if ds.chunks else None, 'compression': ds.compression}


def verify_index(file, index, target):
    if index.ndim != 1 or index.dtype.kind not in 'iu': raise SourceStop('Ragged index integer schema')
    ref = index.attrs.get('target')
    if type(ref) is not h5py.Reference or not ref: raise SourceStop('Missing native VectorIndex target reference')
    actual = file[ref]
    if actual.file.id != file.id or actual.id != target.id: raise SourceStop('Wrong ragged target object identity')


def verify_probe_metadata(file, item, header, audit):
    result = {}
    for prefix in ['/general/devices/', '/general/extracellular_ephys/']:
        path = prefix + item['source_probe_name']; node = file
        for part in path.strip('/').split('/'):
            if not isinstance(node, h5py.Group) or not isinstance(node.get(part, getlink=True), h5py.HardLink):
                raise SourceStop('Frozen probe metadata path identity')
            node = node[part]
        if not isinstance(node, h5py.Group) or node.file.id != file.id: raise SourceStop('Frozen probe group identity')
        text = lambda v: v.decode('utf8') if isinstance(v, bytes) else str(v)
        expected = header['probe_metadata'][path]['attributes']
        attrs = {}
        for name in ['probe_id', 'namespace', 'neurodata_type', 'object_id']:
            if name in expected:
                attrs[name] = text(node.attrs.get(name))
                if attrs[name] != text(expected[name]): raise SourceStop('Original native probe object metadata mismatch')
        if attrs.get('probe_id') != str(item['probe_id']): raise SourceStop('Native selected probe ID mismatch')
        for name in ['obs_intervals', 'observation_intervals', 'obs_intervals_index', 'observation_intervals_index']:
            if node.get(name, getlink=True) is not None: raise SourceStop('Additional probe observation representation requires source contract review')
        result[path] = attrs; audit.append({'probe_metadata_path': path, 'attributes': attrs})
    return result


@contextlib.contextmanager
def value_scope(file, permitted, reads):
    original = h5py.Dataset.__getitem__
    apis = ['__array__', '__iter__', 'read_direct']; prior = {n: getattr(h5py.Dataset, n) for n in apis}
    def deny(*a, **k): raise SourceStop('Unregistered HDF5 value API denied')
    def get(ds, key, *args, **kwargs):
        address = int(h5py.h5o.get_info(ds.id).addr)
        if ds.file.id != file.id or address not in permitted: raise SourceStop('Unregistered/other neural array denied')
        path, selectors = permitted[address]
        if args or kwargs or not any(type(key) is type(allowed) and key == allowed for allowed in selectors): raise SourceStop('Other-unit/unregistered HDF5 selector denied')
        reads.append({'path': path, 'selector': str(key)})
        return original(ds, key)
    h5py.Dataset.__getitem__ = get
    for n in apis: setattr(h5py.Dataset, n, deny)
    try: yield
    finally:
        h5py.Dataset.__getitem__ = original
        for n, v in prior.items(): setattr(h5py.Dataset, n, v)


def read_a_source(file, item, reg, header, flashes, candidates, persist, audit, reads, reused_records=()):
    validate_item(item, reg)
    def text(v): return v.decode('utf8') if isinstance(v, bytes) else str(v)
    if text(file.attrs.get('nwb_version')) != '2.2.2': raise SourceStop('Frozen NWB generation mismatch')
    for name in ['nwb_version', 'namespace', 'neurodata_type', 'object_id']:
        if name in header.get('root_attributes', {}) and text(file.attrs.get(name)) != text(header['root_attributes'][name]):
            raise SourceStop('Original root object/source identity mismatch')
    probe_metadata = verify_probe_metadata(file, item, header, audit)
    ds = {p: resolve(file, p, audit) for p in REQUIRED}
    unit_group = ds['/units/id'].parent
    present = [unit_group.get(p.rsplit('/', 1)[1], getlink=True) is not None for p in OPTIONAL]
    if any(present) and not all(present): raise SourceStop('Incomplete native observation column/index pair')
    if all(present): ds.update({p: resolve(file, p, audit) for p in OPTIONAL})
    for path in SCALARS:
        if ds[path].size != 1: raise SourceStop('Identity/clock scalar schema')
    ids, peak, index, target = (ds[x] for x in ['/units/id', '/units/peak_channel_id', '/units/spike_times_index', '/units/spike_times'])
    if ids.ndim != 1 or ids.dtype.kind not in 'iu' or not 0 < len(ids) <= reg['resources']['unit_table_rows_max']:
        raise SourceStop('Native unit identity schema/engineering cap')
    if peak.ndim != 1 or peak.dtype.kind not in 'iu' or len(peak) != len(ids) or len(index) != len(ids):
        raise SourceStop('Native unit table shape/peak-channel schema')
    if target.ndim != 1 or target.dtype != np.dtype('float64'): raise SourceStop('Native spike-time binary64 schema')
    verify_index(file, index, target)
    if all(present):
        oi, ov = (ds[p] for p in OPTIONAL)
        if len(oi) != len(ids) or ov.ndim != 2 or ov.shape[1] != 2 or ov.dtype != np.dtype('float64'):
            raise SourceStop('Native observation ragged schema')
        verify_index(file, oi, ov)
    permitted = {}
    def allow(path, selectors): permitted[int(h5py.h5o.get_info(ds[path].id).addr)] = (path, selectors)
    for path in SCALARS: allow(path, [()])
    allow('/units/id', [slice(None)])
    records = []
    if [x['unit_id'] for x in reused_records] != item['candidate_unit_ids'][:len(reused_records)]:
        raise SourceStop('Saved candidate prefix differs from original numeric identities')
    with value_scope(file, permitted, reads):
        for path in SCALARS:
            value = np.asarray(ds[path][()]).item()
            if isinstance(value, bytes): value = value.decode('utf8')
            expected = str(item['session_id']) if path == '/identifier' else header[path]
            if str(value) != expected: raise SourceStop('Frozen source identifier/clock mismatch')
        values = ids[:]
        if len(values) != len(set(map(int, values))): raise SourceStop('Duplicate native unit IDs')
        lookup = {int(v): i for i, v in enumerate(values)}
        for position, uid in enumerate(item['candidate_unit_ids']):
            if uid not in lookup: raise SourceStop('Original candidate absent from pinned native source')
            i = lookup[uid]; cert = candidates[(item['session_id'], uid)]
            if position < len(reused_records):
                prior = reused_records[position]
                if prior['peak_channel_id'] != cert['peak_channel_id']:
                    raise SourceStop('Saved candidate peak/probe certificate mismatch')
                records.append(prior)
                continue  # No old candidate peak/index/spike array payload is reread.
            allow('/units/peak_channel_id', [i])
            actual_peak = int(peak[i])
            if actual_peak != cert['peak_channel_id'] or cert['probe_id'] != item['probe_id']:
                raise SourceStop('Native peak-channel/probe/anatomy identity mismatch')
            allow('/units/spike_times_index', [i] if i == 0 else [i-1, i])
            lo, hi = (0 if i == 0 else int(index[i-1])), int(index[i])
            if not 0 <= lo <= hi <= len(target): raise SourceStop('Native spike ragged bounds')
            if hi-lo > reg['resources']['selected_unit_row_values_max']: raise ResourceStop('Selected row memory cap; no unit exclusion/fallback')
            allow('/units/spike_times', [slice(lo, hi)])
            spikes = target[lo:hi]
            # Full selected row integrity first, including unpartitionable non-A nonfinite values.
            from .core import finite_native
            finite_native(spikes)
            native = array_id(spikes)
            obs = None
            if all(present):
                allow('/units/obs_intervals_index', [i] if i == 0 else [i-1, i])
                left, right = (0 if i == 0 else int(oi[i-1])), int(oi[i])
                if not 0 <= left <= right <= len(ov): raise SourceStop('Native observation ragged bounds')
                allow('/units/obs_intervals', [slice(left, right)])
                obs = ov[left:right]
            mask = observation_mask(flashes['start'], flashes['stop'], flashes['main_valid'], obs, reg)
            support = coverage(mask, flashes['color'])
            arrays = extract_a(spikes, flashes['start'], mask)
            del spikes
            physiology = qc_a(arrays, flashes['start'], reg)
            row = {'unit_id': uid, 'peak_channel_id': actual_peak, 'structure': cert['structure'],
                   'full_row_integrity_only': native, 'observation_intervals': None if obs is None else array_id(obs),
                   'support_basis': 'SOURCE_CURATED_PRESENTATIONS' if obs is None else 'EXPLICIT_UNIT_INTERVALS_INTERSECT_CURATED_PRESENTATIONS',
                   'observation_mask': mask.tolist(), 'source_coverage': support,
                   'individual_source_coverage_pass': all(v['pass'] for v in support.values()),
                   'A_physiology': physiology}
            row['private_A_capture'] = persist(uid, arrays, row)
            records.append(row)
    return {'units': records, 'native_objects': {p: metadata(v) for p, v in ds.items()}, 'probe_metadata': probe_metadata,
            'A_only_export': True, 'B_E_arrays_exported': False, 'Final_arrays_accessed': False}
