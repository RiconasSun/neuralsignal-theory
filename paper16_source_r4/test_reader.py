"""All13 frozen reader oracles plus new no-reread prefix cases on owned HDF5."""
import copy
import unittest
from unittest.mock import patch
import h5py
import numpy as np
from paper16_dev_r3 import test_neural as fixture_module
from .core import P,SourceStop
from .neural_reader import read_a_source


class NativeReaderTests(fixture_module.NativeReaderTests):
    def setUp(self):
        self.patchP=patch.object(fixture_module,'P',P);self.patchReader=patch.object(fixture_module,'read_a_source',read_a_source)
        self.patchP.start();self.patchReader.start();super().setUp()
    def tearDown(self):
        try:super().tearDown()
        finally:self.patchReader.stop();self.patchP.stop()


class ResumeReaderTests(unittest.TestCase):
    def setUp(self):
        self.patch=patch.object(fixture_module,'P',P);self.patch.start()
        self.f=fixture_module.NativeReaderTests();self.f.setUp()
        self.prior=self.f.run_reader()['units'][:2]
    def tearDown(self):self.f.tearDown();self.patch.stop()
    def run_resume(self,prior):
        self.captures=[];self.reads=[]
        def persist(uid,arrays,record):self.captures.append(uid);return {'synthetic':True}
        with h5py.File(self.f.path,'r') as f:
            return read_a_source(f,self.f.item,self.f.reg,self.f.header,self.f.flashes,self.f.certs,persist,[],self.reads,reused_records=prior)
    def test_exact_saved_prefix_is_reused_without_old_spike_payload_reads(self):
        result=self.run_resume(self.prior)
        self.assertEqual(len(result['units']),8);self.assertEqual(self.captures,list(range(103,109)))
        slices=[r['selector'] for r in self.reads if r['path']=='/units/spike_times']
        self.assertEqual(len(slices),6);self.assertEqual(slices[0],str(slice(601,901)))
        self.assertEqual(result['units'][:2],self.prior)
    def test_noncontiguous_or_altered_saved_prefix_rejected(self):
        bad=copy.deepcopy(self.prior);bad[1]['unit_id']=104
        with self.assertRaises(SourceStop):self.run_resume(bad)
        self.assertEqual(self.captures,[])
    def test_new_candidate_nonfinite_outside_A_stops_and_keeps_old_prefix(self):
        before=copy.deepcopy(self.prior)
        with h5py.File(self.f.path,'r+') as f:f['/units/spike_times'][781]=np.nan
        with self.assertRaises(SourceStop):self.run_resume(self.prior)
        self.assertEqual(self.prior,before);self.assertEqual(self.captures,[])


if __name__=='__main__':unittest.main(verbosity=2)
