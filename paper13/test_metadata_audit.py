"""Synthetic contract oracles, independent of saved biological outcomes."""
import copy
import json
import unittest
import uuid
from contextlib import contextmanager
from pathlib import Path
from unittest.mock import patch
import acquire_metadata
import verify_saved
from metadata_audit import audit, region, trial_status
from acquire_metadata import Transport, ParquetRanges


@contextmanager
def saved_test_folder():
    # Retain test journals, including injected failures, under the ignored work tree.
    folder=Path(__file__).resolve().parent/'work'/('test_'+uuid.uuid4().hex)
    folder.mkdir(parents=True)
    yield folder


def fixtures(n=16, units=20, trials=400):
    fs=[{'pid':f'p{i}','eid':f'e{i}','lab':'lab','subject':f'm{i}','probe_name':'probe00'} for i in range(n)]
    cs=[{'pid':f'p{i}','eid':f'e{i}','cluster_id':str(j),'uuids':f'u{i}_{j}','atlas_id':'1','label':'1.0'}
        for i in range(n) for j in range(units)]
    ts=[{'eid':f'e{i}','intervals_0':'0','intervals_1':'2','stimOn_times':'.5','goCue_times':'.6',
         'feedback_times':'1.5','bwm_include':'True'} for i in range(n) for _ in range(trials)]
    return fs,cs,ts,{'1':'ACAd5'}


class AdmissionTests(unittest.TestCase):
    def test_laminar_only(self):
        for name in ('ACAd','ACAd1','ACAd2/3','ACAd5','ACAd6a','ACAd6b'):
            self.assertEqual(region(name),'ACAd')
        for name in ('ACAv','ACAdventral','ORBl','ORB','PLX','MOs','ACAd2'):
            self.assertIsNone(region(name))

    def test_exact_boundary_and_no_false_full_admission(self):
        r,_,_=audit(*fixtures())
        self.assertTrue(r['regions']['ACAd']['meets_minimum_upper_bound'])
        self.assertEqual(r['scientific_gate'],'PENDING_ESSENTIAL_METADATA')
        self.assertFalse(r['continue_M1'])
        self.assertEqual(r['regions']['ACAd']['fully_admitted_mice'],0)

    def test_15_mice_fails(self):
        r,_,_=audit(*fixtures(n=15))
        self.assertTrue(r['stop_required'])
        self.assertEqual(r['regions']['ACAd']['maximum_possible_smaller_group'],7)

    def test_19_units_fails(self):
        r,_,_=audit(*fixtures(units=19))
        self.assertEqual(r['regions']['ACAd']['unit_threshold_mice'],0)

    def test_399_trials_fails(self):
        r,_,_=audit(*fixtures(trials=399))
        self.assertEqual(r['regions']['ACAd']['count_upper_bound_mice'],0)

    def test_same_mouse_repeated_sessions_not_independent(self):
        args=fixtures()
        for row in args[0]: row['subject']='same'
        r,_,_=audit(*args)
        self.assertEqual(r['regions']['ACAd']['count_upper_bound_mice'],1)

    def test_regions_not_pooled(self):
        args=fixtures(units=10)
        for i,row in enumerate(args[1]): row['atlas_id']=str(1+i%2)
        args[3]['2']='PL5'
        r,_,_=audit(*args)
        self.assertTrue(r['stop_required'])
        self.assertEqual(r['regions']['ACAd']['unit_threshold_mice'],0)

    def test_probes_not_pooled(self):
        fs,cs,ts,atlas=fixtures(n=1,units=20)
        fs.append({**fs[0],'pid':'psecond'})
        for row in cs[10:]: row['pid']='psecond'
        r,_,_=audit(fs,cs,ts,atlas)
        self.assertEqual(r['regions']['ACAd']['unit_threshold_mice'],0)

    def test_bad_units_not_admitted(self):
        args=fixtures()
        for row in args[1]: row['label']='0.6666666666666666'
        r,_,_=audit(*args)
        self.assertEqual(r['regions']['ACAd']['provider_good_units'],0)

    def test_duplicate_probe(self):
        fs,cs,ts,a=fixtures(n=1);fs.append(copy.deepcopy(fs[0]))
        with self.assertRaisesRegex(ValueError,'Duplicate fixture'): audit(fs,cs,ts,a)

    def test_duplicate_cluster(self):
        fs,cs,ts,a=fixtures(n=1);cs.append(copy.deepcopy(cs[0]))
        with self.assertRaisesRegex(ValueError,'Duplicate cluster'): audit(fs,cs,ts,a)

    def test_duplicate_uuid(self):
        fs,cs,ts,a=fixtures(n=1);cs[1]['uuids']=cs[0]['uuids']
        with self.assertRaisesRegex(ValueError,'UUID'): audit(fs,cs,ts,a)

    def test_wrong_identity_join(self):
        fs,cs,ts,a=fixtures(n=1);cs[0]['eid']='different'
        with self.assertRaisesRegex(ValueError,'mismatch'): audit(fs,cs,ts,a)

    def test_conflicting_session_mouse(self):
        fs,cs,ts,a=fixtures(n=2);fs[1]['eid']=fs[0]['eid']
        with self.assertRaisesRegex(ValueError,'Conflicting'): audit(fs,cs,ts,a)

    def test_missing_trials_not_pass(self):
        fs,cs,_,a=fixtures(n=16)
        r,_,_=audit(fs,cs,[],a)
        self.assertEqual(len(r['denominator']['fixture_sessions_missing_trials']),16)
        self.assertTrue(r['stop_required'])

    def test_nonfinite_and_noncausal_trial_events(self):
        row=fixtures(n=1,units=1,trials=1)[2][0]
        self.assertEqual(trial_status(row),'usable')
        self.assertEqual(trial_status({**row,'stimOn_times':'nan'}),'nonfinite_timing')
        self.assertEqual(trial_status({**row,'feedback_times':'.1'}),'invalid_event_order')
        self.assertEqual(trial_status({**row,'bwm_include':'False'}),'provider_excluded')
        self.assertEqual(trial_status({**row,'intervals_1':'.05'}),'invalid_event_order')

    def test_deny_spike_and_unregistered_provider(self):
        t=Transport()
        for url in ('https://unregistered.invalid/metadata','https://ibl-brain-wide-map-public.s3.amazonaws.com/aggregates/spikes.times.npy'):
            with self.assertRaises(ValueError): t.request(url)

    def test_range_rejects_full_object_response(self):
        class Fake:
            def request(self,url,**kwargs):
                if kwargs.get('method')=='HEAD': return b'',{'Content-Length':'10','ETag':'abc'},{}
                return b'123',{'Content-Range':'bytes 0-2/10','ETag':'CHANGED'},{}
        reader=ParquetRanges(Fake(),'unused')
        with self.assertRaisesRegex(RuntimeError,'changed'): reader.read(3)
        with self.assertRaises(ValueError): reader.read(-1)

    def test_http_200_range_response_never_read(self):
        class Response:
            status_code=200
            headers={}
            def __enter__(self): return self
            def __exit__(self,*args): pass
            def iter_content(self,*args):
                raise AssertionError('Bulk response must never be consumed')
        class Session:
            def request(self,*args,**kwargs): return Response()
        with saved_test_folder() as folder, patch.object(acquire_metadata,'META',Path(folder)):
            t=Transport();t.session=Session()
            with self.assertRaises(RuntimeError):
                t.request('https://ibl-brain-wide-map-public.s3.amazonaws.com/aggregates/metadata.pqt',headers={'Range':'bytes=0-2'})
            rows=[json.loads(line) for line in (Path(folder)/'access.jsonl').read_text().splitlines()]
            self.assertEqual(len(rows),2)
            self.assertEqual(sum(r['bytes'] for r in rows),0)

    def test_global_request_budget_uses_existing_journal(self):
        with saved_test_folder() as folder, patch.object(acquire_metadata,'META',Path(folder)):
            (Path(folder)/'access.jsonl').write_text('{"bytes":7}\n'*1800)
            t=Transport()
            self.assertEqual(t.used,12600)
            with self.assertRaisesRegex(RuntimeError,'Request budget'):
                t.request('https://api.github.com/repos/int-brain-lab/metadata')

    def test_saved_hash_tampering_fails_before_replay(self):
        with saved_test_folder() as folder, patch.object(verify_saved,'P',Path(folder)):
            (Path(folder)/'saved_inventory.json').write_text(json.dumps({'files':[
                {'path':'paper13/M0_REGISTRATION.json','sha256':'0'*64}]}))
            with self.assertRaisesRegex(ValueError,'altered saved artifact'):
                verify_saved.verify_inventory()


if __name__=='__main__': unittest.main()
