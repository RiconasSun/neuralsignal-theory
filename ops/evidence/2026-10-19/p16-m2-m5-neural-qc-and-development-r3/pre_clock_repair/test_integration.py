"""Synthetic actual production source pipeline with mock HTTP serving an owned HDF5 fixture."""
from pathlib import Path
import copy
import json
import tempfile
import time
import unittest
from unittest.mock import patch
import h5py
import numpy as np
from .core import P, SourceStop, sha
from .transport import BudgetJournal
from . import test_neural as fixture_module
from .test_transport import Response
from .run_m2 import process_source


class ProductionSourceIntegration(unittest.TestCase):
    def setUp(self):
        self.fixture = fixture_module.NativeReaderTests(); self.fixture.setUp()
        base = P/'work/private'; base.mkdir(parents=True, exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=base, prefix='synthetic-production-')
        self.p = Path(self.temp.name); self.e = self.p/'evidence'; self.e.mkdir()
        (self.p/'results').mkdir()
        (self.e/'PREACCESS_APPROVAL.json').write_text('SYNTHETIC FIXTURE ONLY', encoding='utf8')
        self.item = copy.deepcopy(self.fixture.item); self.reg = copy.deepcopy(self.fixture.reg)
        self.calls = []
    def tearDown(self): self.temp.cleanup(); self.fixture.tearDown()
    def run_pipeline(self):
        data = self.fixture.path.read_bytes(); self.item['size'] = len(data); self.reg['objects'] = [self.item]
        (self.p/'ACCESS_REGISTRATION.json').write_text(json.dumps(self.reg), encoding='utf8')
        (self.p/'SOURCE_CANDIDATE_CERTIFICATES.json').write_text(json.dumps({'candidates': [
            {'session_id': sid, 'unit_id': uid, **cert} for (sid, uid), cert in self.fixture.certs.items()]}), encoding='utf8')
        def get(url, **kwargs):
            self.calls.append(kwargs); offset = kwargs['params']['p16_r3_offset']; length = kwargs['params']['p16_r3_length']
            return Response(data[offset:offset+length], offset, length, len(data), self.item['etag'])
        now = time.monotonic(); stage = {'start_monotonic': now, 'deadline_monotonic': now+60}
        journal = BudgetJournal(self.p/'results/budget.jsonl', self.reg)
        try:
            with patch('paper16_dev_r3.run_m2.P', self.p), patch('paper16_dev_r3.run_m2.E', self.e), \
                 patch('paper16_dev_r3.run_m2.source_inputs', return_value=(self.fixture.header, self.fixture.flashes,
                       {'missing': np.zeros((150, 6), dtype=bool)}, {'synthetic_only': True})), \
                 patch('requests.Session.get', side_effect=get):
                return process_source(self.item, self.reg, stage, journal)
        finally: journal.close()
    def test_actual_h5py_range_A_QC_private_persistence_and_common_support(self):
        result = self.run_pipeline()
        self.assertTrue(result['source_pass']); self.assertTrue(result['selection']['admitted'])
        self.assertEqual(result['selection']['selected_unit_ids'], list(range(101, 109)))
        self.assertEqual(result['private_A_capture_count'], 8)
        self.assertFalse(result['B_E_arrays_exported']); self.assertEqual(result['optimizer_attempts'], 0)
        self.assertTrue(self.calls)
        for path in (self.p/'results').rglob('*'):
            if path.is_file(): self.assertNotIn(path.suffix, ['.npz', '.npy', '.bin', '.h5'])
        private = list((self.p/'work/private/A').rglob('*.npz')); self.assertEqual(len(private), 8)
        for path in private:
            with np.load(path, allow_pickle=False) as a:
                self.assertLess(a['timestamps'].max(), 180.)
                self.assertTrue((a['original_ordinals'] < 90).all())
        rows = [json.loads(x) for x in (self.p/'results/sources'/str(self.item['session_id'])/'UNIT_QC.jsonl').read_text().splitlines()]
        self.assertEqual(len(rows), 8)
        for row in rows: self.assertEqual(row['A_physiology']['spikes'], 180)
    def test_late_selected_row_failure_retains_partial_and_denies_repeat(self):
        with h5py.File(self.fixture.path, 'r+') as f: f['/units/spike_times'][601] = np.nan
        with self.assertRaises(SourceStop): self.run_pipeline()
        folder = self.p/'results/sources'/str(self.item['session_id'])
        failure = json.loads((folder/'FAILURE.json').read_text())
        self.assertEqual(failure['completed_private_A_captures'], 2)
        self.assertFalse((folder/'RESULT.json').exists())
        self.assertEqual(len(list((self.p/'work/private/A').rglob('*.npz'))), 2)
        before = len(self.calls)
        with self.assertRaises(FileExistsError): self.run_pipeline()
        self.assertEqual(len(self.calls), before)


if __name__ == '__main__': unittest.main(verbosity=2)
