"""Synthetic M0 regressions; no source retrieval, neural outcomes or model fitting."""
import math
import struct
import tempfile
import unittest
from pathlib import Path
from .core import (native_time, restore_time, strict_past_index, count_bins,
                   presentation_records, source_qualified, metadata_populations,
                   allocate_roles, choose_pilots, TransferBudget, read_json)


class NativeM0Tests(unittest.TestCase):
    def test_binary64_adjacent_roundtrip(self):
        for x in [0., -0., .1, math.nextafter(.1, -math.inf), math.nextafter(.1, math.inf), 1e300]:
            self.assertEqual(struct.pack('<d', restore_time(native_time(x))), struct.pack('<d', x))
        self.assertFalse(native_time(float('nan'))['finite'])
        self.assertTrue(math.isnan(restore_time(native_time(float('nan')))))

    def test_equality_is_not_past(self):
        t = [math.nextafter(1., -math.inf), 1., math.nextafter(1., math.inf)]
        self.assertEqual(strict_past_index(t, 1.), 0)
        self.assertEqual(strict_past_index(t, t[0]), -1)
        with self.assertRaises(ValueError): strict_past_index([0, float('nan')], 1.)
        with self.assertRaises(ValueError): strict_past_index([2., 1.], 3.)

    def test_halfopen_zero_missing_and_invalid_are_distinct(self):
        self.assertEqual(count_bins([1., 2.], [0., 1., 2., 3.], [[0., 2.]]), [0, 1, None])
        self.assertEqual(count_bins([], [0., 1., 2.], [[0., 2.]], [[1., 2.]]), [0, None])
        self.assertEqual(count_bins([1., 1.], [0., 1., 2.], [[0., 2.]]), [0, 2])

    def test_presentation_ids_native_boundaries_and_gaps(self):
        r = presentation_records([91, 4], [.1, 5.], [.2, 6.])
        self.assertEqual([x['presentation_id'] for x in r], ['91', '4'])
        self.assertEqual([x['original_ordinal'] for x in r], [0, 1])
        self.assertEqual(count_bins([], [0., 1., 2., 3.], [[0., 1.], [2., 3.]]), [0, None, 0])
        with self.assertRaises(ValueError): presentation_records([1, 1], [0, 1], [1, 2])

    def test_missing_behavior_remains_missing(self):
        r = native_time(float('nan'))
        self.assertFalse(r['finite']); self.assertIsNone(r['hex'])
        self.assertTrue(math.isnan(restore_time(r)))

    def test_explicit_source_qc_boundaries(self):
        r = {'quality': 'good', 'amplitude_cutoff': .1, 'presence_ratio': .95, 'isi_violations': .5}
        self.assertTrue(source_qualified(r))
        for key, value in [('quality', 'noise'), ('presence_ratio', .949), ('isi_violations', math.inf), ('amplitude_cutoff', -.1)]:
            self.assertFalse(source_qualified({**r, key: value}))

    def test_same_probe_and_duplicate_mouse_are_not_pooled(self):
        sessions = [{'id': 1, 'specimen_id': 9, 'date_of_acquisition': '2020-01-01', 'stimulus_name': 'x'},
                    {'id': 2, 'specimen_id': 9, 'date_of_acquisition': '2021-01-01', 'stimulus_name': 'x'}]
        probes = [{'id': i, 'ecephys_session_id': 1 if i < 3 else 2, 'sampling_rate': 30000} for i in [1, 2, 3]]
        channels = [{'id': i, 'ecephys_probe_id': i, 'structure_acronym': 'VISp'} for i in [1, 2, 3]]
        units = [{'id': i, 'ecephys_channel_id': 1 if i < 5 else (2 if i < 9 else 3), 'quality': 'good', 'presence_ratio': 1, 'isi_violations': 0, 'amplitude_cutoff': 0} for i in range(1, 17)]
        out = metadata_populations(sessions, probes, channels, units)
        self.assertEqual(len(out['selected']), 1)
        self.assertEqual(out['selected'][0]['session_id'], 2)
        self.assertEqual([r['qualified_units'] for r in out['all_populations']], [4, 4, 8])

    def test_role_reservation_is_deterministic_and_history_excluded(self):
        rows = [{'mouse_id': str(i), 'session_id': i, 'session_type': 'brain_observatory_1.1' if i % 2 else 'functional_connectivity'} for i in range(20)]
        a = allocate_roles(rows, range(4), [4])
        b = allocate_roles(list(reversed(rows)), range(4), [4])
        self.assertEqual({r['mouse_id'] for r in a if r['group'] == 'Final_candidate'}, {r['mouse_id'] for r in b if r['group'] == 'Final_candidate'})
        self.assertFalse(any(r['session_id'] <= 4 and r['group'] == 'Final_candidate' for r in a))
        pilots = choose_pilots(a, {i: 100 for i in range(20)}, [4])
        self.assertEqual(len(pilots), 2)
        self.assertTrue(all(r['group'] == 'Development' and r['session_id'] != 4 for r in pilots))

    def test_history_is_whole_mouse_across_sessions(self):
        rows = [{'mouse_id': str(i), 'session_id': 1000+i, 'session_type': 'brain_observatory_1.1'} for i in range(20)]
        roles = allocate_roles(rows, ['11'], ['11'])
        protected = next(r for r in roles if r['mouse_id'] == '11')
        self.assertEqual(protected['group'], 'Development')
        self.assertTrue(protected['historical_source_overlap'])
        pilots = choose_pilots([{**protected, 'group': 'Development'}], {1011: 100}, ['11'])
        self.assertEqual(pilots, [])

    def test_source_domain_and_probe_rate_validity(self):
        good = {'quality': 'good', 'amplitude_cutoff': 0, 'presence_ratio': 1, 'isi_violations': 0}
        for key, value in [('amplitude_cutoff', -.01), ('isi_violations', -.01), ('presence_ratio', 1.01), ('presence_ratio', None), ('isi_violations', float('nan'))]:
            self.assertFalse(source_qualified({**good, key: value}))
        sessions = [{'id': 1, 'specimen_id': 1}]
        channels = [{'id': 1, 'ecephys_probe_id': 1, 'structure_acronym': 'VISp'}]
        units = [{**good, 'id': i, 'ecephys_channel_id': 1} for i in range(8)]
        for rate in [0, -1, None, float('inf'), float('nan')]:
            out = metadata_populations(sessions, [{'id': 1, 'ecephys_session_id': 1, 'sampling_rate': rate}], channels, units)
            self.assertFalse(out['all_populations'][0]['source_probe_valid'])
            self.assertEqual(out['selected'], [])

    def test_small_cohort_not_claimed_independent(self):
        rows = [{'mouse_id': str(i), 'session_id': i} for i in range(15)]
        self.assertTrue(all(r['group'] == 'Development' for r in allocate_roles(rows, [], [])))

    def test_transfer_failure_and_interruption_do_not_reset_consumption(self):
        work = Path(__file__).resolve().parents[1] / 'work'
        work.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=work) as d:
            p = Path(d) / 'ledger.json'; b = TransferBudget(p, 100)
            self.assertEqual(b.charge(60, 'partial'), 60)
            with self.assertRaises(ValueError): b.charge(41, 'overbudget')
            self.assertEqual(TransferBudget(p, 100).charge(40, 'remaining'), 100)
            self.assertEqual(read_json(p)['bytes'], 100)
            p.with_suffix('.lock').touch()
            with self.assertRaises(FileExistsError): b.charge(0, 'concurrent')


if __name__ == '__main__':
    unittest.main()
