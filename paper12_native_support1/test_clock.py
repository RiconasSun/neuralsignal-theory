import io
import tempfile
import unittest
from pathlib import Path
import numpy as np
from clock import affine,official,unwrap,probe_segments
from digital import digital_object,read_edges
from register import HERE

class ClockTests(unittest.TestCase):
    def test_official_fourbit_fixture(self):
        starts,codes=official().extract_barcodes_from_times(np.array([11,14,30,32,34]),np.array([13,15,31,33,35]),10,1,7,4)
        np.testing.assert_equal(starts,[30]);np.testing.assert_equal(codes,[5])
    def test_affine_independent_algebra(self):
        for slope in (.99999,1,1.00001):
            for offset in (-200,0,500):
                x=np.arange(10,dtype=float)*30+300
                r=affine(slope*x+offset,np.arange(10),x,np.arange(10))
                self.assertTrue(r['pass']);self.assertAlmostEqual(r['slope'],slope,places=12)
                self.assertAlmostEqual(r['offset_seconds'],offset,places=10)
    def test_all_codes_not_favorable_pruning(self):
        x=np.arange(10,dtype=float)*30;y=x.copy();y[5]+=.02
        r=affine(y,np.arange(10),x,np.arange(10))
        self.assertFalse(r['pass']);self.assertEqual(r['matched_codes'],10)
    def test_ambiguous_codes(self):
        r=affine([0,30,60],[1,1,2],[0,30,60],[1,2,3])
        self.assertFalse(r['pass']);self.assertEqual(r['master_duplicate_codes'],1)
    def test_counter_wrap(self):
        x,n=unwrap([2**32-2,2**32-1,0,1])
        self.assertEqual(n,1);np.testing.assert_equal(np.diff(x),[1,1,1])
    def test_no_behavior_or_neural_file(self):
        for name in ('spike_band.dat','lfp_band.dat','spike_times.npy','wheel.npy'):
            self.assertFalse(digital_object('visual-coding-neuropixels/raw-data/1/2/'+name))
    def test_undefined_edge_states(self):
        with self.assertRaises(RuntimeError):probe_segments([0,1,2],[1,99,-1])
    def test_nonbarcode_identifiers_not_interpreted(self):
        _,_,_,d=probe_segments([0,1,2,3],[0,2,-2,0])
        self.assertEqual(d['nonbarcode_line_identifiers_not_interpreted'],2)
    def test_native_npy_public_header(self):
        (HERE/'replay').mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=HERE/'replay') as d:
            p=Path(d)/'edge.npy';np.save(p,np.arange(3,dtype=np.int64))
            np.testing.assert_equal(read_edges(p),[0,1,2])
    def test_object_array_denied(self):
        (HERE/'replay').mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=HERE/'replay') as d:
            p=Path(d)/'edge.npy';np.save(p,np.array([{}],dtype=object))
            with self.assertRaises(RuntimeError):read_edges(p)

if __name__=='__main__':unittest.main(verbosity=2)
