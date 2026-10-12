import io
import unittest
import h5py
import numpy as np
import access_audit as a
import register as r


class AccessTests(unittest.TestCase):
    def test_schema_never_reads_values(self):
        class Dataset:
            shape = (10,)
            dtype = np.dtype('float64')
            chunks = None
            compression = None
            def __getitem__(self, key):
                raise AssertionError('Value read forbidden')
        from unittest.mock import patch
        class Group:
            def keys(self): return ['spike_times']
            def get(self, name, getlink=False): return h5py.HardLink()
            def __getitem__(self, name): return Dataset()
        with patch.object(a.h5py, 'Dataset', Dataset):
            s = a.schema(Group())
        self.assertFalse(s['spike_times']['decoded_values'])

    def test_real_hdf_fixture_schema_only(self):
        payload = io.BytesIO()
        with h5py.File(payload, 'w') as f:
            g = f.create_group('units')
            g.create_dataset('spike_times', data=[.1, .2, .9, 1.1])
            g.create_dataset('spike_times_index', data=[4])
        payload.seek(0)
        with h5py.File(payload, 'r') as f:
            s = a.schema(f['units'])
        self.assertEqual(a.classify(s)['format'], 'RAGGED_UNIT_SPIKE_VECTOR')
        self.assertFalse(a.classify(s)['safe_temporal_selection_established'])

    def test_offsets_not_temporal_index(self):
        # Identical unit-vector shape/end-offset; different permitted-time membership.
        x = np.array([.1, .2, .9, 1.1])
        y = np.array([.1, .9, 1.1, 1.2])
        self.assertEqual(x.shape, y.shape)
        self.assertNotEqual(int(((x >= 0) & (x < .5)).sum()), int(((y >= 0) & (y < .5)).sum()))
        self.assertFalse(a.classify({'spike_times': {}, 'spike_times_index': {}})['safe_temporal_selection_established'])

    def test_suggestive_field_not_silent_pass(self):
        c = a.classify({'spike_times': {}, 'spike_times_index': {}, 'trial_time_index': {}})
        self.assertEqual(c['candidate_temporal_index_fields'], ['trial_time_index'])
        self.assertFalse(c['safe_temporal_selection_established'])

    def test_unknown_format_fails_closed(self):
        self.assertFalse(a.classify({})['safe_temporal_selection_established'])

    def test_external_link_rejected(self):
        with h5py.File(io.BytesIO(), 'w') as f:
            g = f.create_group('units')
            g['spike_times'] = h5py.ExternalLink('other.h5', '/times')
            with self.assertRaises(RuntimeError):
                a.schema(g)

    def test_actual_metadata_temporal_membership_missing(self):
        paths = sorted((r.HERE / 'results/M2/schema_network1').glob('*.json'))
        self.assertEqual(len(paths), 26)
        for path in paths:
            saved = r.load(path)
            self.assertNotIn('error', saved)
            self.assertEqual(saved['neural_values_decoded'], 0)
            self.assertFalse(saved['final_outcomes_decoded'])
            self.assertFalse(saved['temporal_selection']['safe_temporal_selection_established'])
            self.assertEqual(saved['temporal_selection']['candidate_temporal_index_fields'], [])


if __name__ == '__main__':
    unittest.main()
