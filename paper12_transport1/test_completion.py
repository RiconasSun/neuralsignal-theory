import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import common as r
import run_recovery as driver


class CompletionTests(unittest.TestCase):
    def setUp(self):
        root=r.HERE/'replay/tests';root.mkdir(parents=True,exist_ok=True)
        self.tmp=tempfile.TemporaryDirectory(dir=root)
        self.old=Path(self.tmp.name)
        self.animal=dict(session_id='1',mouse_id='2',group='development')
        self.source=dict(etag='frozen')
        self.receipt=dict(self.animal,source_etag='frozen',qc_partition='train',
            custody_artifact_namespace='transport_recovery1/sessions/run_fixture',
            final_values_exposed_to_analysis=False,final_holdout_evaluated=False,
            raw_vectors_exported=False,ciphertext_receipts={})
        self.private=self.old/'.private'/self.receipt['custody_artifact_namespace']/'1'
        self.private.mkdir(parents=True)
        for part in ('A','B'):
            path=self.private/(part+'.gcm');path.write_bytes(b'fixture ciphertext')
            (self.private/(part+'.key')).write_bytes(b'k'*32)
            self.receipt['ciphertext_receipts'][part]=dict(ciphertext_sha256=r.sha(path),ciphertext_bytes=path.stat().st_size)
        self.patch=patch.object(r,'OLD',self.old);self.patch.start()

    def tearDown(self):
        self.patch.stop();self.tmp.cleanup()

    def verify(self):
        driver.validate_completion(self.receipt,self.animal,self.source)

    def test_valid(self):self.verify()

    def test_corrupted_before_first_seal_never_published(self):
        (self.private/'A.gcm').write_bytes(b'corrupt')
        with self.assertRaisesRegex(RuntimeError,'CIPHERTEXT'):
            driver.seal_session(self.receipt,self.animal,self.source)
        self.assertFalse((self.old/'.private/transport_recovery1/completed_issuers/1.json').exists())

    def test_identity(self):
        self.receipt['mouse_id']='other'
        with self.assertRaisesRegex(RuntimeError,'IDENTITY'):self.verify()

    def test_source(self):
        self.receipt['source_etag']='other'
        with self.assertRaisesRegex(RuntimeError,'SOURCE'):self.verify()

    def test_compartment(self):
        self.receipt['ciphertext_receipts'].pop('B')
        with self.assertRaisesRegex(RuntimeError,'COMPARTMENTS'):self.verify()

    def test_access(self):
        self.receipt['final_values_exposed_to_analysis']=True
        with self.assertRaisesRegex(RuntimeError,'ACCESS'):self.verify()

    def test_key_length(self):
        (self.private/'A.key').write_bytes(b'bad')
        with self.assertRaisesRegex(RuntimeError,'KEY'):self.verify()

    def test_storage_overlay_only(self):
        old=driver.index2.session_callable();new=driver.extractor()
        self.assertEqual(old.__code__.co_code,new.__code__.co_code)
        self.assertEqual(sum(a!=b for a,b in zip(old.__code__.co_consts,new.__code__.co_consts)),3)


if __name__=='__main__':unittest.main()
