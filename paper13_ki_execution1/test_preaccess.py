"""Synthetic source/QC/partition oracles; no real neural arrays."""
import copy
import io
import json
from pathlib import Path
import unittest
from unittest.mock import patch
import h5py
import numpy as np
from .source import ALLOCATION,P,ROOT,unit_window_export,partition_windows,cut_windows,node,SourceReader
from .qc import screen,counts_for

class AccessTests(unittest.TestCase):
    def record(self):return {'role':'final','epochs':[{'start':10+5*i,'stop':13+5*i,'partition':'C' if i<60 else 'D'} for i in range(120)]}
    def file(self,values):
        b=io.BytesIO()
        with h5py.File(b,'w') as h:
            h['units/spike_times']=values;h['units/spike_times_index']=[len(values)]
        return h5py.File(io.BytesIO(b.getvalue()),'r')
    def test_final_D_export_denied_before_file_access(self):
        with self.assertRaises(PermissionError):unit_window_export(None,0,self.record(),'D')
    def test_development_B_E_QC_export_denied(self):
        r=self.record();r['role']='development'
        for p in ['B','E','C','D']:
            with self.assertRaises(PermissionError):partition_windows(r,p)
    def test_C_export_invariant_to_D_canary(self):
        r=self.record();a=np.array([10.1,11.0,310.1,311.2])
        with self.file(a) as h:x=unit_window_export(h,0,r,'C')
        with self.file(np.array([10.1,11.0,310.2,310.3,312.4,315.5])) as h:y=unit_window_export(h,0,r,'C')
        for first,second in zip(x,y):np.testing.assert_array_equal(first,second)
    def test_QC_invariant_to_excluded_windows(self):
        r=self.record();a=np.array([e['start']+.2 for e in r['epochs'] if e['partition']=='C'])
        x=cut_windows(a,r['epochs'][:60]);y=cut_windows(np.r_[a,[310.001,310.002]*100],r['epochs'][:60])
        self.assertEqual(screen(x),screen(y))
    def test_cut_half_open_identity(self):
        x=cut_windows(np.array([9,10,12.999,13,15]),[{'start':10,'stop':13}])[0]
        np.testing.assert_allclose(x,[0,2.999])
    def test_whole25_denominator_and19role_identity(self):
        original=json.loads((ROOT/'paper13_ki_pl_contract1/PROPOSED_ALLOCATION.json').read_text())
        self.assertEqual({x['mouse_id'] for x in ALLOCATION if x['role']=='development'},set(original['development']))
        self.assertEqual({x['mouse_id'] for x in ALLOCATION if x['role']=='final'},set(original['final']))
        for r in ALLOCATION:
            self.assertEqual(len(r['epochs']),120);self.assertEqual(len(partition_windows(r,r['QC_partition'])),60)
            self.assertEqual(r['PL_units_numeric_order'],sorted(r['PL_units_numeric_order'],key=lambda x:x['unit_id']))
            self.assertTrue(all(e['stop']-e['start']==3 for e in r['epochs']))
    def test_epochs_nonoverlap_and_no_animal_crossing(self):
        self.assertEqual(len({r['mouse_id'] for r in ALLOCATION}),19)
        for r in ALLOCATION:
            self.assertTrue(all(a['stop']<=b['start'] for a,b in zip(r['epochs'],r['epochs'][1:])))
    def test_no_ISI_across_gaps(self):
        ts=[np.array([.001]) for _ in range(60)];q=screen(ts)
        self.assertEqual(q['within_epoch_ISIs'],0);self.assertFalse(q['pass'])
    def test_QC_exact_good_reference(self):
        q=screen([np.array([.2,1.2,2.2]) for _ in range(60)])
        self.assertTrue(q['pass']);self.assertEqual(q['training_spikes'],180);self.assertEqual(q['rate_hz'],1)
        self.assertEqual(q['within_epoch_ISIs'],120)
    def test_QC_empty_and_occupancy(self):
        self.assertFalse(screen([np.array([]) for _ in range(60)])['pass'])
        self.assertFalse(screen([np.arange(100)*.01]+[np.array([]) for _ in range(59)])['pass'])
    def test_QC_duplicates_unsorted_nonfinite(self):
        for times in [[.1,.1],[.2,.1],[float('nan')],[3],[-.1]]:
            self.assertFalse(screen([np.array(times)]+[np.array([]) for _ in range(59)])['pass'])
    def test_QC_rate_and_refractory_failure(self):
        self.assertFalse(screen([np.array([.1,.1001,1]) for _ in range(60)])['pass'])
        self.assertFalse(screen([np.arange(500)/200 for _ in range(60)])['pass'])
    def test_QC_exposure_fixed180(self):
        with self.assertRaises(ValueError):screen([[]]*59)
        self.assertEqual(screen([[]]*60)['exposure_seconds'],180)
    def test_counts_warmup_score_identity_and_zeros(self):
        c=counts_for([np.array([0,.1,.5,2.999]) for _ in range(60)])
        self.assertEqual(c.shape,(60,30));self.assertEqual(c[:,5:].sum(),120)
        self.assertEqual(c[:,5:].size,1500)
    def test_no_soft_external_dataset(self):
        b=io.BytesIO()
        with h5py.File(b,'w') as h:h['units/spike_times']=h5py.ExternalLink('forbidden','D')
        with h5py.File(io.BytesIO(b.getvalue()),'r') as h:
            with self.assertRaises(ValueError):node(h,'/units/spike_times')
    def test_corrupt_ragged_index_fails(self):
        b=io.BytesIO()
        with h5py.File(b,'w') as h:h['units/spike_times']=[1];h['units/spike_times_index']=[9]
        with h5py.File(io.BytesIO(b.getvalue()),'r') as h:
            with self.assertRaises(ValueError):unit_window_export(h,0,self.record(),'C')
    def test_nonfinite_not_silently_lost_before_QC(self):
        r=self.record()
        values=[e['start']+t for e in r['epochs'][:60] for t in [.2,1.2,2.2]]+[float('nan')]
        with self.file(values) as h:
            with self.assertRaisesRegex(ValueError,'SOURCE_INTEGRITY_STOP'):unit_window_export(h,0,r,'C')
    def test_infinite_unassignable_source_halts(self):
        for x in [float('nan'),float('inf'),float('-inf')]:
            with self.assertRaisesRegex(ValueError,'SOURCE_INTEGRITY_STOP'):cut_windows(np.array([10.1,x]),self.record()['epochs'][:60])
    def test_source_constructor_requires_owner_decision_before_network(self):
        import uuid
        empty=P/'work'/('missing_approval_'+uuid.uuid4().hex);empty.mkdir(parents=True)
        with patch('paper13_ki_execution1.source.P',empty),patch('paper13_ki_execution1.source.requests.Session',side_effect=AssertionError('Network session before approval')):
            with self.assertRaisesRegex(PermissionError,'Owner raw-source decision'):SourceReader(ALLOCATION[0])
    def test_original_failed_preaccess_snapshot_preserved(self):
        from zipfile import ZipFile
        import hashlib
        archive=ROOT/'ops/evidence/2026-10-16/p13-ki-pl-science-first-execution/preaccess_r1_package.zip'
        with ZipFile(archive) as z:
            snap=json.loads(z.read('PREACCESS_FREEZE.json'))
            self.assertEqual(len(snap['hashes']),10)
            for name,h in snap['hashes'].items():self.assertEqual(hashlib.sha256(z.read(Path(name).name)).hexdigest(),h)

if __name__=='__main__':unittest.main(verbosity=2)
