"""Synthetic rejection regressions; no model, neural arrays or actual gate writes."""
import copy
import importlib
import unittest

guard = importlib.import_module(__package__+'.seal_sensitivity_gate')

class ReviewGuard(unittest.TestCase):
    def test_only_current_explicit_acceptance_passes(self):
        expected = {'plan.json':'a'*64, 'source.py':'b'*64}
        accepted = dict(decision='ACCEPTED_SENSITIVITY_ADMISSION_GATE',open_P0=0,open_P1=0,
            approved_for_fixed_A_sensitivity_refits=True,hashes=expected,review_sha256='c'*64)
        guard.validate_review(accepted,expected,'c'*64)
        variants = [({},'missing receipt fields'),
            ({'decision':'REJECTED'},'failed review'),({'open_P0':1},'unresolved P0'),
            ({'open_P1':1},'unresolved P1'),({'open_P1':False},'noninteger count'),
            ({'approved_for_fixed_A_sensitivity_refits':False},'no approval'),
            ({'approved_for_fixed_A_sensitivity_refits':1},'nonboolean approval'),
            ({'hashes':{'plan.json':'a'*64}},'incomplete review'),
            ({'hashes':{'plan.json':'x'*64,'source.py':'b'*64}},'changed plan'),
            ({'hashes':dict(expected,extra='d'*64)},'different payload'),
            ({'review_sha256':'d'*64},'different report')]
        for changed,label in variants:
            with self.subTest(label=label):
                candidate = {} if not changed else dict(copy.deepcopy(accepted),**changed)
                with self.assertRaises((AssertionError,KeyError)):
                    guard.validate_review(candidate,expected,'c'*64)

if __name__=='__main__':
    unittest.main()
