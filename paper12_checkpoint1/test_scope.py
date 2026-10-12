import unittest
import study as r
from custody_security import check_path


class ScopeTests(unittest.TestCase):
    def test_traversal_before_mutation(self):
        with self.assertRaisesRegex(RuntimeError,'PATH_TRAVERSAL'):
            check_path(r.HERE/'..'/'forbidden_fixture')
    def test_outside_scope(self):
        with self.assertRaisesRegex(RuntimeError,'OUTSIDE_SYNTHETIC'):
            check_path(r.ROOT/'paper12_custody1')


if __name__=='__main__':unittest.main()
