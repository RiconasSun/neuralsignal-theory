import io
import json
import sys
import unittest
from pathlib import Path

import h5py
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import run_r0_amend1 as a


class AmendmentTests(unittest.TestCase):
    def test_exact_half_open_bins(self):
        b = a.count_array(np.array([-6., -5.9, -.1, 0., 2.]))
        self.assertEqual(b.sum(), 3)
        self.assertEqual(b[[0, 1, 59]].tolist(), [1, 1, 1])

    def test_invalid_allowed_values_fail(self):
        for x in [[float('nan')], [-6.1], [2.1], [-1., -2.]]:
            with self.assertRaises(ValueError):
                a.count_array(np.array(x))

    def test_anatomy_excludes_other_MTL(self):
        def row(label):
            return {'anatomical_location': label, **{'macro_contact_mni_' + x: '1' for x in 'xyz'}}
        self.assertTrue(a.admissible_unit(row('Left Hippocampus')))
        self.assertFalse(a.admissible_unit(row('Left Amygdala')))
        self.assertFalse(a.admissible_unit(row('Left entorhinal cortex')))

    def fixture(self, training_spikes=20, validation_spikes=0, poison_test=True):
        f = h5py.File(io.BytesIO(), 'w')
        for t in [1, 2, 3]:
            g = f.create_group(f'Spike_Times_Unit_1_uAHL_2_Trial_{t}')
            g.attrs['unit'] = 's'
            g['data'] = np.array([-1.] * (training_spikes if t == 1 else validation_spikes if t == 2 else 1))
        return f

    def test_forbidden_values_never_read(self):
        seen = []
        with self.fixture() as f:
            def read(g):
                if 'Trial_3' in g.name:
                    self.fail('Oldtest dataset dereferenced')
                seen.append(g.name)
                return g['data'][...]
            sel, tr, val, q, ledger = a.partition_arrays(f, {1: {'microwire': 'uAHL2', 'anatomical_location': 'Left Hippocampus'}}, {'train': [1], 'validation': [2], 'test': [3]}, read)
        self.assertEqual(sel, [1])
        self.assertEqual(tr.sum(), 20)
        self.assertEqual(val.sum(), 0)
        self.assertEqual(len(seen), 2)
        self.assertTrue(all(x['trial'] != 3 for x in ledger))

    def test_validation_rates_cannot_select_unit(self):
        with self.fixture(19, 1000) as f:
            def read(g):
                self.assertIn('Trial_1', g.name)
                return g['data'][...]
            sel, tr, val, q, _ = a.partition_arrays(f, {1: {'microwire': 'uAHL2', 'anatomical_location': 'Left Hippocampus'}}, {'train': [1], 'validation': [2], 'test': [3]}, read)
        self.assertEqual(sel, [])
        self.assertFalse(q[0]['admitted'])

    def test_partitions_overlap_refused(self):
        with self.assertRaises(ValueError):
            a.partition_arrays({}, {}, {'train': [1], 'validation': [2], 'test': [1]})

    def test_missing_array_not_zero_firing(self):
        sel, _, _, q, _ = a.partition_arrays({}, {1: {'microwire': 'uAHL2', 'anatomical_location': 'Left Hippocampus'}}, {'train': [1], 'validation': [2], 'test': [3]})
        self.assertEqual(sel, [])
        self.assertFalse(q[0]['admitted'])
        self.assertIn('Missing training observation', q[0]['reason'])

    def test_sensitivity_subject_not_session(self):
        r = [{'admitted': True, 'subject': 's1', 'usable_trials': 32, 'simultaneous_hippocampal_units': 5}] * 3
        self.assertEqual(a.sensitivity(r)[0]['subjects'], 1)
        self.assertEqual(a.sensitivity(r)[0]['sessions'], 3)

    def test_authorized_threshold_and_immutable_old_protocol(self):
        new = a.load(a.base.STUDY / 'protocol/r0_amendment1.json')
        old = a.load(a.base.STUDY / 'protocol/protocol.json')
        self.assertEqual(new['development_eligibility_override'], {'minimum_usable_trials_session': 32, 'minimum_training_trials': 24, 'minimum_validation_trials': 8})
        self.assertEqual(old['eligibility']['minimum_valid_trials_session'], 40)
        self.assertEqual(new['unchanged']['minimum_independent_subjects'], 8)
        self.assertTrue(new['unchanged']['external60_40_split_unchanged'])


if __name__ == '__main__':
    unittest.main()
