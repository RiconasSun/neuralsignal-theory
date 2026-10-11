import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import h5py

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import run_m2 as m
import audit_nix_coverage as coverage
import nix_mapping
import copy


class CountTests(unittest.TestCase):
    def test_mapping_tampering_rejected(self):
        original = json.loads((m.MANIFEST / 'nix_objects.json').read_text())
        nix_mapping.validate(original)
        for field, value in [('sha256', '0' * 64), ('filename', 'wrong.h5'), ('session_key', 'sub-99/ses-99'), ('pointer_git_blob_sha1', 'bad')]:
            changed = copy.deepcopy(original)
            changed['objects'][0][field] = value
            with self.assertRaises((ValueError, KeyError, StopIteration)):
                nix_mapping.validate(changed)
        changed = copy.deepcopy(original)
        changed['objects'].append(changed['objects'][0])
        with self.assertRaises(ValueError):
            nix_mapping.validate(changed)

    def test_required_m1_manifest_entries(self):
        accepted = json.loads((m.MANIFEST / 'accepted_m1_outputs.json').read_text())
        self.assertEqual(set(accepted['sha256']), m.M1_OUTPUTS)
    def test_equal_size_m1_selection_tamper_rejected(self):
        name = 'results/M1/unit_qc.csv'
        accepted = json.loads((m.MANIFEST / 'accepted_m1_outputs.json').read_text())
        with tempfile.TemporaryDirectory(dir=m.RESULTS) as folder:
            path = Path(folder) / name
            path.parent.mkdir(parents=True)
            data = (m.PAPER / name).read_bytes()
            changed = data.replace(b'hippocampus', b'XXXXXXXXXXX', 1)
            self.assertEqual(len(data), len(changed))
            path.write_bytes(changed)
            with patch.object(m, 'PAPER', Path(folder)), self.assertRaises(ValueError):
                m.verify_accepted_output(name, accepted['sha256'][name], accepted['accepted_m1_commit'])

    def test_every_bin_edge(self):
        from decimal import Decimal
        epsilon = Decimal('0.00000001')
        for index in range(60):
            edge = Decimal('-6') + Decimal(index) / 10
            self.assertEqual(m.bin_index(str(edge)), index)
            self.assertEqual(m.bin_index(str(edge + epsilon)), index)
            if index:
                self.assertEqual(m.bin_index(str(edge - epsilon)), index - 1)
    def test_missing_coverage_cannot_pass(self):
        with tempfile.TemporaryDirectory(dir=m.RESULTS) as folder:
            with patch.object(coverage.m1, 'PAPER', Path(folder)), patch.object(coverage, 'audit_session', side_effect=coverage.CoverageUnavailable('missing')):
                with self.assertRaises(coverage.CoverageUnavailable):
                    coverage.audit_all({'sub-01/ses-01': [{'unit_id': 1}]}, {'sub-01/ses-01': {'valid_trials': [1], 'excluded_trials': []}})
            report = json.loads((Path(folder) / 'results/M2/coverage_audit.json').read_text())
            self.assertEqual(report['gate'], 'NEED_ENV')
            self.assertEqual(report['sessions_verified'], 0)

    def test_nix_audit_never_reads_values(self):
        # Empty HDF5 schema fixture, not a neural observation or study result.
        with tempfile.TemporaryDirectory(dir=m.RESULTS) as folder:
            path = Path(folder) / 'Data_Subject_01_Session_01.h5'
            with h5py.File(path, 'w') as handle:
                group = handle.create_group(f'data/{path.stem}/data_arrays/fixture')
                group.attrs['name'] = b'Spike_Times_Unit_1_uAHL_2_Trial_1'
                group.attrs['unit'] = b's'
                group.create_dataset('data', shape=(0,), dtype='f8')
            expected = m.m1.digest(path)
            def fake_rows(file):
                return ([{'session_id': 'ses-01', 'nix_source_file': path.name, 'nix_source_sha256': expected}]
                        if file.name.endswith('_sessions.tsv') else [{'unit_id': '1', 'microwire': 'uAHL2'}])
            with patch.object(coverage, 'RAW', Path(folder)), patch.object(coverage.m1, 'rows', side_effect=fake_rows), patch.object(nix_mapping, 'load', return_value={'objects': []}), patch.object(h5py.Dataset, '__getitem__', side_effect=AssertionError('signal value read')):
                report = coverage.audit_session('sub-01/ses-01', [1], [1])
            self.assertFalse(report['timestamp_values_read'])
            self.assertFalse(report['array_lengths_exported'])
            path.write_bytes(path.read_bytes() + b'x')
            with patch.object(coverage, 'RAW', Path(folder)), patch.object(coverage.m1, 'rows', side_effect=fake_rows), patch.object(nix_mapping, 'load', return_value={'objects': []}), self.assertRaises(ValueError):
                coverage.audit_session('sub-01/ses-01', [1], [1])

    def test_exact_coverage_inventory(self):
        records = [{'unit': 1, 'trial': trial, 'microwire': 'uAHL2', 'rank': 1, 'dtype_kind': 'f', 'time_unit': 's'} for trial in (1, 2)]
        coverage.validate_inventory(records, [1], [1, 2], {1: 'uAHL2'})
        for bad in (records[:1], records + records[:1], records + [{**records[0], 'trial': 3}]):
            with self.assertRaises(ValueError):
                coverage.validate_inventory(bad, [1], [1, 2], {1: 'uAHL2'})

    def test_coverage_identity_and_schema(self):
        record = {'unit': 1, 'trial': 1, 'microwire': 'uAHL2', 'rank': 1, 'dtype_kind': 'f', 'time_unit': 's'}
        for field, value in [('microwire', 'uAHR2'), ('rank', 2), ('dtype_kind', 'O'), ('time_unit', 'ms')]:
            with self.assertRaises(ValueError):
                coverage.validate_inventory([{**record, field: value}], [1], [1], {1: 'uAHL2'})

    def test_decimal_boundaries(self):
        for text, expected in [('-6', 0), ('-5.9', 1), ('-0.1', 59), ('-0.000001', 59), ('0', None), ('2', None)]:
            self.assertEqual(m.bin_index(text), expected)

    def test_invalid_training_timestamp(self):
        for text in ('nan', 'inf', '-6.0001', '2.001', 'oops'):
            with self.assertRaises(ValueError):
                m.bin_index(text)

    def test_heldout_opaque_and_zero_arrays(self):
        with tempfile.TemporaryDirectory(dir=m.RESULTS) as folder:
            path = Path(folder) / 'spikes.tsv'
            path.write_text('unit_id\ttrial\tspike_time\n1\t1\t-5.9\nBROKEN\t2\tBROKEN\n1\t1\t0\n', encoding='utf-8')
            counts = m.extract(path, [1, 3], [1, 2])
            self.assertEqual(counts[0][1], [1, 0])
            self.assertEqual(sum(sum(b) for trial in counts for b in trial), 1)
            self.assertEqual(counts[1], [[0, 0] for _ in range(60)])

    def test_covariates_and_history_reset(self):
        for tid in (1, 2):
            rows = m.causal_metadata(tid, 8)['bins']
            self.assertEqual([r['known_set_size'] for r in rows[:10]], [0] * 10)
            self.assertEqual(rows[10]['known_set_size'], 8)
            self.assertEqual([r['bin'] for r in rows if r['history_reset']], [0])
            self.assertEqual({r['exposure_seconds'] for r in rows}, {'0.1'})

    def test_gap_rejected(self):
        with self.assertRaises(ValueError):
            m.check_roster([{'trial': '1'}, {'trial': '3'}])

    def test_hash_rejection(self):
        with self.assertRaises(ValueError):
            m.require_hash(m.PAPER / 'protocol' / 'protocol.json', 'bad')

    def test_preceding_gates_and_sources(self):
        self.assertEqual(m.prerequisite()['gate'], 'PASS')
        self.assertTrue(m.source_audit()['evidence'])

    def test_real_shapes_count_conservation(self):
        manifest = json.loads((m.MANIFEST / 'features.json').read_text())
        selected = m.selection()
        self.assertEqual(len(manifest['files']), 23)
        self.assertEqual(sum(len(units) for units in selected.values()), 613)
        for entry in manifest['files']:
            path = m.PAPER / entry['feature_path']
            m.require_hash(path, entry['sha256'])
            data = json.loads(path.read_text())
            units = selected[entry['session_key']]
            split = json.loads(m.m1.SPLIT.read_text())['sessions'][entry['session_key']]
            self.assertEqual(data['trial_ids'], split['partitions']['train'])
            self.assertEqual(data['unit_ids'], [int(unit['unit_id']) for unit in units])
            self.assertEqual(data['count_shape'], [len(data['trial_ids']), 60, len(units)])
            for trial in data['counts']:
                self.assertEqual(len(trial), 60)
                for bins in trial:
                    self.assertEqual(len(bins), len(units))
                    self.assertTrue(all(type(value) is int and value >= 0 for value in bins))
            totals = [sum(b[u] for trial in data['counts'] for b in trial) for u in range(len(units))]
            self.assertEqual(totals, [int(unit['training_preprobe_spikes']) for unit in units])
            self.assertFalse(data['validation_test_timestamps_parsed'])


if __name__ == '__main__':
    unittest.main()
