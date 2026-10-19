"""Diagnostic HDF5 metadata traversal only; never a production data reader."""
import contextlib
import copy
import posixpath
import h5py
import numpy as np

ALLOWED = frozenset(['/', '/processing', '/processing/running',
    '/processing/running/running_wheel_rotation', '/processing/running/running_wheel_rotation/data',
    '/processing/running/running_wheel_rotation/timestamps', '/processing/running/running_speed',
    '/processing/running/running_speed/timestamps', '/processing/running/running_speed_end_times',
    '/processing/running/running_speed_end_times/timestamps', '/identifier', '/session_start_time',
    '/timestamps_reference_time'])
ALIAS = '/processing/running/running_wheel_rotation/timestamps'
EXPECTED = '/processing/running/running_speed/timestamps'
ATTRS = ['unit', 'conversion', 'offset', 'resolution', 'interval', 'namespace',
         'neurodata_type', 'object_id', 'nwb_version']


class LinkProblem(Exception):
    def __init__(self, kind, path, detail):
        self.kind, self.path, self.detail = kind, path, detail
        super().__init__(kind + ': ' + path + ': ' + detail)


def normalized_target(parent, literal):
    if not isinstance(literal, str) or not literal or '\x00' in literal or '\\' in literal:
        raise ValueError('Invalid internal target spelling')
    return posixpath.normpath(literal if literal.startswith('/') else posixpath.join(parent, literal))


def plain(value):
    if isinstance(value, bytes):
        return value.decode('utf8', errors='strict')
    if isinstance(value, np.generic):
        return plain(value.item())
    if isinstance(value, (list, tuple, np.ndarray)):
        return [plain(x) for x in value]
    if isinstance(value, float) and not np.isfinite(value):
        return {'metadata_nonfinite': repr(value)}
    return value


@contextlib.contextmanager
def no_dataset_values():
    """Block common Python dataset value APIs, including identity scalar reads."""
    names = ['__getitem__', '__array__', '__iter__', 'read_direct']
    old = {name: getattr(h5py.Dataset, name) for name in names}
    count = {'forbidden_value_calls': 0}
    def deny(*a, **kw):
        count['forbidden_value_calls'] += 1
        raise RuntimeError('Dataset numerical/scalar values are forbidden in metadata diagnosis')
    for name in names:
        setattr(h5py.Dataset, name, deny)
    try:
        yield count
    finally:
        for name, fn in old.items():
            setattr(h5py.Dataset, name, fn)


class Inspector:
    def __init__(self, file, emit=None, deadline_guard=None):
        self.file = file
        self.emit = emit or (lambda row: None)
        self.guard = deadline_guard or (lambda: None)
        self.rows = []
        self.objects = {}

    def metadata(self, obj):
        self.guard()
        result = {'object_type': 'Group' if isinstance(obj, h5py.Group) else 'Dataset' if isinstance(obj, h5py.Dataset) else type(obj).__name__,
                  'object_address': int(h5py.h5o.get_info(obj.id).addr),
                  'same_file_id': bool(obj.file.id == self.file.id), 'attributes': {}}
        if not result['same_file_id']:
            raise LinkProblem('UNSAFE', obj.name, 'Object is not in the approved file')
        if isinstance(obj, h5py.Dataset):
            result.update({'shape': list(obj.shape), 'dtype': obj.dtype.str})
        names = ['nwb_version','namespace','neurodata_type','object_id'] if obj.name == '/' else ATTRS
        for name in names:
            if name not in obj.attrs:
                continue
            aid = obj.attrs.get_id(name)
            if int(np.prod(aid.shape, dtype=np.int64)) > 16 or aid.get_storage_size() > 4096:
                raise LinkProblem('UNRESOLVED', obj.name, 'Attribute exceeds metadata bound')
            value = plain(obj.attrs[name])
            if len(repr(value).encode('utf8')) > 4096:
                raise LinkProblem('UNRESOLVED', obj.name, 'Decoded attribute exceeds metadata bound')
            result['attributes'][name] = value
        return result

    def record(self, row):
        self.rows.append(copy.deepcopy(row))
        self.emit(row)

    def inspect(self, path, seen=()):
        self.guard()
        if path not in ALLOWED:
            raise LinkProblem('UNSAFE', path, 'Unregistered logical path denied before lookup')
        if path in seen:
            raise LinkProblem('CYCLE', path, 'Internal alias cycle')
        if path == '/':
            return self.file
        parent = self.file
        walked = ''
        for index, part in enumerate(path.strip('/').split('/')):
            self.guard()
            current = walked + '/' + part
            if current not in ALLOWED:
                raise LinkProblem('UNSAFE', current, 'Unregistered component denied')
            if not isinstance(parent, h5py.Group):
                self.record({'requested_path': path, 'path': current, 'existence': None,
                             'link_class': None, 'parent_path': walked or '/',
                             'problem': 'Unexpected non-Group parent'})
                raise LinkProblem('SCHEMA', current, 'Unexpected parent object type')
            parent_meta = self.metadata(parent)
            link = parent.get(part, getlink=True)
            row = {'requested_path': path, 'path': current, 'existence': link is not None,
                   'link_class': type(link).__name__ if link is not None else None,
                   'literal_target': None, 'normalized_candidate': None,
                   'parent_path': walked or '/', 'parent_identity': parent_meta,
                   'points_inside_same_file': None, 'expected_object_match': None}
            if link is None:
                self.record(row)
                raise LinkProblem('MISSING', current, 'Missing required component')
            if isinstance(link, h5py.ExternalLink):
                row.update({'literal_target': link.path, 'external_filename': link.filename,
                            'points_inside_same_file': False, 'expected_object_match': False})
                self.record(row)
                raise LinkProblem('UNSAFE', current, 'ExternalLink is never dereferenced')
            if isinstance(link, h5py.SoftLink):
                row['literal_target'] = link.path
                try:
                    candidate = normalized_target(walked or '/', link.path)
                except ValueError as exc:
                    row['problem'] = str(exc); self.record(row)
                    raise LinkProblem('UNSAFE', current, str(exc))
                row.update({'normalized_candidate': candidate, 'reference_scope': 'internal',
                            'expected_target_path_match': current == ALIAS and candidate == EXPECTED})
                # Record before validation or any attempted target lookup.
                self.record(row)
                if candidate == current or candidate in seen:
                    raise LinkProblem('CYCLE', current, 'Internal alias cycle')
                if candidate not in ALLOWED or current != ALIAS or candidate != EXPECTED:
                    raise LinkProblem('UNSAFE', current, 'Unexpected or unauthorized internal target')
                if '..' in link.path.split('/'):
                    raise LinkProblem('UNRESOLVED', current, 'Lexical parent normalization is not proof of native HDF5 resolution')
                if index != len(path.strip('/').split('/')) - 1:
                    raise LinkProblem('UNSAFE', current, 'Intermediate alias not registered')
                target = self.inspect(candidate, seen + (path,))
                info = self.metadata(target)
                row.update({'resolved_metadata': info, 'resolution': 'Verified fixed-target metadata traversal',
                            'points_inside_same_file': info['same_file_id'],
                            'expected_object_match': bool(info['same_file_id'])})
                # A separate event preserves the fact that initial resolution was pending.
                self.record({**row, 'event': 'SAFE_INTERNAL_TARGET_RESOLVED'})
                self.objects[path] = info
                return target
            if not isinstance(link, h5py.HardLink):
                self.record(row)
                raise LinkProblem('UNSAFE', current, 'Unsupported link class')
            # Only a flat HardLink component is dereferenced, never file[path].
            obj = parent[part]
            info = self.metadata(obj)
            row.update({'points_inside_same_file': info['same_file_id'], 'object_metadata': info})
            self.record(row)
            self.objects[current] = info
            parent, walked = obj, current
        return parent

    def run(self, paths):
        root = self.metadata(self.file)
        if root['attributes'].get('nwb_version') != '2.2.2':
            raise LinkProblem('SCHEMA', '/', 'Frozen NWB generation mismatch')
        for path in paths:
            obj = self.inspect(path)
            expected = h5py.Dataset if path.endswith(('/data', '/timestamps')) else h5py.Group
            if not isinstance(obj, expected):
                raise LinkProblem('SCHEMA', path, 'Unexpected source object type')
        alias = self.objects[ALIAS]
        target = self.objects[EXPECTED]
        rot = self.objects['/processing/running/running_wheel_rotation/data']
        end = self.objects['/processing/running/running_speed_end_times/timestamps']
        match = alias['same_file_id'] and target['same_file_id'] and alias['object_address'] == target['object_address']
        if not match:
            raise LinkProblem('SCHEMA', ALIAS, 'Alias and registered source timestamp objects differ')
        if any(x['dtype'] != '<f8' or len(x['shape']) != 1 for x in [alias, target, rot, end]):
            raise LinkProblem('SCHEMA', ALIAS, 'Native binary64/vector metadata contradicts contract')
        if not (rot['shape'] == alias['shape'] == end['shape']):
            raise LinkProblem('SCHEMA', ALIAS, 'Native row-count metadata contradicts contract')
        if not 0 < rot['shape'][0] <= 2000000:
            raise LinkProblem('SCHEMA', ALIAS, 'Metadata-visible row count violates the unchanged M2 source capacity bound')
        for name, meta in [(EXPECTED, target), ('/processing/running/running_speed_end_times/timestamps', end)]:
            unit = meta['attributes'].get('unit')
            if unit in [None, '', 'unknown']:
                raise LinkProblem('UNRESOLVED', name, 'Native timestamp unit metadata unavailable')
            if unit != 'seconds':
                raise LinkProblem('SCHEMA', name, 'Native timestamp units contradict frozen seconds contract')
            for field, expected in [('conversion', 1.), ('offset', 0.)]:
                if field in meta['attributes'] and meta['attributes'][field] != expected:
                    raise LinkProblem('SCHEMA', name, 'Explicit timestamp scaling contradicts native clock contract')
        rotation_unit = rot['attributes'].get('unit')
        if rotation_unit in [None, '', 'unknown']:
            raise LinkProblem('UNRESOLVED', '/processing/running/running_wheel_rotation/data', 'Native rotation unit metadata unavailable')
        if rotation_unit != 'radians':
            raise LinkProblem('SCHEMA', '/processing/running/running_wheel_rotation/data', 'Native rotation unit metadata contradicts contract')
        parent_unit = self.objects['/processing/running/running_wheel_rotation']['attributes'].get('unit', rotation_unit)
        if parent_unit != rotation_unit:
            raise LinkProblem('SCHEMA', '/processing/running/running_wheel_rotation', 'Conflicting rotation quantity unit metadata')
        for name, default in [('conversion', 1.), ('offset', 0.)]:
            if rot['attributes'].get(name, default) != default:
                raise LinkProblem('SCHEMA', '/processing/running/running_wheel_rotation/data', 'Nonidentity rotation scaling')
        original = [x for x in self.rows if x['requested_path'] == ALIAS and x['link_class'] != 'HardLink']
        if not original:
            raise LinkProblem('UNRESOLVED', ALIAS, 'Original HardLink-only failure not reproduced structurally')
        return {'status': 'INTERNAL_LINK_METADATA_COMPATIBLE', 'root_metadata': root,
                'failed_component': original[0]['path'], 'actual_link_class': original[0]['link_class'],
                'literal_target': original[0]['literal_target'], 'normalized_target': original[0]['normalized_candidate'],
                'expected_object_match': True, 'object_identity_basis': 'Same approved file ID plus equal HDF5 object address',
                'alias_object_address': alias['object_address'], 'expected_object_address': target['object_address'],
                'objects': self.objects, 'same_row_numeric_timing_validated': False}
