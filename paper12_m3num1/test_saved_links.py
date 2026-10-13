import unittest
from saved_links import validate_links


class NativeLinks(unittest.TestCase):
    def test_child_hashes_and_exact_roster(self):
        links=[{'phase':'smoke' if i==0 else 'cohort_'+str(i),'sha256':{'gate':str(i)}} for i in range(13)]
        gate={'native_proofs':links};receipt={'native_proofs':links}
        self.assertEqual(validate_links(gate,receipt,lambda p:next(x['sha256'] for x in links if x['phase']==p)),13)
        with self.assertRaises(RuntimeError):validate_links(gate,receipt,lambda p:{'gate':'changed'})
        with self.assertRaises(RuntimeError):validate_links(gate,{'native_proofs':links[:12]},lambda p:{})
        with self.assertRaises(RuntimeError):validate_links({'native_proofs':links[:12]},{'native_proofs':links[:12]},lambda p:{})
