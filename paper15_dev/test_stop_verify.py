import unittest
from .stop_verify import inventory_check,safe_relative

class StopInventoryTest(unittest.TestCase):
    def test_recompute_unattempted(self):
        self.assertEqual(inventory_check(['a','b'],{'a','b'},{'a','b','c'}),1)

    def test_duplicate_seal_denied(self):
        with self.assertRaises(AssertionError):inventory_check(['a','a'],{'a','b'},{'a','b','c'})

    def test_unsealed_actual_file_denied(self):
        with self.assertRaises(AssertionError):inventory_check(['a'],{'a','b'},{'a','b','c'})

    def test_unknown_configuration_denied(self):
        with self.assertRaises(AssertionError):inventory_check(['a','x'],{'a','x'},{'a','b','c'})

    def test_manifest_path_escape_denied(self):
        for path in ('../x','/x','C:/x','a\\b','a/../b','./a'):
            with self.subTest(path=path),self.assertRaises(AssertionError):safe_relative(path)
        self.assertEqual(safe_relative('fits/mouse/fit.json'),'fits/mouse/fit.json')

if __name__=='__main__':unittest.main()
