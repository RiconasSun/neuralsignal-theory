"""Registered layer proxies/descriptive association arithmetic, synthetic only."""
import unittest
from .anatomy import composition,association


class AnatomyTests(unittest.TestCase):
    def test_native_layers_keep_root_and_middle_in_denominator(self):
        c=composition(['MOp1','MOp2/3','MOp4','MOp5','MOp6a','MOp6b','MOp','UNKNOWN'])
        self.assertEqual(c['superficial_fraction'],.25);self.assertEqual(c['deep_fraction'],.375)
        self.assertEqual(c['middle_fraction'],.125);self.assertEqual(c['unspecified_fraction'],.25)
    def test_constant_layers_unavailable_without_invented_test(self):
        a=association([.2,.2,.2],[1.,2.,3.]);self.assertIsNone(a['Pearson_r'])
        self.assertEqual(a['status'],'UNAVAILABLE_CONSTANT_OR_INSUFFICIENT')
    def test_linear_association_is_descriptive_without_pvalue(self):
        a=association([0.,.5,1.],[1.,2.,3.]);self.assertAlmostEqual(a['Pearson_r'],1.)
        self.assertIsNone(a['p_value']);self.assertFalse(a['formal_hypothesis_test']);self.assertFalse(a['causal_interpretation'])


if __name__=='__main__':unittest.main()
