import io
import sys
import unittest
from pathlib import Path

import h5py
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import run_r0_amend1_repair as r


class RepairTests(unittest.TestCase):
    def test_rejected_unit_reads_remain_logged(self):
        with h5py.File(io.BytesIO(), 'w') as f:
            for t, values in [(1, [-1.] * 20), (2, [-1., -2.]), (3, [np.nan]), (4, [np.nan])]:
                g = f.create_group(f'Spike_Times_Unit_1_uAHL_2_Trial_{t}')
                g.attrs['unit'] = 's'
                g['data'] = values
            seen = []
            def reader(g):
                self.assertNotIn('Trial_4', g.name)
                seen.append(g.name)
                return g['data'][...]
            sel, tr, val, qc, ledger = r.traced_partition_arrays(f, {1: {'microwire': 'uAHL2', 'anatomical_location': 'Left Hippocampus'}}, {'train': [1, 2], 'validation': [3], 'test': [4]}, reader)
        self.assertEqual(sel, [])
        self.assertEqual(len(seen), 2)
        self.assertEqual([x['trial'] for x in ledger], [1, 2])
        self.assertTrue(all(x['decode_completed'] for x in ledger))
        self.assertFalse(qc[0]['admitted'])

    def test_missing_saved_artifact_stops_before_hash_or_QC(self):
        seen = []
        with self.assertRaises(ValueError):
            r.preflight_saved(['missing.json'], {'other.json': 'hash'}, exists=lambda p: False, digest=lambda p: seen.append(p))
        self.assertEqual(seen, [])

    def test_corrupt_saved_artifact_refused(self):
        with self.assertRaises(ValueError):
            r.preflight_saved(['x'], {'x': 'expected'}, exists=lambda p: True, digest=lambda p: 'corrupt')

    def test_complete_saved_artifact_accepted(self):
        r.preflight_saved(['x'], {'x': 'expected'}, exists=lambda p: True, digest=lambda p: 'expected')


if __name__ == '__main__':
    unittest.main()
