import uuid
import zipfile
import unittest
from . import restore_saved_states as r


class RestoreTests(unittest.TestCase):
    def fixture(self):
        root=r.P/'work'/('restore_tests_'+uuid.uuid4().hex);root.mkdir(parents=True)
        name='paper13_ki_execution1/work/training_states/synthetic.npz';raw=b'synthetic saved state'
        archive=root/'archive.zip'
        with zipfile.ZipFile(archive,'x') as z:z.writestr(name,raw)
        manifest={'archive_file':'archive.zip','archive_sha256':r.sha(archive.read_bytes()),
            'entries':[{'path':name,'mouse_id':'synthetic','partition':'C','sha256':r.sha(raw),'bytes':len(raw)}]}
        return root,manifest

    def test_restore_and_repeat_preserve_identical_original(self):
        root,manifest=self.fixture();self.assertEqual(r.restore(root,manifest)['restored_missing_original_files'],1)
        self.assertEqual(r.restore(root,manifest)['restored_missing_original_files'],0)

    def test_existing_different_state_is_never_overwritten(self):
        root,manifest=self.fixture();path=root/manifest['entries'][0]['path'];path.parent.mkdir(parents=True);path.write_bytes(b'preserve')
        with self.assertRaises(ValueError):r.restore(root,manifest)
        self.assertEqual(path.read_bytes(),b'preserve')

    def test_corrupt_archive_or_payload_fail_before_write(self):
        root,manifest=self.fixture();manifest['entries'][0]['sha256']='wrong'
        with self.assertRaises(ValueError):r.restore(root,manifest)
        self.assertFalse((root/manifest['entries'][0]['path']).exists())
        manifest['archive_sha256']='wrong'
        with self.assertRaises(ValueError):r.restore(root,manifest)

    def test_D_partition_or_traversal_denied(self):
        root,manifest=self.fixture();manifest['entries'][0]['partition']='D'
        with self.assertRaises(PermissionError):r.restore(root,manifest)
        manifest['entries'][0]['partition']='C';manifest['entries'][0]['mouse_id']='../../escape'
        with self.assertRaises(PermissionError):r.restore(root,manifest)
