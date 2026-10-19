"""Saved-only archive approval and exact binary Git framing regressions."""
import unittest
from unittest.mock import patch
from . import archive_handoff as archive


class ArchiveTests(unittest.TestCase):
    def test_missing_review_denied_before_git(self):
        with patch.object(archive, 'load', side_effect=FileNotFoundError('Missing review')), \
             patch.object(archive, 'git', side_effect=AssertionError('No Git before review')):
            with self.assertRaises(FileNotFoundError):
                archive.plan()

    def test_nonaccepted_review_denied_before_files_or_git(self):
        with patch.object(archive, 'load', return_value={'decision': 'NOT_ACCEPTED'}), \
             patch.object(archive, 'git', side_effect=AssertionError('No Git before acceptance')):
            with self.assertRaises(AssertionError):
                archive.plan()

    def test_open_review_defect_denied(self):
        with patch.object(archive, 'load', return_value={
                'decision': 'ACCEPTED_R4_M2_SOURCE_HANDOFF', 'open_P0': 0, 'open_P1': 1}), \
             patch.object(archive, 'git', side_effect=AssertionError('No Git with open P1')):
            with self.assertRaises(AssertionError):
                archive.plan()

    def test_blob_framing_preserves_binary_and_denies_extra_or_missing_bytes(self):
        bodies = [b'embedded\x00newline\n\xff', b'']
        raw = b''.join(b'a' * 40 + b' blob ' + str(len(body)).encode() + b'\n' + body + b'\n' for body in bodies)
        with patch.object(archive.subprocess, 'check_output', return_value=raw):
            result = archive.batch('origin/test', ['one path', 'two'])
        self.assertEqual([body for _, body in result], bodies)
        for corrupt in [raw + b'extra', raw[:-1], b'missing path\n']:
            with patch.object(archive.subprocess, 'check_output', return_value=corrupt):
                with self.assertRaises(AssertionError):
                    archive.batch('origin/test', ['one path', 'two'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
