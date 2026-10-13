"""Transport fixture tests, not a native checkpoint campaign or neural experiment."""
import hashlib
import io
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import patch
import requests
import study as r
import transport as t
import test_resume


class FakeHTTP:
    def __init__(self,values):self.values=list(values);self.headers={};self.calls=[]
    def get(self,*args,**kwargs):
        self.calls.append((args,kwargs));value=self.values.pop(0)
        if isinstance(value,Exception):raise value
        return value
    def close(self):pass


class TransportTests(unittest.TestCase):
    def setUp(self):
        root=r.HERE/'replay';root.mkdir(exist_ok=True)
        self.temp=tempfile.TemporaryDirectory(dir=root)
        self.root=Path(self.temp.name);self.old=self.root/'old';self.old.mkdir()
        self.new=self.root/'new';self.new.mkdir()
        self.owner=types.SimpleNamespace(size=9,etag='e',file_id='synthetic',session_id='fixture')
        self.source=dict(file_id='synthetic',etag='e',size=9,start=0,end=8)
        def prepare(path):path=Path(path);path.mkdir(parents=True,exist_ok=True);return path
        def durable(path,value):r.save(path,value,True)
        def commit(root,name,body,source):
            target=Path(root)/(name+'.checkpoint');target.write_bytes(body)
            return dict(committed=True,artifact_sha256=r.sha(target),body_sha256=hashlib.sha256(body).hexdigest())
        self.patches=[patch.object(t.a,'prepare',prepare),patch.object(t.a,'durable_record',durable),
                      patch.object(t.a,'commit',commit),patch.object(t.a,'read',lambda path,source,digest:Path(path).read_bytes())]
        for p in self.patches:p.start()
    def tearDown(self):
        for p in reversed(self.patches):p.stop()
        self.temp.cleanup()
    def response(self,status=206,body=b'synthetic',etag='e'):
        response=t.Response(body,{'ETag':etag,'Content-Range':'bytes 0-8/9'})
        response.status_code=status;return response
    def reader(self,values):
        session=FakeHTTP(values)
        return t.HTTP(self.owner,self.new,self.old,session,sleep=lambda _:None),session
    def get(self,reader):return reader.get('https://same-source.invalid',headers={'Range':'bytes=0-8','If-Match':'e'})

    def test_response_and_cache(self):
        reader,session=self.reader([self.response()])
        self.assertEqual(self.get(reader).raw.read(),b'synthetic')
        self.assertEqual(self.get(reader).raw.read(),b'synthetic')
        self.assertEqual(len(session.calls),1);self.assertFalse(session.calls[0][1]['allow_redirects'])
        self.assertEqual(session.calls[0][1]['timeout'],(20,120))

    def test_carried_budget_limits_new_attempts(self):
        source,block=test_resume.Correctness().fixture(self.old,2)
        for n in (1,2):r.save(self.old/'attempts_0000000000000000'/(str(n)+'.result.json'),dict(attempt=n,status='TRANSIENT_FAILURE'))
        (block/'body.blob').unlink();(block/'marker.json').unlink();block.rmdir()
        reader,session=self.reader([requests.Timeout()])
        with self.assertRaisesRegex(RuntimeError,'TRANSPORT_UNRECOVERABLE'):self.get(reader)
        self.assertEqual(len(session.calls),1)
        with self.assertRaisesRegex(RuntimeError,'PRESERVED_NEW_TRANSPORT_STOP'):self.get(reader)
        self.assertEqual(len(session.calls),1)

    def test_pending_no_new_request(self):
        test_resume.Correctness().fixture(self.old,pending=True)
        reader,session=self.reader([])
        self.assertEqual(self.get(reader).raw.read(),b'synthetic')
        self.assertEqual(session.calls,[]);self.assertEqual(reader.stats['old_pending_recovered'],1)

    def test_missing_old_verified_no_request(self):
        _,block=test_resume.Correctness().fixture(self.old)
        (block/'body.blob').unlink();(block/'marker.json').unlink();block.rmdir()
        reader,session=self.reader([])
        with self.assertRaisesRegex(RuntimeError,'OLD_VERIFIED_BLOCK_ARTIFACT_MISSING'):self.get(reader)
        self.assertEqual(session.calls,[])

    def test_bad_version_no_retry(self):
        reader,session=self.reader([self.response(etag='changed')])
        with self.assertRaisesRegex(RuntimeError,'SOURCE_VERSION_OR_RANGE_INVALID'):self.get(reader)
        self.assertEqual(len(session.calls),1)

    def test_partial_no_retry(self):
        reader,session=self.reader([self.response(body=b'x')])
        with self.assertRaisesRegex(RuntimeError,'SOURCE_RESPONSE_LENGTH_INVALID'):self.get(reader)
        self.assertEqual(len(session.calls),1)

    def test_redirect_fatal(self):
        reader,session=self.reader([self.response(status=302)])
        with self.assertRaisesRegex(RuntimeError,'SOURCE_VERSION_OR_RANGE_INVALID'):self.get(reader)
        self.assertEqual(len(session.calls),1)

    def test_three_transients_stop(self):
        reader,session=self.reader([requests.Timeout(),requests.ConnectionError(),requests.Timeout()])
        with self.assertRaisesRegex(RuntimeError,'TRANSPORT_UNRECOVERABLE'):self.get(reader)
        self.assertEqual(len(session.calls),3)

    def test_permission_failure_stops(self):
        reader,session=self.reader([self.response()])
        with patch.object(t.a,'commit',side_effect=RuntimeError('ATOMIC_COMMIT_SAFE_STOP')):
            with self.assertRaisesRegex(RuntimeError,'ATOMIC_COMMIT_SAFE_STOP'):self.get(reader)
        with self.assertRaisesRegex(RuntimeError,'PRESERVED_NEW_TRANSPORT_STOP'):self.get(reader)
        self.assertEqual(len(session.calls),1)


if __name__=='__main__':unittest.main()
