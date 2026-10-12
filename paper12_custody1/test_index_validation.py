import unittest
import numpy as np
from index_validation import identity,offsets


class IndexTests(unittest.TestCase):
    def test_negative_before_cast_or_slice(self):
        with self.assertRaises(ValueError):offsets(np.array([-1,10]),2,10)
    def test_unsigned_overflow_before_cast(self):
        with self.assertRaises(ValueError):offsets(np.array([2**63,2**63+1],dtype=np.uint64),2,10)
    def test_identity_overflow(self):
        with self.assertRaises(ValueError):identity(np.array([2**64-1],dtype=np.uint64))
    def test_bounds(self):
        with self.assertRaises(ValueError):offsets(np.array([11,10]),2,10)
    def test_monotonic(self):
        with self.assertRaises(ValueError):offsets(np.array([9,8,10]),3,10)
    def test_final_length(self):
        with self.assertRaises(ValueError):offsets(np.array([2,9]),2,10)
    def test_cardinality(self):
        with self.assertRaises(ValueError):offsets(np.array([10]),2,10)
    def test_float_not_index(self):
        with self.assertRaises(ValueError):offsets(np.array([1.,10.]),2,10)
    def test_valid_signed_unsigned_equivalent(self):
        for kind in (np.int32,np.int64,np.uint32,np.uint64):
            self.assertEqual(offsets(np.array([0,5,10],dtype=kind),3,10).tolist(),[0,5,10])
    def test_empty(self):
        self.assertEqual(len(offsets(np.array([],dtype=np.int64),0,0)),0)
        with self.assertRaises(ValueError):offsets(np.array([],dtype=np.int64),0,1)


if __name__=='__main__':unittest.main()
