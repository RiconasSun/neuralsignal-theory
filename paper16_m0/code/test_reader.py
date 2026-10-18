import unittest
from unittest.mock import patch
import numpy as np
from .core import count_bins
from .pilot_reader import fast_counts,invalid_for_probe,validate_access

class ReaderTests(unittest.TestCase):
    def test_vector_counts_equal_checked_oracle(self):
        for spikes in [[],[1.,1.,2.],[0.,.5,1.,2.,3.]]:
            for bad in [[],[[1.,2.]]]:
                self.assertEqual(fast_counts(np.asarray(spikes),np.asarray([0.,1.,2.,3.]),[[0.,2.]],bad),count_bins(spikes,[0.,1.,2.,3.],[[0.,2.]],bad))
    def test_invalid_scope_is_probe_specific_and_unknown_denied(self):
        probes={1:'probeA',2:'probeB'}
        rows=[{'start_time':0,'stop_time':1,'tags':['EcephysProbe','probeB']}]
        self.assertEqual(invalid_for_probe(rows,1,'probeA',probes),[])
        self.assertEqual(invalid_for_probe(rows,2,'probeB',probes),[[0.,1.]])
        for tags in [[],['unknown'],['EcephysProbe'],['EcephysProbe','probeZ'],['Stimulus','unknown']]:
            with self.assertRaises(ValueError): invalid_for_probe([{'start_time':0,'stop_time':1,'tags':tags}],1,'probeA',probes)
        self.assertEqual(invalid_for_probe([{'start_time':0,'stop_time':1,'tags':['Stimulus']}],1,'probeA',probes),[[0.,1.]])
    def test_unregistered_final_not_opened(self):
        with patch('paper16_m0.code.pilot_reader.approved_pilots',return_value=[{'session_id':1}]):
            self.assertEqual(validate_access(1),{'session_id':1})
            with self.assertRaises(ValueError): validate_access(2)

if __name__=='__main__':unittest.main()
