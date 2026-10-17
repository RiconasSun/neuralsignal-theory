"""Source/causal-policy regression oracles, never real neural model tests."""
import itertools
import json
import unittest
from unittest.mock import patch
import numpy as np
import pandas as pd
from . import audit,columns,inventory,protocol_support as policy,retrieve

def trials():
    rows=[]
    for b in range(6):
        for k in range(75):
            t=10*(b*75+k)
            rows.append(dict(trial_index=b*75+k,block_index=b,rewarded_modality='aud' if b%2==0 else 'vis',start_time=t,stim_start_time=t+1,stim_stop_time=t+1.5,stop_time=t+3,is_opto=False,is_response=False,response_time=np.nan,is_rewarded=False,reward_time=np.nan))
    frame=pd.DataFrame(rows)
    # Nullable source flags must reach the policy oracle, including malformed cases.
    for name in ['is_opto','is_response','is_rewarded']:frame[name]=frame[name].astype(object)
    for name in ['start_time','stim_start_time','stim_stop_time','stop_time']:frame[name]=frame[name].astype(float)
    return frame

class RecoveryTests(unittest.TestCase):
    def test_historical_evidence(self):self.assertEqual(audit.verify_history(),281)

    def test_license_bucket_not_cross_transferred(self):
        a=dict(location='s3://aind-open-data/a',name='a',data_description={'license':'CC-BY-4.0'})
        self.assertTrue(inventory.public(a))
        for location in ['s3://aind-scratch-data/a','s3://aind-open-data/another']:
            self.assertFalse(inventory.public(dict(a,location=location)))

    def test_public_pagination_and_sorted_agreement(self):
        x=audit.catalog_pages();self.assertEqual(len(x),595);self.assertEqual(len({a['_id'] for a in x}),595)

    def test_exact_session_not_same_mouse(self):
        a=dict(name='ecephys_123456_2024-01-02_12-00-00_nwb_2026-01-01_00-00-00',data_description={'subject_id':'123456'})
        self.assertEqual(inventory.session(a),'123456_2024-01-02')
        self.assertNotEqual(inventory.session(a),'123456_2024-01-01')
        with self.assertRaises(ValueError):inventory.session(dict(a,data_description={'subject_id':'000000'}))

    def test_unknown_sessions_retained_in_upper(self):
        rows=[dict(mouse='1',anatomy_status='FAIL_REGISTERED_ANATOMY_QC'),dict(mouse='1',anatomy_status='UNRESOLVED_HDF5_NOT_READ'),dict(mouse='2',anatomy_status='FAIL_REGISTERED_ANATOMY_QC'),dict(mouse='3',anatomy_status='POTENTIAL_ANATOMY_ONLY')]
        self.assertEqual(audit.conservative_mouse_upper(rows),2)
        self.assertEqual(audit.conservative_mouse_upper(rows+rows),2)

    def test_anatomy_exact_descendants(self):
        for s in ['ACAd','ACAv2/3','PL6a','ILA1']:self.assertIsNotNone(columns.region(s))
        for s in ['MOs','ORBvl','PLextra','ACA','unknown']:self.assertIsNone(columns.region(s))

    def test_metadata_decoder_rejects_neural(self):
        for f in ['units/spike_times','units/spike_amplitudes','units/firing_rate','processing/running/data']:
            with self.assertRaises(PermissionError):columns.decode('662892_2023-08-24',f)

    def test_metadata_decoder_known_finite_dimensions(self):
        x=columns.decode('662892_2023-08-24','units/structure');q=columns.decode('662892_2023-08-24','units/is_qc_pass')
        self.assertEqual(len(x),1120);self.assertEqual(len(q),1120);self.assertEqual(q.dtype,np.dtype('bool'))

    def test_network_validator_denies_signal_and_unregistered_paths(self):
        root='https://aind-open-data.s3.us-west-2.amazonaws.com/'
        for path in ['unregistered/data_description.json',retrieve.read(retrieve.P/'CANONICAL_ACCESS.json')['prefixes'][0]+'/units/spike_times/0','unregistered.nwb']:
            with self.assertRaises(PermissionError):retrieve.validate(root+path)
        with self.assertRaises(PermissionError):retrieve.validate('https://aind-scratch-data.s3.us-west-2.amazonaws.com/anything')

    def test_listing_trailing_slash_regression(self):
        prefix=retrieve.read(retrieve.P/'CANONICAL_ACCESS.json')['prefixes'][0]
        for s in [prefix,prefix+'/']:retrieve.validate(inventory.S3,{'list-type':'2','prefix':s,'max-keys':'1000'})
        with self.assertRaises(PermissionError):retrieve.validate(inventory.S3,{'list-type':'2','prefix':prefix+'-other/','max-keys':'1000'})

    def test_literal_None_restriction_regression(self):
        old=audit.read
        def bad(path):
            x=old(path)
            if str(path).endswith('dynamic_routing_public_all_assets.json'):
                x[0]['data_description']['restrictions']='No secondary analysis'
            return x
        with patch.object(audit,'read',side_effect=bad):
            with self.assertRaisesRegex(ValueError,'restriction'):audit.catalog_pages()

    def test_missing_events_never_imputed(self):
        f=trials();f.loc[10,'is_response']=True;f.loc[20,'is_rewarded']=True;f.loc[30,['is_response','response_time']]=[True,301.2]
        before=f.copy(deep=True);m=policy.missing_event_mask(f)
        self.assertFalse(m[10]);self.assertFalse(m[20]);self.assertTrue(m[30]);self.assertTrue(m[11]);pd.testing.assert_frame_equal(f,before)

    def test_unknown_flags_fail_closed(self):
        f=trials();f.loc[10,'is_response']=None
        self.assertFalse(policy.missing_event_mask(f)[10])

    def test_fixed_block_halves_and_first_five(self):
        m,h,c,ok=policy.masks(trials());self.assertTrue(ok);self.assertEqual(sum(m),420)
        for block in range(6):
            self.assertFalse(m[block*75:block*75+5].any())
            self.assertEqual(set(h[block*75:(block+1)*75]),{'calibration' if block<3 else 'scoring'})
        self.assertEqual(min(c.values()),70)

    def test_clock_inversion_and_block_merging_denied(self):
        f=trials();f.loc[20,'stim_start_time']=0
        with self.assertRaisesRegex(ValueError,'clock'):policy.masks(f)
        f=trials();f.loc[150:224,'block_index']=0
        with self.assertRaisesRegex(ValueError,'Reappearing'):policy.masks(f)

    def test_opto_unknown_timing_and_missing_response_excluded(self):
        f=trials();f.loc[10,'is_opto']=True;f.loc[11,'is_opto']=None;f.loc[12,'is_response']=True;f.loc[13,'stop_time']=131.1
        m,*_=policy.masks(f)
        self.assertFalse(m[10:14].any())

    def test_insufficient_cohort_no_swap_or_split(self):
        with self.assertRaises(ValueError):policy.allocate([f'{i:06}' for i in range(13)])
        with self.assertRaises(ValueError):policy.allocate(['000001']*16)
        ids=[f'{i:06}' for i in range(18)];a,b=policy.allocate(ids)
        self.assertEqual((len(a),len(b)),(9,9));self.assertFalse(set(a)&set(b));self.assertEqual((a,b),policy.allocate(ids[::-1]))

    def test_count_preserving_finite_definition_not_biological_null(self):
        x=np.arange(60).reshape(4,5,3);y=policy.temporal_definition_fixture(x,np.random.default_rng(7014))
        np.testing.assert_array_equal(x.sum(axis=1),y.sum(axis=1));self.assertEqual(y.shape,x.shape);self.assertTrue((y>=0).all())
        with self.assertRaises(ValueError):policy.temporal_definition_fixture(x.astype(float),np.random.default_rng(1))

    def test_every_required_ready_gate(self):
        keys=['license_verified','cohort_verified','timing_verified','protocol_frozen','review_accepted']
        for values in itertools.product([False,True],repeat=5):self.assertEqual(policy.ready_gate(**dict(zip(keys,values))),all(values))
        with self.assertRaises(ValueError):policy.ready_gate(**dict(zip(keys,[1]*5)))

    def test_registered_access_journal_no_signal(self):
        rows=[json.loads(x) for x in (retrieve.P/'sources/access.jsonl').read_text().splitlines()]
        limit=retrieve.read(retrieve.P/'REGISTRATION.json')['budget']
        self.assertLessEqual(len(rows),limit['attempts']);self.assertLessEqual(sum(x['bytes'] for x in rows),limit['total_bytes'])
        for row in rows:
            self.assertEqual(row['method'],'GET');self.assertNotIn('spike_times/0',row['url']);self.assertNotIn('spike_amplitudes/0',row['url'])
            self.assertFalse(row['url'].endswith('.nwb'));retrieve.validate(row['url'],row['params'])

if __name__=='__main__':unittest.main()
