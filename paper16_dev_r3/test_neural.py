"""Synthetic exact-row/source/A-QC tests; no live source or real model fit."""
from pathlib import Path
import copy
import tempfile
import unittest
import h5py
import numpy as np
from .core import R, P, load, sha, SourceStop, CommonSupportStop, observation_mask, extract_a, qc_a, select_common
from .neural_reader import read_a_source, resolve, value_scope


class NativeReaderTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=P/'work', prefix='synthetic-neural-')
        self.path = Path(self.temp.name)/'fixture.h5'
        self.reg = load(P/'ACCESS_REGISTRATION.json')
        self.item = copy.deepcopy(self.reg['objects'][0])
        self.item['candidate_unit_ids'] = list(range(101, 109))
        self.reg['objects'] = [self.item]
        self.header = {'/session_start_time': 'synthetic-clock', '/timestamps_reference_time': 'synthetic-clock',
                       'root_attributes': {'nwb_version': '2.2.2', 'object_id': 'synthetic-object'}}
        starts = np.arange(150, dtype=np.float64)*2
        self.flashes = {'start': starts, 'stop': starts+.25, 'color': np.tile([-1., 1.], 75), 'main_valid': np.ones(150, dtype=bool)}
        self.certs = {(self.item['session_id'], uid): {'peak_channel_id': 42, 'probe_id': self.item['probe_id'], 'structure': 'VISp4'} for uid in self.item['candidate_unit_ids']}
        self.persisted = []
        with h5py.File(self.path, 'w') as f:
            f.attrs['nwb_version'] = '2.2.2'; f.attrs['object_id'] = 'synthetic-object'
            self.header['probe_metadata'] = {}
            for prefix in ['/general/devices/', '/general/extracellular_ephys/']:
                path = prefix+self.item['source_probe_name']; group = f.require_group(path)
                group.attrs['probe_id'] = self.item['probe_id']
                self.header['probe_metadata'][path] = {'attributes': {'probe_id': str(self.item['probe_id'])}}
            for key, value in [('identifier', str(self.item['session_id'])), ('session_start_time', 'synthetic-clock'), ('timestamps_reference_time', 'synthetic-clock')]: f.create_dataset(key, data=value)
            f.create_dataset('/units/id', data=np.arange(100, 110, dtype=np.int64))
            f.create_dataset('/units/peak_channel_id', data=np.full(10, 42, dtype=np.int64))
            values, index = [], []
            for uid in range(100, 110):
                # Unregistered neighboring unit has a nonfinite canary. It must never be materialized.
                row = np.array([np.nan]) if uid in [100, 109] else np.sort(np.ravel(starts[:, None]+[.1, .15]))
                values.extend(row); index.append(len(values))
            target = f.create_dataset('/units/spike_times', data=np.asarray(values, dtype=np.float64))
            ragged = f.create_dataset('/units/spike_times_index', data=np.asarray(index, dtype=np.uint64))
            ragged.attrs['target'] = target.ref

    def tearDown(self): self.temp.cleanup()

    def run_reader(self):
        def persist(uid, arrays, record):
            self.persisted.append((uid, {k: v.copy() for k, v in arrays.items()}, copy.deepcopy(record)))
            return {'synthetic': True}
        self.audit, self.reads = [], []
        with h5py.File(self.path, 'r') as f:
            return read_a_source(f, self.item, self.reg, self.header, self.flashes,
                                 self.certs, persist, self.audit, self.reads)

    def test_candidate_rows_only_A_native_export_and_no_neighbor_canary(self):
        result = self.run_reader()
        self.assertEqual(len(result['units']), 8)
        self.assertFalse(result['B_E_arrays_exported'])
        for uid, arrays, record in self.persisted:
            self.assertEqual(arrays['timestamps'].dtype, np.dtype('float64'))
            self.assertEqual(arrays['timestamps'].size, 180)
            self.assertTrue(np.all(arrays['original_ordinals'] < 90))
            self.assertLess(arrays['timestamps'].max(), self.flashes['start'][90])
            self.assertEqual(record['A_physiology']['ISI_pairs'], 90)
            self.assertEqual(record['A_physiology']['occupied'], 90)
            self.assertTrue(record['A_physiology']['pass'])
        actual_slices = [x['selector'] for x in self.reads if x['path'] == '/units/spike_times']
        self.assertEqual(actual_slices[0], str(slice(1, 301)))
        self.assertEqual(actual_slices[-1], str(slice(2101, 2401)))

    def test_B_E_changes_do_not_change_A_QC_or_ranking(self):
        first = self.run_reader(); captures = [a[1]['timestamps'].copy() for a in self.persisted]
        self.persisted = []
        with h5py.File(self.path, 'r+') as f:
            ds = f['/units/spike_times']
            for i in range(8):
                start = 1+i*300
                ds[start+180:start+300] = np.linspace(190, 299, 120)
        second = self.run_reader()
        for old, new in zip(first['units'], second['units']): self.assertEqual(old['A_physiology'], new['A_physiology'])
        for old, new in zip(captures, self.persisted): np.testing.assert_array_equal(old, new[1]['timestamps'])

    def test_selected_nonfinite_outside_A_is_integrity_STOP(self):
        with h5py.File(self.path, 'r+') as f: f['/units/spike_times'][181] = np.nan
        with self.assertRaises(SourceStop): self.run_reader()
        self.assertEqual(self.persisted, [])

    def test_probe_metadata_identity_and_unknown_observation_fail_closed(self):
        path = '/general/devices/'+self.item['source_probe_name']
        with h5py.File(self.path, 'r+') as f: f[path].attrs['probe_id'] = 999
        with self.assertRaises(SourceStop): self.run_reader()
        with h5py.File(self.path, 'r+') as f:
            f[path].attrs['probe_id'] = self.item['probe_id']
            f.create_dataset(path+'/obs_intervals', data=np.array([[0., 300.]]))
        with self.assertRaises(SourceStop): self.run_reader()

    def test_completed_A_captures_survive_later_integrity_failure(self):
        with h5py.File(self.path, 'r+') as f: f['/units/spike_times'][601] = np.nan
        with self.assertRaises(SourceStop): self.run_reader()
        self.assertEqual([x[0] for x in self.persisted], [101, 102])

    def test_source_clock_peak_and_root_mismatches_stop(self):
        for field in ['clock', 'peak', 'root']:
            with self.subTest(field=field):
                with h5py.File(self.path, 'r+') as f:
                    if field == 'clock': f['session_start_time'][()] = 'wrong'
                    elif field == 'peak': f['/units/peak_channel_id'][1] = 99
                    else: f.attrs['object_id'] = 'wrong'
                with self.assertRaises(SourceStop): self.run_reader()
                with h5py.File(self.path, 'r+') as f:
                    f['session_start_time'][()] = 'synthetic-clock'; f['/units/peak_channel_id'][1] = 42; f.attrs['object_id'] = 'synthetic-object'

    def test_Final_and_altered_roster_denied_before_value_reads(self):
        for kind in ['Final', 'altered']:
            with self.subTest(kind=kind):
                old = copy.deepcopy(self.item)
                if kind == 'Final': self.item['session_id'] = self.reg['denied_final_session_ids'][0]
                else: self.item['etag'] = 'wrong'
                # item and reg intentionally do not share identity for this negative.
                self.reg['objects'] = [old]
                with self.assertRaises(SourceStop): self.run_reader()
                self.item = old; self.reg['objects'] = [self.item]

    def test_wrong_target_soft_external_and_missing_observation_pair(self):
        with h5py.File(self.path, 'r+') as f:
            f['/units/spike_times_index'].attrs['target'] = f['/units/id'].ref
        with self.assertRaises(SourceStop): self.run_reader()
        with h5py.File(self.path, 'r+') as f:
            f['/units/spike_times_index'].attrs['target'] = f['/units/spike_times'].ref
            f.create_dataset('/units/obs_intervals_index', data=np.zeros(10, dtype=np.uint64))
        with self.assertRaises(SourceStop): self.run_reader()
        with h5py.File(self.path, 'r+') as f:
            del f['/units/obs_intervals_index']
            del f['/units/peak_channel_id']; f['/units/peak_channel_id'] = h5py.SoftLink('/units/id')
        with self.assertRaises(SourceStop): self.run_reader()
        with h5py.File(self.path, 'r+') as f:
            del f['/units/peak_channel_id']; f['/units/peak_channel_id'] = h5py.ExternalLink('unapproved.h5', '/units/id')
        with self.assertRaises(SourceStop): self.run_reader()

    def test_value_guard_blocks_other_rows_other_APIs_and_boolean_index(self):
        with h5py.File(self.path, 'r') as f:
            peak = f['/units/peak_channel_id']; allowed = {int(h5py.h5o.get_info(peak.id).addr): ('/units/peak_channel_id', [1])}
            with value_scope(f, allowed, []):
                self.assertEqual(int(peak[1]), 42)
                for fn in [lambda: peak[True], lambda: peak[2], lambda: peak[:], lambda: np.asarray(peak), lambda: peak.read_direct(np.empty(10)), lambda: f['/units/spike_times'][:]]:
                    with self.assertRaises(SourceStop): fn()
            self.assertEqual(int(peak[2]), 42)  # guard restores the original APIs.

    def test_observation_intervals_exclusion_zero_counts_and_A_boundaries(self):
        obs = np.array([[0., 100.], [102., 300.]], dtype=np.float64)
        mask = observation_mask(self.flashes['start'], self.flashes['stop'], self.flashes['main_valid'], obs, self.reg)
        self.assertFalse(mask[50]); self.assertTrue(mask[51])
        spikes = np.array([0., .22, 178., 178.219999999, 180.], dtype=np.float64)
        arrays = extract_a(spikes, self.flashes['start'], np.ones(150, dtype=bool))
        np.testing.assert_array_equal(arrays['timestamps'], [0., 178., 178.219999999])
        zeros = extract_a(np.empty(0, dtype=np.float64), self.flashes['start'], np.ones(150, dtype=bool))
        self.assertEqual(qc_a(zeros, self.flashes['start'], self.reg)['spikes'], 0)
        self.assertFalse(qc_a(zeros, self.flashes['start'], self.reg)['pass'])
        for role in ['B', 'E', 'C', 'D']:
            with self.assertRaises(SourceStop): extract_a(spikes, self.flashes['start'], mask, role)

    def test_explicit_native_observation_ragged_path_and_incomplete_support(self):
        with h5py.File(self.path, 'r+') as f:
            target = f.create_dataset('/units/obs_intervals', data=np.tile(np.array([[0., 300.]], dtype=np.float64), (10, 1)))
            index = f.create_dataset('/units/obs_intervals_index', data=np.arange(1, 11, dtype=np.uint64))
            index.attrs['target'] = target.ref
        records = self.run_reader()['units']
        self.assertTrue(all(x['support_basis'] == 'EXPLICIT_UNIT_INTERVALS_INTERSECT_CURATED_PRESENTATIONS' for x in records))
        with h5py.File(self.path, 'r+') as f:
            f['/units/obs_intervals'][:] = np.tile(np.array([[200., 300.]], dtype=np.float64), (10, 1))
        self.persisted = []
        records = self.run_reader()['units']
        for row in records:
            self.assertFalse(row['A_physiology']['pass'])
            self.assertIsNone(row['A_physiology']['rate'])
            self.assertEqual(row['A_physiology']['reason'], 'NO_SUPPORTED_A_PRESENTATIONS')

    def test_no_ISIs_across_flash_gaps(self):
        spikes = self.flashes['start'][:90] + .1
        arrays = extract_a(spikes, self.flashes['start'], np.ones(150, dtype=bool))
        result = qc_a(arrays, self.flashes['start'], self.reg)
        self.assertEqual(result['ISI_pairs'], 0); self.assertFalse(result['pass'])

    def test_lowest_eight_once_and_no_common_support_replacement(self):
        records = self.run_reader()['units']
        selected = select_common(records[::-1], self.flashes['color'], np.zeros((150, 6), dtype=bool), self.reg)
        self.assertEqual(selected['selected_unit_ids'], list(range(101, 109)))
        # Each candidate can pass30/color alone while intersections fail. An extra qualifying ID cannot replace one.
        for i, row in enumerate(records):
            row['observation_mask'][i*2:i*2+2] = [False, False]
        extra = copy.deepcopy(records[-1]); extra['unit_id'] = 999; extra['observation_mask'] = [True]*150
        # Remove enough disjoint A rows to make common floors fail while each candidate remains individually supported.
        for i, row in enumerate(records):
            for j in range(i*4, i*4+4): row['observation_mask'][j] = False
        with self.assertRaises(CommonSupportStop): select_common(records+[extra], self.flashes['color'], np.zeros((150, 6), dtype=bool), self.reg)


if __name__ == '__main__': unittest.main(verbosity=2)
