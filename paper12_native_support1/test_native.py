import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch,MagicMock
import h5py
import numpy as np
import clock
import digital
from native_headers import read,permitted
from analysis import presentation_trials,excluded,affected,region,native_clock_for_trial,channel_distances
from visual_clock import nearest,zero_frame_correction
from register import HERE,verify
from storage import load

class NativeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):(HERE/'replay').mkdir(exist_ok=True)
    def test_parser_mismatch_denied(self):
        fake=MagicMock();fake.extract_barcodes_from_times.return_value=([10,20],[99])
        with patch.object(clock,'official',return_value=fake):
            with self.assertRaises(RuntimeError):clock.decode([0],[1])
    def test_forbidden_cache_before_reuse(self):
        with patch.object(digital.requests,'get') as req:
            with self.assertRaises(RuntimeError):digital.acquire({'key':'visual-coding-neuropixels/raw-data/1/spike_times.npy','bytes':1},'x',10)
            req.assert_not_called()
    def test_corrupt_cache_denied(self):
        with tempfile.TemporaryDirectory(dir=HERE/'replay') as d:
            root=Path(d);folder=root/'metadata/digital';folder.mkdir(parents=True)
            (folder/'x.receipt').write_bytes(b'changed')
            item={'key':'visual-coding-neuropixels/raw-data/1/2/event_timestamps.npy','bytes':7,'etag_not_assumed_checksum':'etag'}
            receipt={'url':'https://allen-brain-observatory.s3.us-west-2.amazonaws.com/'+item['key'],
                     'bytes':7,'etag':'etag','sha256':hashlib.sha256(b'original').hexdigest()}
            (folder/'x.json').write_text(json.dumps(receipt))
            with patch.object(digital,'HERE',root),patch.object(digital.requests,'get') as req:
                with self.assertRaises(RuntimeError):digital.acquire(item,'x',100,offline=True)
                req.assert_not_called()
    def test_offline_missing_cache_never_network(self):
        with tempfile.TemporaryDirectory(dir=HERE/'replay') as d:
            item={'key':'visual-coding-neuropixels/raw-data/1/2/event_timestamps.npy','bytes':8,'etag_not_assumed_checksum':'etag'}
            with patch.object(digital,'HERE',Path(d)),patch.object(digital.requests,'get') as req:
                with self.assertRaises(RuntimeError):digital.acquire(item,'x',100,offline=True)
                req.assert_not_called()
    def test_numeric_vlen_denied(self):
        with tempfile.TemporaryDirectory(dir=HERE/'replay') as d:
            with h5py.File(Path(d)/'fixture.h5','w') as f:
                f.create_dataset('/intervals/invalid_times/start_time',data=['neural?'],dtype=h5py.string_dtype())
                with self.assertRaises(RuntimeError):read(f,'/intervals/invalid_times/start_time')
    def test_string_tags_allowed(self):
        with tempfile.TemporaryDirectory(dir=HERE/'replay') as d:
            with h5py.File(Path(d)/'fixture.h5','w') as f:
                f.create_dataset('/intervals/invalid_times/tags',data=['EcephysProbe'],dtype=h5py.string_dtype())
                self.assertEqual(read(f,'/intervals/invalid_times/tags'),['EcephysProbe'])
    def test_soft_link_denied(self):
        with tempfile.TemporaryDirectory(dir=HERE/'replay') as d:
            with h5py.File(Path(d)/'fixture.h5','w') as f:
                g=f.create_group('/intervals/invalid_times');g['start_time']=h5py.SoftLink('/somewhere')
                with self.assertRaises(RuntimeError):read(f,'/intervals/invalid_times/start_time')
    def test_neural_paths_denied(self):
        for path in ('/units/spike_times','/processing/mean_waveforms','/acquisition/running_speed/data'):
            self.assertFalse(permitted(path))
            with self.assertRaises(RuntimeError):read({},path)
    def test_movie_frames_not_trials(self):
        frames=np.tile(np.arange(900),2);t=np.arange(1800)/30
        table={'frame':frames,'start_time':t,'stop_time':t+1/30,'stimulus_block':np.repeat([3,8],900)}
        trials,summary=presentation_trials(table,'movie')
        self.assertEqual(len(trials),2);self.assertEqual(summary['presentation_rows'],1800)
    def test_incomplete_movie_not_counted(self):
        n=899;t=np.arange(n)/30
        trials,summary=presentation_trials({'frame':np.arange(n),'start_time':t,'stop_time':t+1/30,'stimulus_block':np.zeros(n)},'movie')
        self.assertEqual(len(trials),0);self.assertEqual(summary['incomplete_runs'],1)
    def test_overlapping_movie_rejected(self):
        t=np.arange(900)/30
        with self.assertRaises(RuntimeError):presentation_trials({'frame':np.arange(900),'start_time':t,'stop_time':t+.1,'stimulus_block':np.zeros(900)},'movie')
    def test_grating_conditions(self):
        table={'start_time':[0,3],'stop_time':[2,5],'orientation':[0,0],'contrast':[.8,.8],'temporal_frequency':[2,2]}
        trials,summary=presentation_trials(table,'grating');self.assertEqual(summary['genuine_trials'],2)
    def test_probe_exclusion_tags(self):
        rows=excluded({'start_time':[1],'stop_time':[2],'tags':['EcephysProbe','p','probeA'],'tags_index':[3]})
        registry={'p':'probeA','q':'probeB'}
        self.assertTrue(affected(rows[0]['tags'],'p','probeA',registry));self.assertFalse(affected(rows[0]['tags'],'q','probeB',registry))
        self.assertIsNone(affected(['unknown'],'p','probeA'))
    def test_unknown_probe_exclusion_not_ignored(self):
        self.assertIsNone(affected(['EcephysProbe','missing'],'p','probeA',{'p':'probeA'}))
        self.assertIsNone(affected(['EcephysProbe','p','probeB'],'p','probeA',{'p':'probeA','q':'probeB'}))
    def test_channel_geometry_independent_fixture(self):
        rows=[{'id':'a','probe_vertical_position':0,'structure_acronym':'CA1'},
              {'id':'b','probe_vertical_position':20,'structure_acronym':'CA1'},
              {'id':'c','probe_vertical_position':40,'structure_acronym':'DG'},
              {'id':'d','probe_vertical_position':None,'structure_acronym':'DG'}]
        self.assertEqual(channel_distances(rows),{'a':40.0,'b':20.0,'c':20.0,'d':None})
    def test_extrapolation_not_certified(self):
        p={'probe_id':'p','name':'probeA','segments':[{'pass':True,'master_anchor_min_seconds':10,'master_anchor_max_seconds':30}]}
        self.assertFalse(native_clock_for_trial(p,0,5,[]));self.assertTrue(native_clock_for_trial(p,15,20,[]))
        self.assertFalse(native_clock_for_trial(p,15,20,[{'start':16,'stop':17,'tags':['EcephysProbe','p']}]))
    def test_nearest_oracle(self):np.testing.assert_allclose(nearest([0,.02,.04],[.001,.039]),[.001,.001])
    def test_frame_correction_nochange_regular(self):np.testing.assert_allclose(zero_frame_correction(np.arange(121)/60),np.arange(121)/60)
    def test_no_mtl_mixing(self):
        self.assertIsNone(region('SUB'));self.assertIsNone(region('CA2'));self.assertEqual(region('DG-sg'),'DG')
    def test_all_schema_checks(self):
        rows=[load(p) for p in (HERE/'metadata/schema_checks').glob('*.json')]
        self.assertEqual(len(rows),58);self.assertTrue(all(r['pass'] and not r['decoded_values'] for r in rows))
    def test_prior_papers_original_m0_immutable(self):self.assertGreater(len(verify()['prior_hashes']),11000)
    def test_original_admission_not_pass(self):
        for name in ('allen_gate_result.json','ibl_gate_result.json','gate_result.json'):
            self.assertFalse(load(HERE.parent/'paper12/results'/name)['pass'])
    def test_full_denominators(self):
        r=load(HERE/'results/summary.json');self.assertEqual((r['sessions'],r['probes'],r['channels']),(58,332,123224))
        self.assertEqual(r['original_admitted_mice'],0)
    def test_metadata_compaction_exact(self):
        from storage import bytes_for
        for row in load(HERE/'metadata/compact_manifest.json'):
            self.assertEqual(hashlib.sha256(bytes_for(HERE/row['logical_path'])).hexdigest(),row['original_sha256'])

if __name__=='__main__':unittest.main(verbosity=2)
