"""Synthetic source-pinning race and partial-file regression tests."""
import datetime
import hashlib
import io
import tempfile
import unittest
from pathlib import Path
from .source import P
from .source_integrity import conditional_download, verify_etag_bytes


class Body(io.BytesIO):
    def __init__(self,b):super().__init__(b);self.reads=0
    def read(self,n=-1):self.reads+=1;return super().read(n)


class Client:
    def __init__(self,response):self.response=response;self.kwargs=None
    def get_object(self,**kwargs):self.kwargs=kwargs;return self.response


class IntegrityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        (P/'work/test_tmp').mkdir(parents=True,exist_ok=True)
    def fixture(self):
        when=datetime.datetime(2026,1,1,tzinfo=datetime.timezone.utc);b=b'frozen-source'
        pin=dict(key='key',etag=hashlib.md5(b).hexdigest(),bytes=len(b),version_id=None,
            version_id_header_present=False,last_modified=when.isoformat())
        body=Body(b);response=dict(ETag='"'+pin['etag']+'"',ContentLength=len(b),LastModified=when,Body=body)
        return pin,body,response
    def test_actual_get_uses_frozen_ifmatch(self):
        pin,body,response=self.fixture();client=Client(response)
        with tempfile.TemporaryDirectory(dir=P/'work/test_tmp') as d:
            dest=Path(d)/'source';conditional_download(client,'bucket',pin,pin,dest)
            self.assertEqual(dest.read_bytes(),b'frozen-source')
        self.assertEqual(client.kwargs['IfMatch'],'"'+pin['etag']+'"');self.assertNotIn('VersionId',client.kwargs)
    def test_changed_response_denied_before_payload_use(self):
        pin,body,response=self.fixture();response['ETag']='"altered"'
        with tempfile.TemporaryDirectory(dir=P/'work/test_tmp') as d:
            dest=Path(d)/'source'
            with self.assertRaises(ValueError):conditional_download(Client(response),'bucket',pin,pin,dest)
            self.assertFalse(dest.exists());self.assertFalse(dest.with_name('source.partial').exists())
        self.assertEqual(body.reads,0)
    def test_version_must_match_actual_response(self):
        pin,body,response=self.fixture();pin['version_id']='registered';pin['version_id_header_present']=True
        response['VersionId']='different'
        with tempfile.TemporaryDirectory(dir=P/'work/test_tmp') as d:
            with self.assertRaises(ValueError):conditional_download(Client(response),'bucket',pin,pin,Path(d)/'source')
        self.assertEqual(body.reads,0)
    def test_truncated_body_retains_partial(self):
        pin,body,response=self.fixture();response['Body']=Body(b'bad')
        with tempfile.TemporaryDirectory(dir=P/'work/test_tmp') as d:
            dest=Path(d)/'source'
            with self.assertRaises(ValueError):conditional_download(Client(response),'bucket',pin,pin,dest)
            self.assertFalse(dest.exists());self.assertEqual(dest.with_name('source.partial').read_bytes(),b'bad')
    def test_existing_partial_cannot_be_overwritten(self):
        pin,body,response=self.fixture()
        with tempfile.TemporaryDirectory(dir=P/'work/test_tmp') as d:
            dest=Path(d)/'source';dest.with_name('source.partial').write_bytes(b'old')
            with self.assertRaises(FileExistsError):conditional_download(Client(response),'bucket',pin,pin,dest)
            self.assertEqual(dest.with_name('source.partial').read_bytes(),b'old')
        self.assertEqual(body.reads,0)
    def test_multipart_etag_integrity_and_unknown_layout(self):
        b=b'abcde';parts=[b[:3],b[3:]]
        etag=hashlib.md5(b''.join(hashlib.md5(p).digest() for p in parts)).hexdigest()+'-2'
        self.assertTrue(verify_etag_bytes(b,etag,3));self.assertFalse(verify_etag_bytes(b'abcdX',etag,3))
        self.assertFalse(verify_etag_bytes(b,etag,4*1024*1024))


if __name__=='__main__':unittest.main(verbosity=2)
