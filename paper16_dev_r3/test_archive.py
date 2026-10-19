"""Synthetic Git receipt framing and independent approval fail-closed checks."""
import unittest
from unittest.mock import patch
from . import archive_handoff as archive


class ArchiveGuardTests(unittest.TestCase):
    def test_missing_final_independent_approval_denied_before_git_or_plan(self):
        with patch.object(archive, 'read', side_effect=FileNotFoundError('No independent approval')), \
             patch.object(archive, 'git', side_effect=AssertionError('No Git action before review')):
            with self.assertRaises(FileNotFoundError): archive.plan()

    def test_git_blob_readback_preserves_embedded_NUL_newline_and_binary_bytes(self):
        bodies = [b'first\x00payload\n\xff', b'']
        raw = b''.join(b'a'*40+b' blob '+str(len(body)).encode()+b'\n'+body+b'\n' for body in bodies)
        with patch.object(archive.subprocess, 'check_output', return_value=raw):
            result = archive.batch('origin/test', ['one', 'two'])
        self.assertEqual([v for _, v in result], bodies)
        with patch.object(archive.subprocess, 'check_output', return_value=raw+b'extra'):
            with self.assertRaises(AssertionError): archive.batch('origin/test', ['one', 'two'])


if __name__ == '__main__': unittest.main(verbosity=2)
