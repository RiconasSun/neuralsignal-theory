"""Synthetic and saved-metadata oracles; no real neural measurements."""
import copy
import io
import json
import math
from pathlib import Path
import unittest
from unittest.mock import patch
import h5py
import requests
from audit import P,M,OLD,validate_intervals,saturation,candidate_windows,intersects,future_qc_contract
from manual_intervals import decode,ArchiveReader,SIZE
from proposed_qc import screen,projected_gradient
from sources import Transport
from proposed_operators import scalar_leaky_states,restricted_linear,state_prior,sign_flip_p,censor_recent_epoch,shifted_score_bins,broad_baseline_direction,temporal_direction,deep_laminar_mask

class ContractTests(unittest.TestCase):
    def test_full_denominator_and_bounds(self):
        a=json.loads((P/'results/initial/audit.json').read_text())
        self.assertEqual(len(a['records']),25);self.assertEqual(len({r['mouse_id'] for r in a['records']}),25)
        self.assertEqual(a['bounds'],{'historical_raw_PL':20,'historical_basic120':20,'historical_active120':15,'refined_A120':19,'refined_B120':15,'actual_QC_eligible_mice':0})
        self.assertTrue(all(not r['quality_admitted'] and not r['awake_certified'] and not r['eligible_mouse_certified'] for r in a['records']))
    def test_known_independent_per_mouse_oracle(self):
        expected={'128514':200,'128515':200,'128516':176,'147463':55,'147465':197,'152414':199,'152417':200,'152419':178,'156130':190,'156131':196,'216300':200,'216301':200,'225757':198,'225758':200,'225759':200,'258412':200,'258414':200,'258416':201,'258419':192,'259112':250,'268947':198,'268951':623,'273853':520,'273855':200,'273858':570}
        a=json.loads((P/'results/initial/audit.json').read_text())
        self.assertEqual({r['mouse_id']:r['proposed_A_after_known_masks'] for r in a['records']},expected)
        self.assertEqual(sum(r['historical_basic'] for r in a['records']),6155)
    def test_quality_remains_unknown(self):
        q=json.loads((P/'results/initial/audit.json').read_text())['quality_metadata']
        self.assertEqual(q['units'],9408);self.assertEqual(q['col0_max'],55383)
        self.assertEqual(q['exact_formula_units_and_exporter'],'UNRESOLVED');self.assertTrue(q['no_ratio_inferred'])
        self.assertFalse(future_qc_contract()['historical_columns_used_for_admission'])
    def test_nan_pair_is_provider_empty(self):
        v={f'/analysis/spike saturation {s}/timestamps':[None] for s in ['start','stop']}
        self.assertEqual(saturation(v,'spike'),([], 'provider_single_nan_sentinel'))
    def test_missing_does_not_become_empty(self):
        with self.assertRaises(ValueError):saturation({},'spike')
    def test_mixed_nan_fails(self):
        v={'/analysis/spike saturation start/timestamps':[None],'/analysis/spike saturation stop/timestamps':[1]}
        with self.assertRaises(ValueError):saturation(v,'spike')
        v={f'/analysis/spike saturation {s}/timestamps':[None,None] for s in ['start','stop']}
        with self.assertRaises(ValueError):saturation(v,'spike')
    def test_saturation_length_and_reversal(self):
        for a,b in [([1,2],[3]),([4],[3])]:
            with self.assertRaises(ValueError):saturation({'/analysis/spike saturation start/timestamps':a,'/analysis/spike saturation stop/timestamps':b},'spike')
    def test_interval_finite_order_shape(self):
        for x in [[[2,1]],[[0,0]],[[float('nan'),3]],[[0,1,2]],[[False,3]]]:
            with self.assertRaises(ValueError):validate_intervals(x)
        self.assertEqual(validate_intervals([[0,3]]),[[0,3]])
    def test_half_open_and_conservative_touch(self):
        self.assertFalse(intersects([0,3],[3,4]));self.assertTrue(intersects([0,3],[3,4],True))
    def fixture(self):
        v={'/stimulus/presentation/AudStim_10kHz/timestamps':[3,5,10],'/processing/ecephys/LFP/ElectricalSeries/starting_time':0}
        s=[{'path':'/processing/ecephys/LFP/ElectricalSeries/starting_time','attrs':{'rate':10}},{'path':'/processing/ecephys/LFP/ElectricalSeries/data','shape':[100]}]
        return v,s
    def test_overlap_removes_both_not_greedy_selection(self):
        v,s=self.fixture();e,ex,support,n=candidate_windows(v,s)
        self.assertEqual(e,[[7,10]]);self.assertEqual(ex,{'overlap':2});self.assertEqual(support,[0,10])
    def test_noise_not_puretone(self):
        v,s=self.fixture();v['/stimulus/presentation/passive_bluenoise/timestamps']=[8]
        self.assertEqual(candidate_windows(v,s)[3],3)
    def test_outside_support(self):
        v,s=self.fixture();v['/stimulus/presentation/AudStim_10kHz/timestamps']=[2,11]
        self.assertEqual(candidate_windows(v,s)[1],{'support':2})
    def test_invalid_clock_fails(self):
        v,s=self.fixture();s[0]['attrs']['rate']=float('nan')
        with self.assertRaises(ValueError):candidate_windows(v,s)
    def test_manual_saved_member(self):
        b=(P/'metadata/147463_20191113_probe0__badtimes.h5').read_bytes()
        self.assertEqual(decode(b)['intervals'],[[900.0,2730.0]])
    def test_member_wrong_shape_and_external_link_denied(self):
        for external in [False,True]:
            b=io.BytesIO()
            with h5py.File(b,'w') as h:
                if external:h['badtints']=h5py.ExternalLink('forbidden','counts')
                else:h.create_dataset('badtints',data=[1,2,3])
            with self.assertRaises(ValueError):decode(b.getvalue())
    def test_manual_corrupt_bytes(self):
        with self.assertRaises(OSError):decode(b'not HDF5')
    def test_empty_synthetic_unit_fails(self):self.assertFalse(screen([[] for _ in range(60)])['pass'])
    def test_training_operational_qc_pass_and_exposure(self):
        r=screen([[.2,1.2,2.2] for _ in range(60)])
        self.assertTrue(r['pass']);self.assertEqual(r['rate_hz'],1);self.assertEqual(r['exposure_seconds'],180)
    def test_no_ISI_crosses_epochs(self):
        r=screen([[2.999] if i%2 else [0.0] for i in range(60)])
        self.assertEqual(r['adjacent_ISIs'],0);self.assertFalse(r['pass'])
    def test_refractory_bad_unit(self):self.assertFalse(screen([[.2,.2001,2] for _ in range(60)])['pass'])
    def test_duplicate_and_outside_and_nonfinite(self):
        for ts in [[.2,.2],[3],[float('nan')],[-.1]]:
            with self.assertRaises(ValueError):screen([ts]+[[] for _ in range(59)])
    def test_wrong_partition_size_rejected(self):
        with self.assertRaises(ValueError):screen([[] for _ in range(59)])
    def test_occupancy_not_just_total_count(self):
        ts=[i*.01 for i in range(100)]
        self.assertFalse(screen([ts]+[[] for _ in range(59)])['pass'])
    def test_original_outward_PG_polarity(self):
        self.assertEqual(projected_gradient([-8,8,0],[4,-5,.0005]),.0005)
        self.assertEqual(projected_gradient([-8,8,0],[-4,5,0]),5)
        with self.assertRaises(ValueError):projected_gradient([9],[0])
    def test_no_active_cohort_promotion(self):
        a=json.loads((P/'results/initial/audit.json').read_text())
        self.assertLess(a['bounds']['refined_B120'],16);self.assertFalse(a['protocol_activated'])
        self.assertEqual({r['quietdet_src'] for r in a['records']},{'self'})
    def test_proposed_allocation_exact_disjoint_no_replacement(self):
        a=json.loads((P/'PROPOSED_ALLOCATION.json').read_text());r=json.loads((P/'results/initial/audit.json').read_text())
        self.assertEqual((len(a['development']),len(a['final'])),(10,9));self.assertFalse(set(a['development'])&set(a['final']))
        self.assertEqual(set(a['development']+a['final']),{x['mouse_id'] for x in r['records'] if x['A_potential']});self.assertFalse(a['replacements'])
    def test_original_thresholds_and_complexity_denominators(self):
        c=json.loads((P/'PROPOSED_CONFIG.json').read_text())
        self.assertEqual((c['units'],c['epochs']),(8,120));self.assertEqual(c['D']['added_free_parameters'],c['C']['added_free_parameters'])
        self.assertEqual(c['numerical']['PG_max'],.001);self.assertEqual(c['numerical']['independent_gradient_relative_max'],1e-5)
        self.assertEqual(30*25*8,6000);self.assertEqual(60*25*8,12000);self.assertEqual(3+4*9+27+27,c['development_fit_cap_per_mouse'])
    def test_source_single_nan_convention_present(self):
        source=(M/'code__python__utils__data_classes.py').read_text()
        self.assertIn('np.size(temp)==2 and hasnan',source);self.assertIn('self._spikesatmat = np.empty((0,2))',source)
        normal=(OLD/'headers.py').read_text();self.assertIn('isfinite',normal)
    def test_no_neural_provider_transport(self):
        with self.assertRaises(ValueError):Transport().request('https://api.dandiarchive.org/api/assets/forbidden/download/')
        with self.assertRaises(ValueError):Transport().request('https://zenodo.org/api/records/14205018/files/preprocessing.zip/content')
    def test_bounded_archive_read(self):
        r=ArchiveReader(None)
        with self.assertRaises(ValueError):r.read()
        with self.assertRaises(ValueError):r.seek(SIZE+1)
    def test_actual_transport_lowercase_header_range_contract(self):
        class Response:
            status_code=206;headers=requests.structures.CaseInsensitiveDict({'content-range':f'bytes 0-65535/{SIZE}'})
            def __enter__(self):return self
            def __exit__(self,*a):return False
            def raise_for_status(self):return None
            def iter_content(self,n):yield b'X'*65536
        t=Transport()
        with patch.object(t.session,'get',return_value=Response()),patch.object(Path,'open',side_effect=AssertionError('No audit-journal writes in synthetic test')):
            # Redirect only the journal to memory while exercising request/header normalization.
            class Journal:
                def open(self,*a,**k):return io.StringIO()
            t.journal=Journal();reader=ArchiveReader(t)
            self.assertEqual(reader.read(3),b'XXX')
    def test_wrong_content_range_denied(self):
        class T:
            def request(self,*a,**k):return b'X'*65536,{'Content-Range':'wrong'},{}
        with self.assertRaises(ValueError):ArchiveReader(T()).read(1)
    def test_continuous_exact_one_lag_index(self):
        self.assertEqual(scalar_leaky_states([1,2,9],.5),[0, .5,1.25])
    def test_continuous_future_perturbation(self):
        self.assertEqual(scalar_leaky_states([1,2,9],.5),scalar_leaky_states([1,2,-900],.5))
    def test_continuous_epoch_reset(self):
        self.assertEqual(scalar_leaky_states([9,9],.5)[0],0)
        self.assertEqual(scalar_leaky_states([0,0],.5),[0,0])
    def test_sign_enumeration_and_nonzero_mean_counterexample(self):
        self.assertEqual(sign_flip_p([1]*8),2/256)
        self.assertAlmostEqual(.9*1+.1*(-9),0)
        self.assertAlmostEqual(.9**8,.43046721)
        # Enumeration is not a valid test of unrestricted zero population mean.
        self.assertGreater(.9**8,.05)
    def test_stronger_baseline_guard_counterexample(self):
        self.assertGreater(-1.05-(-1.1),0)
        self.assertFalse(broad_baseline_direction(-1.05,-1.1,-1.0))
        self.assertTrue(broad_baseline_direction(-.95,-1.1,-1.0))
    def test_static_mixture_has_no_persistent_prior(self):
        self.assertEqual(state_prior(.5,[.9,.1]),[.5,.5])
        self.assertEqual(state_prior(.5,[.1,.9]),[.5,.5])
        self.assertFalse(temporal_direction(.5,-1,-2))
    def test_persistent_state_prior_and_guard(self):
        self.assertAlmostEqual(state_prior(.98,[.9,.1])[0],.884)
        self.assertTrue(temporal_direction(.98,-1,-2))
        self.assertFalse(temporal_direction(.98,-2,-1))
    def test_reduced_unit_inputs_remove_omitted_sources(self):
        terms=[(2,3,None),(1,4,7),(100,9,8)]
        self.assertEqual(restricted_linear(terms,{7}),10)
        self.assertEqual(restricted_linear(terms,{7,8}),910)
    def test_saved_anatomy_cell_applicability(self):
        from collections import Counter
        census=Counter()
        for p in (M/'headers').glob('000473_*.json'):
            v=json.loads(p.read_text())['decoded_values'];labels=v['/general/extracellular_ephys/electrodes/location']
            for e in v['/units/electrodes']:
                if labels[e].startswith('PL'):census[labels[e]]+=1
        self.assertEqual(dict(census),{'PL5':1064,'PL6a':754,'PL2/3':68,'PL6b':14})
        self.assertEqual(census['PL'],0)
        self.assertEqual(deep_laminar_mask({1:'PL5',2:'PL6a',3:'PL2/3',4:'PL6b',5:'PL'}),[1,2])
    def test_recent_event_censors_whole_epoch_not_target_tone(self):
        e=[10,13]
        self.assertFalse(censor_recent_epoch(e,[13]))
        self.assertTrue(censor_recent_epoch(e,[5]))
        self.assertTrue(censor_recent_epoch(e,[12.999]))
        self.assertFalse(censor_recent_epoch(e,[4.999]))
    def test_recent_event_interval_half_open_boundary(self):
        self.assertFalse(censor_recent_epoch([10,13],[],[[1,5]]))
        self.assertTrue(censor_recent_epoch([10,13],[],[[4,5.001]]))
    def test_alignment_never_scores_tone_response(self):
        self.assertEqual(len(shifted_score_bins([10,13],-.1)),25)
        self.assertEqual(len(shifted_score_bins([10,13],.1)),24)
        self.assertTrue(all(b<=13+1e-10 for a,b in shifted_score_bins([10,13],.1)))
    def test_revised_contract_guards_and_coverage(self):
        c=json.loads((P/'PROPOSED_CONFIG.json').read_text())
        self.assertEqual(c['final_fit_cap_per_mouse'],15+3+1+3)
        self.assertEqual(c['claim_guard_family'],['D-B*','C-B*','D-S'])
        self.assertIn('NOT unrestricted zero mean',c['sign_flip_null'])
        self.assertEqual(c['sensitivity_anatomy']['census']['PL'],0)
        self.assertEqual(c['sensitivity_minimum']['missing_required_panel'],'INCONCLUSIVE')
    def test_preserved_failed_r1_exact_inputs(self):
        import hashlib
        from zipfile import ZipFile
        e=P.parent/'ops/evidence/2026-10-15/p13-ki-pl-quality-epoch-resolution-1'
        with ZipFile(e/'reviewed_r1_package.zip') as z:
            snap=json.loads(z.read('FREEZE_r1.json'))
            self.assertEqual(len(snap['hashes']),82)
            for name,expected in snap['hashes'].items():
                payload=z.read(name.removeprefix('paper13_ki_pl_contract1/')) if name.startswith('paper13_ki_pl_contract1/') else (P.parent/name).read_bytes()
                self.assertEqual(hashlib.sha256(payload).hexdigest(),expected,name)

if __name__=='__main__':unittest.main(verbosity=2)
