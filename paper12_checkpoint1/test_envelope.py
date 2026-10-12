import hashlib
import unittest
from envelope import pack,unpack


class EnvelopeTests(unittest.TestCase):
    def setUp(self):self.body=b'synthetic payload';self.source=dict(source='synthetic',version=1);self.digest=hashlib.sha256(self.body).hexdigest()
    def test_roundtrip(self):self.assertEqual(unpack(pack(self.body,self.source),self.source,self.digest),self.body)
    def test_partial(self):
        with self.assertRaises(ValueError):unpack(pack(self.body,self.source)[:-1],self.source,self.digest)
    def test_corrupt(self):
        with self.assertRaises(ValueError):unpack(pack(self.body,self.source)[:-1]+b'x',self.source,self.digest)
    def test_source(self):
        with self.assertRaises(ValueError):unpack(pack(self.body,self.source),dict(source='other'),self.digest)
    def test_hash(self):
        with self.assertRaises(ValueError):unpack(pack(self.body,self.source),self.source,'0'*64)
    def test_trailing(self):
        with self.assertRaises(ValueError):unpack(pack(self.body,self.source)+b'trailing',self.source,self.digest)
    def test_empty(self):
        with self.assertRaises(ValueError):pack(b'',self.source)


if __name__=='__main__':unittest.main()
