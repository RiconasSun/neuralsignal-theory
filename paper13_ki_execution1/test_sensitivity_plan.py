import unittest
from . import sensitivity_plan as s


class SensitivityTests(unittest.TestCase):
    def epochs(self):return [{'start':10.,'stop':13.,'ordinal':1,'partition':'C'},{'start':20.,'stop':23.,'ordinal':2,'partition':'D'}]

    def test_alignment_excludes_response_bin_and_keeps_parent(self):
        ep=self.epochs()
        for shift,bins in [(-.1,30),(.1,29)]:
            out=s.shifted(ep,shift,[0,30])
            self.assertTrue(all(z['retained'] for z in out))
            for z,e in zip(out,ep):
                self.assertEqual(z['observed_full_bins'],bins);self.assertLessEqual(z['export_stop'],e['stop']+1e-10)
                self.assertEqual(z['partition'],e['partition']);self.assertEqual(z['ordinal'],e['ordinal'])

    def test_alignment_support_saturation_touch_and_cross_partition(self):
        ep=self.epochs();out=s.shifted(ep,-.1,[10,30]);self.assertIn('support',out[0]['exclusion_reasons'])
        out=s.shifted(ep,.1,[0,30],lfp=[[14.1,15.]])
        self.assertIn('LFP_saturation',out[0]['exclusion_reasons'])
        ep[1].update(start=13.,stop=16.)
        out=s.shifted(ep,.1,[0,30]);self.assertIn('other_partition_original_touch',out[0]['exclusion_reasons'])

    def test_pairwise_shift_overlap_discards_both_no_substitution(self):
        ep=self.epochs();ep[1].update(start=12.,stop=15.)
        out=s.shifted(ep,.1,[0,30])
        self.assertTrue(all('shifted_overlap' in z['exclusion_reasons'] for z in out))
        self.assertEqual(len(out),2)

    def test_recent_event_half_open_boundaries_and_intervals(self):
        ep=self.epochs()
        self.assertEqual(s.recent_keep(ep,[13.,23.]),[True,True])
        self.assertEqual(s.recent_keep(ep,[5.]),[False,True])
        self.assertEqual(s.recent_keep(ep,[],[[4.,5.]]),[True,True])
        self.assertEqual(s.recent_keep(ep,[],[[4.,5.1]]),[False,True])
        with self.assertRaises(ValueError):s.recent_keep(ep,[float('nan')])

    def test_training_rate_ties_numeric_ID_and_strict_QC_deep_masks(self):
        units=[{'unit_id':j,'label':'PL5' if j<5 else 'PL2/3'} for j in range(8)]
        qc={str(j):{'rate_hz':1.,'refractory_fraction':.005 if j<6 else .006} for j in range(8)}
        out=s.unit_panels({'units':units,'unit_QC':qc})
        self.assertEqual(out['rate4'],[True]*4+[False]*4)
        self.assertEqual(sum(out['quality005']),6);self.assertEqual(sum(out['deep_PL5_PL6a']),5)
