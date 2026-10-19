"""Synthetic HTTP/header/byte/deadline/cache tests; no real request permitted."""
from pathlib import Path
import copy
import io
import json
import tempfile
import time
import unittest
from unittest.mock import patch
from .core import P, load, SourceStop, ResourceStop
from .transport import RangeReader, BudgetJournal


class Response:
    def __init__(self, data, offset, length, total, etag, status=206, wrong_range=False):
        self.status_code = status
        self.headers = {'ETag': etag, 'Content-Range': 'wrong' if wrong_range else f'bytes {offset}-{offset+length-1}/{total}'}
        self.raw = io.BytesIO(data)
    def __enter__(self): return self
    def __exit__(self, *args): return False


class TransportTests(unittest.TestCase):
    def setUp(self):
        base = P/'work/private'; base.mkdir(parents=True, exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=base, prefix='synthetic-http-')
        self.root = Path(self.temp.name)
        self.reg = load(P/'ACCESS_REGISTRATION.json')
        self.item = copy.deepcopy(self.reg['objects'][0]); self.item['size'] = 100
        self.reg['objects'] = [self.item]
        self.reg['resources'].update({'per_request_bytes_max': 32, 'logical_read_bytes_max': 100,
                                     'aggregate_reserved_bytes_max': 200, 'per_source_reserved_bytes_max': 200})
        now = time.monotonic(); self.stage = {'start_monotonic': now, 'deadline_monotonic': now+60}
        self.journal = BudgetJournal(self.root/'journal.jsonl', self.reg)
        self.data = bytes(range(100)); self.calls = []
    def tearDown(self):
        self.journal.close(); self.temp.cleanup()
    def request(self, url, **kw):
        self.calls.append((url, kw)); offset = kw['params']['p16_r3_offset']; length = kw['params']['p16_r3_length']
        return Response(self.data[offset:offset+length], offset, length, 100, self.item['etag'])
    def reader(self, **kw): return RangeReader(self.item, self.reg, self.stage, self.journal, self.root/'cache', **kw)

    def test_exact_bounded_ranges_cache_and_lossless_cross_block_reads(self):
        with patch('requests.Session.get', self.request), self.reader() as reader:
            reader.seek(25); self.assertEqual(reader.read(20), self.data[25:45])
            reader.seek(0); self.assertEqual(reader.read(64), self.data[:64])
            self.assertEqual(len(self.calls), 2)
        with patch('requests.Session.get', side_effect=AssertionError('Network forbidden')), self.reader(offline=True) as reader:
            reader.seek(20); self.assertEqual(reader.read(40), self.data[20:60])
        self.assertEqual(self.journal.reserved, 66); self.assertEqual(self.journal.payload, 64)
        self.assertEqual(self.calls[0][1]['allow_redirects'], False)
        self.assertEqual(self.calls[0][1]['headers']['If-Match'], self.item['etag'])

    def test_per_source_and_aggregate_budget_deny_before_next_network(self):
        for scope in ['per_source_reserved_bytes_max', 'aggregate_reserved_bytes_max']:
            with self.subTest(scope=scope):
                self.reg['resources'][scope] = 1
                with patch('requests.Session.get', side_effect=AssertionError('Network forbidden')), self.reader() as reader:
                    with self.assertRaises(ResourceStop): reader.read(1)
                self.reg['resources'][scope] = 200
        self.assertEqual(self.journal.reserved, 0)

    def test_wrong_status_range_etag_no_body_or_retry(self):
        for k, kw in [('status', {'status': 200}), ('range', {'wrong_range': True}), ('etag', {})]:
            with self.subTest(k=k):
                response = Response(self.data[:32], 0, 32, 100, 'wrong' if k == 'etag' else self.item['etag'], **kw)
                with patch('requests.Session.get', return_value=response) as request, self.reader() as reader:
                    with self.assertRaises(SourceStop): reader.read(1)
                    self.assertEqual(request.call_count, 1); self.assertEqual(response.raw.tell(), 0)

    def test_partial_failure_bytes_preserved_and_not_retried(self):
        response = Response(b'partial', 0, 32, 100, self.item['etag'])
        with patch('requests.Session.get', return_value=response) as request, self.reader() as reader:
            with self.assertRaises(SourceStop): reader.read(1)
            self.assertEqual(request.call_count, 1)
        raw = self.root/'cache'/str(self.item['session_id'])/'0.bin'
        self.assertEqual(raw.read_bytes(), b'partial')
        with patch('requests.Session.get', side_effect=AssertionError('No retry')), self.reader() as reader:
            with self.assertRaises(SourceStop): reader.read(1)
        self.assertEqual(self.journal.payload, 7)

    def test_deadline_oversize_and_Final_denied_without_network(self):
        with patch('requests.Session.get', side_effect=AssertionError('No network')):
            with self.reader() as reader:
                with self.assertRaises(ResourceStop): reader.read(-1)
                with self.assertRaises(ResourceStop): reader.read(101)
            self.stage['deadline_monotonic'] = time.monotonic()-1
            with self.assertRaises(ResourceStop): self.reader()
            self.stage['deadline_monotonic'] = time.monotonic()+60
            self.item = dict(self.item, session_id=self.reg['denied_final_session_ids'][0])
            with self.assertRaises(SourceStop): self.reader()

    def test_cache_tampering_and_public_cache_path_denied(self):
        with patch('requests.Session.get', self.request), self.reader() as reader: reader.read(1)
        raw = self.root/'cache'/str(self.item['session_id'])/'0.bin'; raw.write_bytes(b'x'*32)
        with patch('requests.Session.get', side_effect=AssertionError('No fallback')), self.reader(offline=True) as reader:
            with self.assertRaises(SourceStop): reader.read(1)
        with self.assertRaises(SourceStop): RangeReader(self.item, self.reg, self.stage, self.journal, P/'results')

    def test_cache_missing_offline_denial_and_append_accounting(self):
        with self.reader(offline=True) as reader:
            with self.assertRaises(SourceStop): reader.read(1)
        with patch('requests.Session.get', self.request), self.reader() as reader: reader.read(1)
        self.journal.close()
        other = BudgetJournal(self.root/'journal.jsonl', self.reg, append=True)
        self.assertEqual(other.reserved, 33); self.assertEqual(other.payload, 32)
        self.assertEqual(other.by_source[self.item['session_id']]['requests'], 1)
        other.close()


if __name__ == '__main__': unittest.main(verbosity=2)
