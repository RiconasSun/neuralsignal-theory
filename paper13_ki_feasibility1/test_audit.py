import unittest
import json
from pathlib import Path
from audit import identity,region,interval_valid,overlapping,basic_epochs,record_table


class AuditTests(unittest.TestCase):
    def test_negative_stratum_not_exported_as_release_impossibility(self):
        result=json.loads((Path(__file__).resolve().parent/'results/review1/audit.json').read_text())
        candidate=result['candidates']['001260']
        self.assertEqual(candidate['primary_task_stratum'],'Passive')
        self.assertEqual(candidate['primary_task_stratum_verdict'],'DATA_INSUFFICIENT')
        self.assertEqual(candidate['scientific_verdict'],'INCONCLUSIVE_METADATA')
        self.assertIn('not the whole release',candidate['upper_bound_scope'])
    def test_same_mouse_two_export_suffixes(self):
        a=identity({'/general/subject/subject_id':'518804_1','/general/session_id':'518804_20220228-probe0'})
        b=identity({'/general/subject/subject_id':'518804_2','/general/session_id':'518804_20220301-probe0'})
        self.assertEqual(a['mouse_id'],b['mouse_id']);self.assertNotEqual(a['session_id'],b['session_id'])

    def test_same_session_two_probes(self):
        a=identity({'/general/subject/subject_id':'PL028','/general/session_id':'PL028_20190517-probe0'})
        b=identity({'/general/subject/subject_id':'PL028','/general/session_id':'PL028_20190517-probe1'})
        self.assertEqual(a['mouse_id'],b['mouse_id']);self.assertEqual(a['session_id'],b['session_id'])

    def test_identity_conflict_refused(self):
        with self.assertRaises(ValueError):identity({'/general/subject/subject_id':'animalA','/general/session_id':'animalB_20200101-probe0'})

    def test_no_region_pooling(self):
        for label,expected in [('PL5','PL'),('ILA6','ILA'),('ACAd2/3','ACAd'),('ACAv','ACAv'),('ORBm','ORBm')]:self.assertEqual(region(label),expected)
        for label in ['ACA','ORB','mPFC','PLandILA','CA1']:self.assertIsNone(region(label))

    def test_half_open_intervals(self):
        self.assertFalse(overlapping([0,3],[3,6]));self.assertTrue(overlapping([0,3],[2,5]))
        self.assertFalse(interval_valid([0,float('nan')]));self.assertFalse(interval_valid([2,1]))

    def example(self):
        values={'/stimulus/presentation/passive_10kHz/timestamps':[5.,10.,15.],
                '/stimulus/presentation/passive_bluenoise/timestamps':[8.],
                '/processing/ecephys/LFP/ElectricalSeries/starting_time':0.,
                '/analysis/spike saturation start/timestamps':[],
                '/analysis/spike saturation stop/timestamps':[]}
        structure=[{'path':'/processing/ecephys/LFP/ElectricalSeries/data','shape':[20000,2]},
                   {'path':'/processing/ecephys/LFP/ElectricalSeries/starting_time','attrs':{'rate':1000}}]
        return values,structure

    def test_only_genuine_pure_tones(self):
        result=basic_epochs(*self.example())
        self.assertEqual(result['basic_epochs'],[[2.,5.],[7.,10.],[12.,15.]])
        self.assertFalse(result['sleep_lick_exclusions_complete'])

    def test_saturation_excluded_with_fixed_padding(self):
        v,s=self.example();v['/analysis/spike saturation start/timestamps']=[8.];v['/analysis/spike saturation stop/timestamps']=[8.5]
        self.assertEqual(basic_epochs(v,s)['basic_epochs'],[[2.,5.],[12.,15.]])

    def test_missing_mask_not_empty_mask(self):
        v,s=self.example();v.pop('/analysis/spike saturation start/timestamps')
        self.assertFalse(basic_epochs(v,s)['saturation_complete'])

    def test_no_clock_not_valid_epoch(self):
        v,_=self.example();self.assertEqual(basic_epochs(v,[])['basic_epochs'],[])

    def test_overlap_not_independent_epoch(self):
        v,s=self.example();v['/stimulus/presentation/passive_10kHz/timestamps']=[5.,6.]
        self.assertEqual(basic_epochs(v,s)['basic_epochs'],[])

    def test_source_table_corroborates_alias_dates(self):
        rows=record_table()
        self.assertIn('518804_20220228-probe0',rows)
        self.assertIn('518804_20220301-probe0',rows)


if __name__=='__main__':unittest.main()
