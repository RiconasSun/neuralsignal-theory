"""Fully synthetic official NWB integration and actual entrypoint denial tests."""
import concurrent.futures,datetime,json, tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import numpy as np
from pynwb import NWBFile,NWBHDF5IO
from pynwb.epoch import TimeIntervals
from hdmf.common.table import VectorIndex
from . import pilot_reader as reader,pilot_transfer as transfer
from .core import dump_json,read_json,sha256,TransferBudget
from .access_gate import REQUIRED,E,verify_access_approval

class IntegrationTests(unittest.TestCase):
    def test_headers_redacted_case_insensitively(self):
        from .http_metadata import sanitize_headers
        source={'sEt-CoOkIe':'synthetic-cookie','Authorization':'synthetic-token','Cookie':'synthetic-value','Proxy-Authorization':'synthetic-value','X-API-Key':'synthetic-value','ETag':'object-identity','Content-Length':'64'}
        actual=sanitize_headers(source)
        self.assertTrue(all(actual[k]=='<REDACTED_HEADER>' for k in list(source)[:5]))
        self.assertEqual(actual['ETag'],'object-identity');self.assertEqual(actual['Content-Length'],'64')

    def temp(self):
        base=Path(__file__).resolve().parents[1]/'work';base.mkdir(exist_ok=True)
        return tempfile.TemporaryDirectory(dir=base)
    def approval(self,root):
        for rel in REQUIRED:
            path=root/rel;path.parent.mkdir(parents=True,exist_ok=True)
            if not path.exists():path.write_text('{}')
        report=root/E/'PILOT_ACCESS_REVIEW.md';report.parent.mkdir(parents=True,exist_ok=True);report.write_text('SYNTHETIC approval fixture only')
        receipt={'decision':'ACCEPTED_BOUNDED_PILOT_ACCESS','approved_spike_GET_or_decode':True,'open_P0':0,'open_P1':0,'report_sha256':sha256(report),'reviewed_hashes':{rel:sha256(root/rel) for rel in REQUIRED}}
        dump_json(root/E/'PILOT_ACCESS_REVIEW_RECEIPT.json',receipt);return receipt
    def test_rejected_empty_incomplete_tampered_approval_denied(self):
        with self.temp() as temp:
            root=Path(temp);valid=self.approval(root);target=root/E/'PILOT_ACCESS_REVIEW_RECEIPT.json'
            self.assertEqual(verify_access_approval(root)['open_P0'],0)
            for key,value in [('decision','REJECTED'),('approved_spike_GET_or_decode',False),('open_P0',False),('open_P1',0.0),('reviewed_hashes',{}),('report_sha256','0'*64)]:
                dump_json(target,{**valid,key:value})
                with self.assertRaises(ValueError):verify_access_approval(root)
            dump_json(target,valid);(root/'paper16_m0/code/core.py').write_text('altered')
            with self.assertRaises(ValueError):verify_access_approval(root)
    def test_actual_download_entrypoint_rejects_before_network(self):
        with self.temp() as temp:
            root=Path(temp);p=root/'paper16_m0';(p/'results').mkdir(parents=True)
            dump_json(p/'results/PILOT_OBJECT_FREEZE.json',{})
            self.approval(root);receipt=read_json(root/E/'PILOT_ACCESS_REVIEW_RECEIPT.json');receipt['decision']='REJECTED';receipt['reviewed_hashes']={};dump_json(root/E/'PILOT_ACCESS_REVIEW_RECEIPT.json',receipt)
            with patch.multiple(transfer,P=p,R=root,E=root/E),patch('urllib.request.urlopen',side_effect=AssertionError('Network must not be reached')):
                with self.assertRaises(ValueError):transfer.download()
    def test_exclusive_claim_and_conservative_crash_budget(self):
        with self.temp() as temp:
            path=Path(temp)/'attempt.json'
            def claim(i):
                try:transfer.claim_attempt(path,{'attempt':i});return True
                except FileExistsError:return False
            with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
                self.assertEqual(sum(pool.map(claim,range(16))),1)
            budget=TransferBudget(Path(temp)/'budget.json',100);budget.charge(100,'reserve BEFORE any receive')
            # Simulated crash before first block leaves full conservative consumption.
            self.assertEqual(read_json(budget.path)['bytes'],100)
            with self.assertRaises(ValueError):TransferBudget(budget.path,100).charge(1,'duplicate')
    def test_download_read_failure_keeps_full_reservation_and_denies_retry(self):
        with self.temp() as temp:
            root=Path(temp);p=root/'paper16_m0'
            for name in ['results','work','metadata']:(p/name).mkdir(parents=True,exist_ok=True)
            role={'session_id':1,'mouse_id':'1','probe_id':1,'group':'Development'}
            dump_json(p/'results/ROLE_ALLOCATION.json',[role]);dump_json(p/'results/PILOT_METADATA_SELECTION.json',[role])
            dump_json(p/'results/PILOT_OBJECT_FREEZE.json',{'roles_sha256':sha256(p/'results/ROLE_ALLOCATION.json'),'objects':[{**role,'content_length':64,'resolved_url':'https://synthetic.invalid/no-network','etag':'fixture'}]})
            self.approval(root)
            class BrokenResponse:
                headers={'Content-Length':'64','ETag':'fixture'}
                def __enter__(self):self.calls=0;return self
                def __exit__(self,*args):pass
                def read(self,size):
                    self.calls+=1
                    if self.calls==1:return b'abc'
                    raise OSError('SYNTHETIC interruption')
            with patch.multiple(transfer,P=p,R=root,E=root/E),patch('urllib.request.urlopen',return_value=BrokenResponse()) as request:
                with self.assertRaises(OSError):transfer.download()
                self.assertEqual(request.call_count,1)
                self.assertEqual(read_json(p/'results/PAYLOAD_LEDGER.json')['bytes'],20_000_064)
                self.assertEqual((p/'work/session_1.partial').read_bytes(),b'abc')
                self.assertEqual(read_json(p/'results/TRANSFER_1.json')['status'],'FAILED')
                with self.assertRaises(FileExistsError):transfer.download()
                self.assertEqual(request.call_count,1)

    def test_real_pynwb_synthetic_main_lazy_rows_native_events_missing_behavior(self):
        with self.temp() as temp:
            root=Path(temp);p=root/'paper16_m0'
            for name in ['results','work','metadata']:(p/name).mkdir(parents=True,exist_ok=True)
            stamp=datetime.datetime(2020,1,1,tzinfo=datetime.timezone.utc)
            n=NWBFile('synthetic only','1',stamp,timestamps_reference_time=stamp)
            n.add_unit_column('peak_channel_id','synthetic peak channel')
            for uid in range(1,10):n.add_unit(id=uid,spike_times=np.array([.1,.15,1.]) if uid<=8 else np.array([float('nan')]),peak_channel_id=10)
            table=TimeIntervals(name='drifting_gratings_presentations',description='synthetic')
            table.add_column('orientation','synthetic two conditions')
            for i in range(32):table.add_interval(id=100+i,start_time=float(i),stop_time=float(i)+.8,orientation=float((i%2)*90))
            n.add_time_intervals(table)
            bad=TimeIntervals(name='invalid_times',description='synthetic other probe')
            bad.add_column('tags','scope',index=True);bad.add_interval(start_time=.2,stop_time=.3,tags=['EcephysProbe','probeB']);n.invalid_times=bad
            path=p/'work/session_1.nwb'
            with NWBHDF5IO(str(path),'w') as io:io.write(n)
            import h5py
            with h5py.File(path,'r') as h:version=str(h.attrs['nwb_version'])
            role={'session_id':1,'mouse_id':'1','probe_id':1,'probe_name':'probeA','session_type':'synthetic','group':'Development','qualified_unit_ids':list(range(1,9)),'fail_eye_tracking':True}
            dump_json(p/'results/ROLE_ALLOCATION.json',[role]);dump_json(p/'results/PILOT_METADATA_SELECTION.json',[role]);dump_json(p/'results/PILOT_OBJECT_FREEZE.json',{'objects':[role]})
            dump_json(p/'metadata/channels.body',{'msg':[{'id':10,'ecephys_probe_id':1,'structure_acronym':'VISp'}]})
            dump_json(p/'metadata/source_unit_qc.body',{'msg':[{'id':u,'ecephys_channel_id':10} for u in range(1,9)]})
            dump_json(p/'metadata/probes.body',{'msg':[{'id':1,'name':'probeA','ecephys_session_id':1},{'id':2,'name':'probeB','ecephys_session_id':1},{'id':3,'name':'probeB','ecephys_session_id':2}]})
            dump_json(p/'results/TRANSFER_1.json',{'status':'COMPLETE','sha256':sha256(path)})
            self.approval(root);seen=[];original=VectorIndex.__getitem__
            def traced(obj,item,*args,**kwargs):
                if obj.target.name=='spike_times':seen.append(item)
                return original(obj,item,*args,**kwargs)
            with patch.multiple(reader,P=p,R=root,E=root/E,EXPECTED_NWB_VERSION=version),patch.multiple(transfer,P=p,R=root,E=root/E),patch.object(VectorIndex,'__getitem__',traced):
                reader.main()
                with self.assertRaises(FileExistsError):reader.main()
            result=read_json(p/'results/PILOT_1.json')
            self.assertEqual(seen,list(range(8)))
            self.assertTrue(result['event_binary64_roundtrip_pass']);self.assertTrue(result['coverage_gate'])
            self.assertEqual(result['invalid_intervals_applied'],[])
            self.assertFalse(result['behavior']['running']['available']);self.assertFalse(result['behavior']['pupil']['available'])
            self.assertGreater(result['true_zero_bins'],0)
            self.assertEqual(result['selected_unit_ids'],list(range(1,9)))
            self.assertEqual(result['families'][0]['condition_columns'],['orientation'])
            self.assertEqual(sum(x['n'] for x in result['families'][0]['condition_values_and_repetitions']),32)
            # Synthetic current schema is explicitly distinct from unexecuted real NWB2.2.2 compatibility.
            self.assertEqual(result['nwb_version'],version)

if __name__=='__main__':unittest.main()
