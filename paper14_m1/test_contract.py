"""Source/allocation/coverage oracles only, no real or synthetic neural fits."""
import csv
import itertools
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from . import retrieve
from .audit import P,ROOT,allocation,cohort,canonical_sid,canonical_version289,descriptor_presence,activation_gate,metadata_path_match,collect_metadata_rates,verify_inputs,STATUSES


class ContractTests(unittest.TestCase):
    def test_original104M0_hashes(self):verify_inputs()

    def test_18_unique_original_populations(self):
        r=cohort();self.assertEqual(len(r),18);self.assertEqual(len({v['mouse'] for v in r}),18)
        self.assertTrue(all(v['region']=='mPFC_composite' for v in r))

    def test_reserved9_9_matches_original_prospective_hash_policy(self):
        r=allocation(cohort());self.assertEqual(sum(x['arm']=='development' for x in r),9);self.assertEqual(sum(x['arm']=='final' for x in r),9)
        expected={'746439','702131','714748','733891','690706','686740','666986','664851','737403'}
        self.assertEqual({x['mouse'] for x in r if x['arm']=='development'},expected)
        self.assertTrue(all(not x['activation_authorized'] and x['physiological_eligibility']=='UNMEASURED' for x in r))

    def test_order_does_not_change_allocation(self):
        self.assertEqual(allocation(cohort()),allocation(list(reversed(cohort()))))

    def test_no_refill_or_duplicate_animals(self):
        r=cohort()
        for bad in [r[:-1],r+[r[0]],r[:-1]+[r[0]]]:
            with self.assertRaises(ValueError):allocation(bad)

    def test_same_mouse_different_day_is_not_same_session(self):
        self.assertEqual(canonical_sid('ecephys_664851_2023-11-16_12-54-53_nwb_2026'),'664851_2023-11-16')
        self.assertNotEqual(canonical_sid('ecephys_664851_2023-11-16_12-54-53_nwb_2026'),'664851_2023-11-13')
        self.assertFalse(metadata_path_match('DRpilot_664851_20231116','664851_2023-11-13'))
        self.assertTrue(metadata_path_match('DRpilot_664851_20231113','664851_2023-11-13'))

    def test_processing_version_not_inferred_from_asset_label(self):
        x={'name':'v0.0.289','processing':{'data_processes':[{'process_type':'File format conversion','code':{'version':'0.0.288'}}]}}
        self.assertFalse(canonical_version289(x));x['processing']['data_processes'][0]['code']['version']='0.0.289';self.assertTrue(canonical_version289(x))

    def test_shape_and_filter_cutoff_are_not_sampling_frequency(self):
        d={'metadata':{'processing/behavior/running_speed/data/.zarray':{'shape':[10000]},'processing/behavior/running_speed/.zattrs':{'description':'low-pass 4Hz'}}}
        v=descriptor_presence(d);self.assertTrue(v['running']);self.assertNotIn('sampling_rate',v)
        self.assertEqual(collect_metadata_rates({'shape':[10000],'low_pass_filter_Hz':4}),{})
        self.assertEqual(collect_metadata_rates({'sampling_rate':60}),{'sampling_rate':60})

    def test_clock_required_and_no_neural_authorization_implied(self):
        names=['rights_all18','clock_all18','protocol_complete','independent_ready_review','neural_owner_authorization']
        for values in itertools.product([False,True],repeat=5):self.assertEqual(activation_gate(**dict(zip(names,values))),all(values))
        self.assertFalse(activation_gate(rights_all18=True,clock_all18=True,protocol_complete=True,independent_ready_review=True))

    def test_deny_NWB_and_signal_chunk_GET_before_network(self):
        with patch.object(retrieve.requests,'request',side_effect=AssertionError('Unexpected network')):
            for url in ['https://aind-scratch-data.s3.us-west-2.amazonaws.com/dynamic-routing/cache/nwb/v0.0.289/741137_2024-10-10.nwb','https://aind-scratch-data.s3.us-west-2.amazonaws.com/dynamic-routing/cache/nwb_components/v0.0.289/running_speed/x.zarr/data/0','https://example.com/license']:
                with self.subTest(url=url),self.assertRaises(PermissionError):retrieve.get(url,'forbidden')

    def test_mutations_denied_even_on_allowed_host(self):
        for method in ['POST','PUT','DELETE']:
            with self.assertRaises(PermissionError):retrieve.validate('https://api.allenneuraldynamics.org/v2/metadata_index/data_assets',method)

    def test_coverage18_exact_original_identities(self):
        with (P/'results/SESSION_COVERAGE_18.csv').open(encoding='utf8',newline='') as f:r=list(csv.DictReader(f))
        self.assertEqual({(x['mouse'],x['session'],x['probe']) for x in r},{(x['mouse'],x['session'],x['probe']) for x in cohort()})
        for x in r:
            for k in ['running_target_scratch_status','pupil_target_scratch_status','lick_response_status','behavior_ephys_clock_status','observations_status','interruption_status']:self.assertIn(x[k],STATUSES)
            self.assertEqual(x['behavior_ephys_clock_status'],'UNRESOLVED');self.assertEqual(x['pupil_target_scratch_status'],'UNRESOLVED')

    def test_canonical_license_does_not_resolve_scratch_scope(self):
        with (P/'results/SOURCE_RIGHTS_18.csv').open(encoding='utf8',newline='') as f:r=list(csv.DictReader(f))
        canonical=[x for x in r if x['canonical_licenses']=='CC-BY-4.0'];self.assertEqual(len(canonical),3)
        self.assertTrue(all(x['scratch_rights_status']=='UNRESOLVED' and x['canonical_to_scratch_applicability_proven']=='False' for x in r))

    def test_missing_response_event_not_imputed_from_outcome(self):
        with (P/'results/MISSING_RESPONSE_TIME_EVENTS.csv').open(encoding='utf8',newline='') as f:r=list(csv.DictReader(f))
        self.assertEqual(len(r),5);self.assertEqual(len({x['session'] for x in r}),4)
        self.assertTrue(all(x['response_time']=='MISSING_NOT_IMPUTED' for x in r))

    def test_journal_bounds_and_no_data_GET(self):
        rows=[json.loads(x) for x in (P/'sources/access.jsonl').read_text(encoding='utf8').splitlines()]
        limits=retrieve.read(P/'REGISTRATION.json')['new_http_limits'];self.assertLessEqual(len(rows),limits['attempts']);self.assertLessEqual(sum(x['bytes'] for x in rows),limits['total_bytes'])
        for x in rows:
            self.assertEqual(x['method'],'GET');self.assertFalse(x['url'].endswith(('.nwb','.h5','.parquet','.npy')))
            self.assertLessEqual(x['bytes'],limits['single_response_bytes'])

    def test_one_scientific_decision_and_no_protocol_activation(self):
        x=retrieve.read(P/'results/M1_DECISION.json');self.assertEqual(x['scientific_decision'],'SOURCE_RIGHTS_BLOCKED')
        self.assertFalse(x['scientific_protocol_frozen']);self.assertFalse(x['Prompt3_eligible_for_owner_consideration']);self.assertFalse(x['external_correspondence_sent'])
        self.assertEqual(x['raw_neural_values_or_raw_behavior_signals_read'],0);self.assertEqual(x['M0_verdict_unchanged'],'INCONCLUSIVE_METADATA')


if __name__=='__main__':unittest.main(verbosity=2)
