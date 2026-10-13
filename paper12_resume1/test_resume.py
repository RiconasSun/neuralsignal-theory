import hashlib
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import patch
import study as r
import verified_atomic as a
import transport as t


class Correctness(unittest.TestCase):
    def temporary(self):
        root=r.HERE/'replay';root.mkdir(exist_ok=True)
        return tempfile.TemporaryDirectory(dir=root)

    def test_unchanged_bytecode(self):self.assertTrue(a.verify_parity())

    def test_outside_scope_denied(self):
        with self.assertRaises(RuntimeError):a.check_path(r.OLD/'.private/forbidden')

    def test_path_traversal_denied(self):
        with self.assertRaises(RuntimeError):a.check_path(r.HERE/'.private/../bad')

    def test_frozen_science(self):
        p=r.load(r.HERE/'protocol.json')
        self.assertEqual(p['science']['seeds'],[11,23,37])
        self.assertEqual(p['science']['configurations'],57)
        self.assertEqual(p['transport']['attempts_per_chunk_total'],3)

    def test_source_denominator(self):
        p=r.load(r.HERE/'registration.json')
        self.assertEqual(len(p['sources']),26);self.assertEqual(len(p['reuse']),8)

    def test_ranges(self):
        self.assertEqual(t.byte_range('bytes=0-8',9),(0,8))
        with self.assertRaises(RuntimeError):t.byte_range('bytes=1-8',9)

    def test_encoding(self):
        with self.assertRaises(RuntimeError):t.validate_headers(206,{'ETag':'e','Content-Range':'bytes 0-8/9','Content-Encoding':'gzip'},0,8,9,'e')

    def test_partial(self):
        with self.assertRaises(RuntimeError):t.validate(206,{'ETag':'e','Content-Range':'bytes 0-8/9'},b'x',0,8,9,'e')

    def fixture(self,root,attempt=1,pending=False):
        source=dict(file_id='synthetic',etag='e',size=9,start=0,end=8)
        ledger=root/'attempts_0000000000000000';ledger.mkdir()
        for n in range(1,attempt+1):
            r.save(ledger/(str(n)+'.intent.json'),dict(source=source,attempt=n))
            r.save(ledger/(str(n)+'.result.json'),dict(attempt=n,status='VERIFIED_COMPLETE_BLOCK' if n==attempt else 'TRANSIENT_FAILURE'))
        block=root/('pending_fixture' if pending else 'chunk_0000000000000000');block.mkdir()
        (block/'body.blob').write_bytes(b'synthetic')
        r.save(block/'marker.json',dict(source=source,sha256=hashlib.sha256(b'synthetic').hexdigest()))
        return source,block

    def test_budget_carried_three(self):
        with self.temporary() as path:
            source,_=self.fixture(Path(path),3)
            self.assertEqual(t.prior_budget(Path(path),source),3)

    def test_pending_reverified(self):
        with self.temporary() as path:
            source,_=self.fixture(Path(path),pending=True)
            body,used,pending=t.prior_block(Path(path),source)
            self.assertEqual(body,b'synthetic');self.assertEqual(used,1);self.assertTrue(pending)

    def test_corrupt_old_denied(self):
        with self.temporary() as path:
            source,block=self.fixture(Path(path))
            (block/'body.blob').write_bytes(b'corrupted')
            with self.assertRaises(RuntimeError):t.prior_block(Path(path),source)

    def test_fatal_old_denied(self):
        with self.temporary() as path:
            source,_=self.fixture(Path(path))
            r.save(Path(path)/'attempts_0000000000000000/1.result.json',dict(attempt=1,status='FATAL'))
            with self.assertRaises(RuntimeError):t.prior_budget(Path(path),source)

    def test_source_identity_denied(self):
        with self.temporary() as path:
            source,_=self.fixture(Path(path));source['etag']='other'
            with self.assertRaises(RuntimeError):t.prior_budget(Path(path),source)

    def test_orphan_result_denied(self):
        with self.temporary() as path:
            source,_=self.fixture(Path(path))
            (Path(path)/'attempts_0000000000000000/1.intent.json').unlink()
            with self.assertRaises(RuntimeError):t.prior_budget(Path(path),source)

    def test_original_stop_untouched(self):
        with self.temporary() as path:
            root=Path(path);source,_=self.fixture(root);r.save(root/'STOP.json',{'winerror':5})
            before=(root/'STOP.json').read_bytes();t.prior_block(root,source)
            self.assertEqual((root/'STOP.json').read_bytes(),before)

    def test_missing_verified_old_block_stops(self):
        with self.temporary() as path:
            source,block=self.fixture(Path(path))
            (block/'body.blob').unlink();(block/'marker.json').unlink();block.rmdir()
            with self.assertRaisesRegex(RuntimeError,'OLD_VERIFIED_BLOCK_ARTIFACT_MISSING'):
                t.prior_block(Path(path),source)


if __name__=='__main__':unittest.main()
