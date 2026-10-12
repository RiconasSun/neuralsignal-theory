import os
import unittest
import numpy as np
from cryptography.exceptions import InvalidTag
import cipher_core as crypt
from custody_core import count_unit,public_train_export,guarded_publish


def trial(start,partition,admitted=True):
    return {'start':start,'analysis_stop':start+2.,'nominal_bin_edges':[start+i/10 for i in range(21)],
            'partition':partition,'metadata_admitted':admitted}


class CustodyTests(unittest.TestCase):
    def test_half_open_membership(self):
        y,q=count_unit(np.array([0.,.1,1.9,2.,3.]),[trial(0.,'train')],'train')
        self.assertEqual(int(y.sum()),3)
        self.assertEqual(int(y[0,0]),1)
        self.assertEqual(int(y[0,1]),1)
        self.assertEqual(q['QC_trials'],1)

    def test_adjacent_trials_boundary_not_double_count(self):
        y,q=count_unit(np.array([0.,2.,4.]),[trial(0.,'train'),trial(2.,'locked_evaluation')],'train')
        self.assertEqual(y.sum(axis=1).tolist(),[1,1])

    def test_mask_not_replenished(self):
        y,q=count_unit(np.array([0.,3.]),[trial(0.,'train',False),trial(3.,'train')],'train')
        self.assertEqual(int(y[0].sum()),0)
        self.assertEqual(q['QC_trials'],1)

    def test_final_canary_cannot_change_training_or_qc(self):
        ts=[trial(0.,'train'),trial(3.,'locked_evaluation')]
        a,qa=count_unit(np.array([.1,.4,3.1]),ts,'train')
        b,qb=count_unit(np.array([.1,.4,3.1,3.2,3.3,3.4,3.5]),ts,'train')
        self.assertEqual(qa,qb)
        self.assertEqual(public_train_export(a,ts).tobytes(),public_train_export(b,ts).tobytes())
        self.assertNotEqual(a[1].tobytes(),b[1].tobytes())

    def test_no_cross_trial_ISI(self):
        y,q=count_unit(np.array([1.9999,2.]),[trial(0.,'train'),trial(2.,'train')],'train')
        self.assertEqual(q['within_trial_ISI_pairs'],0)
        self.assertEqual(q['ISI_under_1ms_fraction'],0)

    def test_duplicate_permitted_rejected_by_qc(self):
        y,q=count_unit(np.array([.1,.1]),[trial(0.,'train')],'train')
        self.assertFalse(q['eligible'])
        self.assertTrue(q['invalid_permitted_timestamps'])

    def test_sorted_source_required(self):
        with self.assertRaises(ValueError):
            count_unit(np.array([.4,.1]),[trial(0.,'train')],'train')

    def test_authentication_and_equal_length(self):
        key=os.urandom(32)
        context={'study':'synthetic','animal':'fixture','compartment':'D','lock':'test-only'}
        a=crypt.seal(key,np.zeros(40,dtype='<i4').tobytes(),context)
        b=crypt.seal(key,np.ones(40,dtype='<i4').tobytes(),context)
        self.assertEqual(len(a),len(b))
        self.assertEqual(crypt.unseal(key,a,context),np.zeros(40,dtype='<i4').tobytes())
        with self.assertRaises(InvalidTag):
            crypt.unseal(os.urandom(32),a,context)
        with self.assertRaises(InvalidTag):
            crypt.unseal(key,a,{**context,'compartment':'A'})
        with self.assertRaises(InvalidTag):
            crypt.unseal(key,a[:-1]+bytes([a[-1]^1]),context)

    def test_bad_key_and_frame(self):
        with self.assertRaises(ValueError):
            crypt.seal(b'short',b'fixture',{'test':True})
        with self.assertRaises(ValueError):
            crypt.unseal(os.urandom(32),b'wrong',{'test':True})

    def test_failure_aborts_publication(self):
        with self.assertRaises(PermissionError):
            guarded_publish(False,b'never published')


if __name__=='__main__':
    unittest.main()
