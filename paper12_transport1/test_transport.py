import io
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
import requests
import common as r
from range_transport import RetryHTTP


class Response:
    def __init__(self,body=b'abcdefgh',status=206,etag='"e"',content_range='bytes 0-7/8'):
        self.raw=io.BytesIO(body);self.status_code=status
        self.headers={'ETag':etag,'Content-Range':content_range}
    def __enter__(self):return self
    def __exit__(self,*a):self.raw.close()


class HTTP:
    def __init__(self,items):self.items=iter(items);self.headers={};self.calls=0
    def get(self,*a,**kw):
        self.calls+=1;self.last_kwargs=kw;item=next(self.items)
        if isinstance(item,Exception):raise item
        return item
    def close(self):pass


class TransportTests(unittest.TestCase):
    def setUp(self):
        root=r.HERE/'replay/tests';root.mkdir(parents=True,exist_ok=True)
        self.temp=tempfile.TemporaryDirectory(dir=root);self.root=Path(self.temp.name)
        self.owner=SimpleNamespace(size=8,etag='"e"',file_id='f')
    def tearDown(self):
        if not self.root.resolve().is_relative_to((r.HERE/'replay/tests').resolve()):raise RuntimeError('BAD_FIXTURE_CLEANUP')
        self.temp.cleanup()
    def transport(self,items):
        self.http=HTTP(items);self.waits=[]
        return RetryHTTP(self.owner,self.root,lambda p:None,self.http,self.waits.append)
    def read(self,t):
        with t.get('synthetic',headers={'Range':'bytes=0-7'}) as response:return response.raw.read()
    def test_good_exact_bytes(self):self.assertEqual(self.read(self.transport([Response()])),b'abcdefgh')
    def test_two_timeouts_then_success(self):
        t=self.transport([requests.ReadTimeout(),requests.ReadTimeout(),Response()])
        self.assertEqual(self.read(t),b'abcdefgh');self.assertEqual(self.http.calls,3);self.assertEqual(self.waits,[2,4])
    def test_exhaustion_persists_across_restart(self):
        t=self.transport([requests.ReadTimeout()]*3)
        with self.assertRaisesRegex(RuntimeError,'UNRECOVERABLE'):self.read(t)
        t=self.transport([Response()])
        with self.assertRaisesRegex(RuntimeError,'UNRECOVERABLE'):self.read(t)
        self.assertEqual(self.http.calls,0)
    def test_cached_block_no_request(self):
        self.read(self.transport([Response()]));t=self.transport([])
        self.assertEqual(self.read(t),b'abcdefgh');self.assertEqual(self.http.calls,0)
    def test_corrupted_cache_stops_without_retry(self):
        self.read(self.transport([Response()]));(self.root/'chunk_0000000000000000/body.blob').write_bytes(b'corrupt!')
        t=self.transport([])
        with self.assertRaisesRegex(RuntimeError,'CACHE_INTEGRITY'):self.read(t)
        self.assertEqual(self.http.calls,0)
    def test_version_mismatch_fatal(self):
        t=self.transport([Response(etag='"changed"')])
        with self.assertRaisesRegex(RuntimeError,'VERSION_OR_RANGE'):self.read(t)
        self.assertEqual(self.http.calls,1)
    def test_short_body_fatal(self):
        t=self.transport([Response(body=b'ab')])
        with self.assertRaisesRegex(RuntimeError,'LENGTH_INVALID'):self.read(t)
        self.assertEqual(self.http.calls,1)
    def test_wrong_range_fatal(self):
        t=self.transport([Response(content_range='bytes 1-8/8')])
        with self.assertRaisesRegex(RuntimeError,'VERSION_OR_RANGE'):self.read(t)
    def test_transient_http_status(self):
        t=self.transport([Response(status=503),Response()]);self.assertEqual(self.read(t),b'abcdefgh')
    def test_interrupted_intent_consumes_attempt(self):
        t=self.transport([requests.ReadTimeout()]*3)
        ledger=self.root/'attempts_0000000000000000';ledger.mkdir()
        r.save(ledger/'1.intent.json',dict(source=dict(file_id='f',etag='"e"',size=8,start=0,end=7),attempt=1))
        with self.assertRaisesRegex(RuntimeError,'UNRECOVERABLE'):self.read(t)
        self.assertEqual(self.http.calls,2)
    def test_pending_data_not_accepted(self):
        p=self.root/'pending_incomplete';p.mkdir();(p/'body.blob').write_bytes(b'abcdefgh')
        t=self.transport([Response()]);self.read(t);self.assertEqual(self.http.calls,1)
    def test_invalid_range_never_requests(self):
        t=self.transport([])
        with self.assertRaisesRegex(RuntimeError,'PERMITTED_RANGE'):t.get('synthetic',headers={'Range':'bytes=1-7'})
        self.assertEqual(self.http.calls,0)
    def test_fatal_then_restart_never_requests(self):
        t=self.transport([Response(etag='"wrong"')])
        with self.assertRaises(RuntimeError):self.read(t)
        t=self.transport([Response()])
        with self.assertRaises(RuntimeError):self.read(t)
        self.assertEqual(self.http.calls,0)
    def test_saved_fatal_result_without_stop_file(self):
        t=self.transport([]);ledger=self.root/'attempts_0000000000000000';ledger.mkdir()
        r.save(ledger/'1.intent.json',dict(source=dict(file_id='f',etag='"e"',size=8,start=0,end=7),attempt=1))
        r.save(ledger/'1.result.json',dict(attempt=1,status='FATAL'))
        with self.assertRaisesRegex(RuntimeError,'PRESERVED_FATAL'):self.read(t)
        self.assertEqual(self.http.calls,0)
    def test_redirect_disabled(self):
        t=self.transport([Response()]);self.read(t)
        self.assertIs(self.http.last_kwargs['allow_redirects'],False)
    def test_redirect_status_fatal(self):
        t=self.transport([Response(status=302)])
        with self.assertRaises(RuntimeError):self.read(t)
        self.assertEqual(self.http.calls,1)


if __name__=='__main__':unittest.main()
