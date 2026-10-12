import unittest
from unittest.mock import patch
import register as r
import source_safe4


class DiagnosticTests(unittest.TestCase):
    def test_repeated_close_writes_once(self):
        item={'file_id':'fixture','content_range':'bytes 0-7/8','etag':'test-only'}
        source=source_safe4.Source(item)
        with patch.object(source_safe4.original,'protect'),patch.object(r,'save') as writer:
            source.close();source.close()
            self.assertEqual(writer.call_count,1)
        self.assertTrue(source.closed)
    def test_unique_ids_not_python_address(self):
        item={'file_id':'fixture','content_range':'bytes 0-7/8','etag':'test-only'}
        a,b=source_safe4.Source(item),source_safe4.Source(item)
        self.assertNotEqual(a.diagnostic_id,b.diagnostic_id)
        with patch.object(source_safe4.original,'protect'),patch.object(r,'save'):
            a.close();b.close()
    def test_transport_validation_unchanged(self):
        self.assertIs(source_safe4.Source.read,source_safe4.original.Source.read)
        self.assertIs(source_safe4.Source.readinto,source_safe4.original.Source.readinto)


if __name__=='__main__':unittest.main()
