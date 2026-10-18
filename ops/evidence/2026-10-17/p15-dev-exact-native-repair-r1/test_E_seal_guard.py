"""Synthetic review-rejection probes, with no E data or batch claim."""
import importlib
import unittest

guard = importlib.import_module(__package__+'.seal_E_gate')

class EReviewGuard(unittest.TestCase):
    def test_exact_accepted_payload_only(self):
        hashes={'plan':'a'*64,'state':'b'*64}
        approved=dict(decision='ACCEPTED_E_BATCH_GATE',open_P0=0,open_P1=0,
            approved_for_one_frozen_E_batch=True,hashes=hashes,review_sha256='c'*64)
        guard.validate_review(approved,hashes,'c'*64)
        for changed in ({'decision':'REJECTED'},{'open_P0':1},{'open_P1':1},{'open_P0':False},
            {'approved_for_one_frozen_E_batch':False},{'approved_for_one_frozen_E_batch':1},
            {'hashes':{}},{'hashes':dict(hashes,state='d'*64)},{'review_sha256':'e'*64}):
            with self.subTest(changed=changed):
                with self.assertRaises(AssertionError):
                    guard.validate_review(dict(approved,**changed),hashes,'c'*64)
        with self.assertRaises(KeyError):
            guard.validate_review({},hashes,'c'*64)

if __name__=='__main__':
    unittest.main()
