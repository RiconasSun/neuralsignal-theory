import unittest
import numpy as np
from mouse_statistics import holm,paired,aggregate
class StatisticsTests(unittest.TestCase):
    def test_holm(self):np.testing.assert_allclose(holm([.04,.001,.02,.2]),[.08,.004,.06,.2])
    def test_equal_mouse(self):
        r=paired(np.ones(13));self.assertEqual(r['mean_CA1_minus_DG'],1);self.assertEqual(r['paired_signflip_p'],2/8192);self.assertEqual(r['CI95'],[1,1])
    def test_zero_and_seed(self):
        self.assertEqual(paired(np.zeros(13))['paired_signflip_p'],1);self.assertEqual(paired(np.arange(13))['CI95'],paired(np.arange(13))['CI95'])
    def test_minimum(self):
        with self.assertRaises(ValueError):paired(np.ones(7))
if __name__=='__main__':unittest.main()
