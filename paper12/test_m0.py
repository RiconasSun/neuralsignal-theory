"""Metadata audit unit tests; fixtures never stand in for biological evidence."""
import io
import json
import unittest
import tempfile
import h5py
import numpy as np
from pathlib import Path
from unittest.mock import patch
from unittest.mock import MagicMock
from collections import Counter
from audit import classify, evaluate, potential, table, HERE
from acquire import FIELDS, validate_projection
from header_metadata import permitted, read_metadata, RangeReader, validate_dataset
from ibl_audit import cohort
from register import verify, sha

class MetadataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        (HERE/'replay').mkdir(exist_ok=True)
    def test_primary_threshold(self):
        self.assertTrue(potential(Counter(CA1=5, DG=5)))
        self.assertFalse(potential(Counter(CA1=4, DG=100)))
        self.assertFalse(potential(Counter(CA1=100, DG=4)))
    def test_exact_labels(self):
        for label in ('DG', 'DG-mo', 'DG-po', 'DG-sg'): self.assertEqual(classify(label), 'DG')
        for label in ('HPF', 'SUB', 'CA2', 'DG-other', None): self.assertIsNone(classify(label))
    def test_forbidden_metadata_paths(self):
        for p in ('/units/spike_times', '/acquisition/data', '/processing/firing_rate', '/intervals/x/../spikes'):
            self.assertFalse(permitted(p))
            with self.assertRaises(RuntimeError): read_metadata({}, p)
    def test_allowed_paths(self):
        for p in ('/session_start_time', '/intervals/x/start_time', '/intervals/invalid_times/tags'):
            self.assertTrue(permitted(p))
    def test_identity_projection(self):
        self.assertEqual(FIELDS['units'][1], 'id,ecephys_channel_id')
        for _, fields in FIELDS.values():
            for forbidden in ('rate', 'waveform', 'amplitude', 'presence_ratio', 'isi_violations'):
                self.assertNotIn(forbidden, fields.replace('sampling_rate', 'clock_frequency'))
    def test_full_actual_denominators(self):
        result = evaluate(*(table(n) for n in ('sessions','probes','channels','units')))
        self.assertEqual(result['denominator']['sessions'], 58)
        self.assertEqual(result['denominator']['units'], 135275)
        self.assertEqual(result['potential_paired_mice'], 51)
        self.assertEqual(result['orphans'], {})
        self.assertEqual(result['admitted_mice'], 0)
    def test_session_pseudoreplication(self):
        s = [{'id':'a','specimen_id':'m'}, {'id':'b','specimen_id':'m'}]
        r = evaluate(s, [], [], [])
        self.assertEqual(r['denominator']['mice'], 1)
    def test_missing_channel(self):
        r = evaluate([], [], [], [{'id':'u','ecephys_channel_id':'missing'}])
        self.assertEqual(r['orphans']['unit_channel'], 1)
    def test_duplicate_identity(self):
        with self.assertRaises(RuntimeError): evaluate([{'id':'a'}, {'id':'a'}], [], [], [])
    def test_range_read_bounds(self):
        reader = RangeReader('unused', 100)
        with self.assertRaises(RuntimeError): reader.read(-1)
        with self.assertRaises(RuntimeError): reader.read(131073)
        with self.assertRaises(ValueError): reader.seek(-1)
    def test_range_budget(self):
        reader = RangeReader('unused', 100, max_bytes=1)
        with self.assertRaises(RuntimeError): reader.read(2)
    def test_range_eof(self):
        reader = RangeReader('unused', 100)
        reader.seek(100)
        self.assertEqual(reader.read(5), b'')
    def test_bulk_response_not_consumed(self):
        reader = RangeReader('unused',100)
        res = MagicMock(status_code=200)
        context = MagicMock()
        context.__enter__.return_value = res
        reader.http.get = MagicMock(return_value=context)
        with self.assertRaises(RuntimeError): reader.read(8)
        res.raw.read.assert_not_called()
    def test_range_version_not_consumed(self):
        reader = RangeReader('unused',100,etag='old')
        res = MagicMock(status_code=206)
        res.headers = {'Content-Range':'bytes 0-7/100','ETag':'new'}
        context = MagicMock()
        context.__enter__.return_value = res
        reader.http.get = MagicMock(return_value=context)
        with self.assertRaises(RuntimeError): reader.read(8)
        res.raw.read.assert_not_called()
    def test_unexpected_projection_denied(self):
        with self.assertRaises(RuntimeError):
            validate_projection({'success':True, 'total_rows':1,'msg':[{'id':'1','firing_rate':2}]}, 'id')
    def test_truncated_projection_denied(self):
        with self.assertRaises(RuntimeError):
            validate_projection({'success':True, 'total_rows':2,'msg':[{'id':'1'}]}, 'id')
    def test_soft_and_external_links_denied(self):
        with tempfile.TemporaryDirectory(dir=HERE/'replay') as d:
            with h5py.File(Path(d)/'fixture.h5','w') as file:
                file.create_dataset('fake_values',data=np.arange(3,dtype=float))
                group = file.create_group('intervals').create_group('x')
                group['start_time'] = h5py.SoftLink('/fake_values')
                with self.assertRaises(RuntimeError): read_metadata(file,'/intervals/x/start_time')
                group['stop_time'] = h5py.ExternalLink('outside.h5','/values')
                with self.assertRaises(RuntimeError): validate_dataset(file,'/intervals/x/stop_time')
    def test_metadata_shapes_denied(self):
        with tempfile.TemporaryDirectory(dir=HERE/'replay') as d:
            with h5py.File(Path(d)/'fixture.h5','w') as file:
                file.create_dataset('/intervals/x/start_time',data=np.ones((2,2)))
                with self.assertRaises(RuntimeError): read_metadata(file,'/intervals/x/start_time')
    def test_correct_timestamp_dataset(self):
        with tempfile.TemporaryDirectory(dir=HERE/'replay') as d:
            with h5py.File(Path(d)/'fixture.h5','w') as file:
                file.create_dataset('/intervals/x/start_time',data=np.arange(20000,dtype=float))
                self.assertEqual(read_metadata(file,'/intervals/x/start_time').size,20000)
    def test_ibl_probe_join(self):
        fixture = [{'eid':'e','pid':'p','subject':'m','lab':'lab'}]
        rows = [{'eid':'e','pid':'other','cluster_id':'1','atlas_id':'1'}]
        _, result = cohort(rows,fixture,{'1':'CA1'})
        self.assertEqual(result['orphan_units']['unlisted_probe'],1)
    def test_ibl_duplicates(self):
        fixture = [{'eid':'e','pid':'p','subject':'m','lab':'lab'}]
        row = {'eid':'e','pid':'p','cluster_id':'1','atlas_id':'1'}
        with self.assertRaises(RuntimeError): cohort([row,row],fixture,{'1':'CA1'})
    def test_ibl_namespace(self):
        fixture = [{'eid':'e1','pid':'p1','subject':'m','lab':'lab1'},
                   {'eid':'e2','pid':'p2','subject':'m','lab':'lab2'}]
        _, result = cohort([],fixture,{})
        self.assertEqual(result['mice'],2)
    def test_header_policy_immutable(self):
        r = json.loads((HERE/'header_registration.json').read_text())
        self.assertEqual(r['policy_sha256'], sha(HERE/'HEADER_POLICY.json'))
    def test_past_papers_unchanged(self):
        self.assertGreater(len(verify()['prior_hashes']), 10000)
        original = json.loads((HERE/'ibl_registration.json').read_text())
        self.assertEqual(sha(HERE/'archive/ibl_audit_initial.py'),original['code_sha256'])
    def test_no_outcome_loader(self):
        for p in ('acquire.py', 'audit.py', 'support.py', 'header_metadata.py', 'raw_inventory.py'):
            source = (HERE / p).read_text()
            self.assertNotIn('get_session_data(', source)
            self.assertNotIn('np.load(', source)
    def test_full_header_denominator(self):
        records = [json.loads(p.read_text()) for p in (HERE/'metadata/headers_code1').glob('*.json')]
        self.assertEqual({r['session_id'] for r in records}, {r['id'] for r in table('sessions')})
        self.assertTrue(all(r['decoded_neural_values'] is False for r in records))
    def test_all_actual_links_passed(self):
        rows = [json.loads(p.read_text()) for p in (HERE/'metadata/link_audit').glob('*.json')]
        self.assertEqual(len(rows),58)
        self.assertTrue(all(r['pass'] and not r['decoded_values'] for r in rows))
    def test_no_scientific_pass(self):
        gate = json.loads((HERE/'results/allen_gate_result.json').read_text())
        self.assertFalse(gate['pass'])
        self.assertEqual(gate['admitted_mice'],0)
        final = json.loads((HERE/'results/gate_result.json').read_text())
        self.assertFalse(final['pass'])
        self.assertFalse(final['scientific_validation_pass'])
        self.assertEqual(final['warn_count'],5)

if __name__ == '__main__': unittest.main(verbosity=2)
