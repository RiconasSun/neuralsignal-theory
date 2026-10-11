import io
import sys
import unittest
from pathlib import Path

import h5py
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import run_r0_schema as schema


class SchemaTests(unittest.TestCase):
    def test_toronto_identity(self):
        self.assertEqual(schema.patient('sub-TWH088/session.nwb'), 'sub-TWH088')
        self.assertEqual(schema.patient('sub-P10HMH_2/session.nwb'), 'sub-P10HMH')
        self.assertNotEqual(schema.patient('sub-P27CS/x'), schema.patient('sub-P27HMH/x'))
        with self.assertRaises(RuntimeError):
            schema.patient('sub-unidentified/x')

    def fixture(self, phases, starts=None):
        n = len(phases)
        f = h5py.File(io.BytesIO(), 'w')
        f['units/id'] = np.arange(5)
        f['units/electrodes'] = np.zeros(5, dtype=int)
        f['general/extracellular_ephys/electrodes/location'] = np.array(['Right Hippocampus'], dtype=h5py.string_dtype())
        f['intervals/trials/start_time'] = np.arange(n) * 2. if starts is None else starts
        f['intervals/trials/stop_time'] = f['intervals/trials/start_time'][...] + .2
        f['intervals/trials/stim_phase'] = np.array(phases, dtype=h5py.string_dtype())
        return f

    def test_recog_is_recognition(self):
        with self.fixture(['learn'] * 40 + ['recog'] * 100) as file:
            result = schema.summarize(file, [])
        self.assertTrue(result['metadata_candidate'])
        self.assertEqual(result['calibration_train_rows'], list(range(40, 100)))
        self.assertEqual(result['locked_final_rows'], list(range(100, 140)))

    def test_unknown_phase_not_silently_excluded(self):
        with self.fixture(['unexpected']) as file:
            with self.assertRaises(RuntimeError):
                schema.summarize(file, [])

    def test_nonchronological_refused(self):
        with self.fixture(['recog', 'recog'], [2., 1.]) as file:
            with self.assertRaises(RuntimeError):
                schema.summarize(file, [])

    def test_overlap_not_eligible(self):
        with self.fixture(['recog'] * 40, np.arange(40) * .1) as file:
            result = schema.summarize(file, [])
        self.assertFalse(result['metadata_candidate'])


if __name__ == '__main__':
    unittest.main()
