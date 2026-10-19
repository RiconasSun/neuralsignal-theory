"""Owned synthetic HTTP/cache inputs only; network disabled in every test."""
import copy
import datetime
import hashlib
import io
import json
from pathlib import Path
import tempfile
import time
import unittest
from unittest.mock import patch
import urllib3
from .core import P,R,load,SourceStop,ResourceStop
from .transport import Journal,Transport,RangeReader


def stage(seconds=120):
    now=time.monotonic();utc=datetime.datetime.now(datetime.timezone.utc)
    return {'start_monotonic':now,'deadline_monotonic':now+seconds,'start_UTC':utc.isoformat(),
            'deadline_UTC':(utc+datetime.timedelta(seconds=seconds)).isoformat(),'no_reset':True,'windows_boot_UTC':'SYNTHETIC'}


class Response:
    def __init__(self,data,offset,length,item,status=206):
        self.status_code=status;self.headers={'ETag':item['etag'],'Content-Range':f'bytes {offset}-{offset+length-1}/{item["size"]}',
            'Content-Length':str(length)};self.raw=io.BytesIO(data)
    def __enter__(self):return self
    def __exit__(self,*a):return False


class TimeoutBody:
    def __init__(self,partial=b'part'):self.partial=partial;self.first=True
    def read(self,n):
        if self.first:self.first=False;return self.partial
        raise urllib3.exceptions.ReadTimeoutError(None,None,'SYNTHETIC timeout')


class TransportTests(unittest.TestCase):
    def setUp(self):
        base=P/'work/private';base.mkdir(parents=True,exist_ok=True)
        self.temp=tempfile.TemporaryDirectory(dir=base,prefix='synthetic-r4-');self.root=Path(self.temp.name)
        self.reg=load(P/'ACCESS_REGISTRATION.json');self.item=copy.deepcopy(self.reg['objects'][3]);self.item['size']=100
        self.reg['objects'][3]=self.item
        self.reg['resources'].update({'per_request_bytes_max':32,'logical_read_bytes_max':100,
            'aggregate_reserved_bytes_max':1000,'per_source_reserved_bytes_max':1000})
        prefix=self.root/'original_prefix.bin';prefix.write_bytes(b'1234567')
        self.reg['recovery'].update({'old_offset':0,'old_length':32,'prefix_length':7,'prefix_path':prefix.relative_to(R).as_posix(),
            'prefix_sha256':hashlib.sha256(b'1234567').hexdigest(),'suffix_offset':7,'suffix_length':25,'backoff_seconds':0})
        self.patches=[patch('paper16_source_r4.transport.P',self.root),patch('paper16_source_r4.transport.S',self.root/'history'),
                      patch('socket.socket.connect',side_effect=AssertionError('No real network in synthetic test'))]
        for p in self.patches:p.start()
        self.journal=Journal(self.root/'journal.jsonl',self.reg);self.t=Transport(self.item,self.reg,stage(),self.journal)
    def tearDown(self):
        self.t.close();self.journal.close()
        for p in reversed(self.patches):p.stop()
        self.temp.cleanup()
    def response(self,data=None,offset=7,length=25):return Response(b'x'*length if data is None else data,offset,length,self.item)
    def get(self,**kwargs):return patch('requests.Session.get',**kwargs)

    def test_suffix_exact_reconstruction_preserves_original_and_reader_offsets(self):
        prefix=(self.root/'original_prefix.bin').read_bytes();suffix=b'x'*25
        with self.get(return_value=self.response(suffix)) as call:receipt=self.t.recover_historical()
        self.assertEqual(call.call_args.kwargs['headers']['Range'],'bytes=7-31');self.assertEqual(call.call_count,1)
        self.assertEqual((self.root/'original_prefix.bin').read_bytes(),prefix)
        self.assertEqual(receipt['sha256'],hashlib.sha256(prefix+suffix).hexdigest())
        with self.get(side_effect=AssertionError('Offline')):
            with RangeReader(self.t,offline=True) as reader:self.assertEqual(reader.read(32),prefix+suffix)
        self.assertEqual(self.journal.payload,25)

    def test_corrupt_saved_prefix_rejected_before_any_request(self):
        (self.root/'original_prefix.bin').write_bytes(b'corrupt')
        with self.get(side_effect=AssertionError('No network')):
            with self.assertRaises(SourceStop):self.t.recover_historical()
        self.assertEqual(self.journal.reserved,0)

    def test_offset_overlap_and_gap_rejected_before_request(self):
        for shift in [-1,1]:
            with self.subTest(shift=shift),self.get(side_effect=AssertionError('No network')):
                self.reg['recovery']['suffix_offset']=7+shift
                with self.assertRaises(SourceStop):self.t.recover_historical()
        self.assertEqual(self.journal.reserved,0)

    def test_wrong_etag_range_status_or_length_denied_without_body_or_retry(self):
        for key,value in [('ETag','wrong'),('Content-Range','bytes 6-30/100'),('status',200),('Content-Length','24')]:
            with self.subTest(key=key):
                response=self.response()
                if key=='status':response.status_code=value
                else:response.headers[key]=value
                with self.get(return_value=response) as call:
                    with self.assertRaises(SourceStop):self.t.download(7,25)
                self.assertEqual(call.call_count,1);self.assertEqual(response.raw.tell(),0)

    def test_clean_partial_response_is_preserved_and_not_accepted_or_retried(self):
        with self.get(return_value=self.response(b'short')) as call:
            with self.assertRaises(SourceStop):self.t.download(7,25)
        self.assertEqual(call.call_count,1);self.assertEqual(self.journal.payload,5)
        self.assertEqual((self.root/'work/private/http_attempts'/str(self.item['session_id'])/'00001.bin').read_bytes(),b'short')

    def test_one_timeout_exact_second_range_and_both_attempts_are_preserved(self):
        first=self.response();first.raw=TimeoutBody()
        with self.get(side_effect=[first,self.response()]) as call:body,_=self.t.download(7,25)
        self.assertEqual(body,b'x'*25);self.assertEqual(call.call_count,2)
        self.assertEqual([c.kwargs['headers']['Range'] for c in call.call_args_list],['bytes=7-31']*2)
        self.assertEqual(self.journal.payload,29);self.assertEqual(self.journal.recovery_slots,1)
        self.assertEqual(sum(x['event']=='RECOVERED_R4_TIMEOUT' for x in self.journal.events),1)
        self.assertEqual(len(list((self.root/'work/private/http_attempts').rglob('*.bin'))),2)

    def test_two_timeouts_exhaust_two_requests_without_third_or_refund(self):
        responses=[self.response(),self.response()]
        for response in responses:response.raw=TimeoutBody()
        with self.get(side_effect=responses) as call:
            with self.assertRaises(urllib3.exceptions.ReadTimeoutError):self.t.download(7,25)
        self.assertEqual(call.call_count,2);self.assertEqual(self.journal.recovery_slots,1)
        self.assertFalse(any(x['event']=='COMPLETE_HTTP_BODY' for x in self.journal.events))

    def test_recovery_per_source_and_global_caps_deny_second_request(self):
        for field in ['new_timeout_recovery_slots_per_source_max','new_timeout_recovery_slots_global_max']:
            response=self.response();response.raw=TimeoutBody();self.reg['recovery'][field]=0
            with self.subTest(field=field),self.get(return_value=response) as call:
                with self.assertRaises(ResourceStop):self.t.download(7,25)
                self.assertEqual(call.call_count,1)
            self.reg['recovery'][field]=2 if 'per_source' in field else 6

    def test_resource_caps_and_oversized_request_deny_before_network(self):
        for field in ['aggregate_reserved_bytes_max','per_source_reserved_bytes_max','per_source_requests_max']:
            before=self.reg['resources'][field];self.reg['resources'][field]=0
            with self.subTest(field=field),self.get(side_effect=AssertionError('No network')):
                with self.assertRaises(ResourceStop):self.t.download(7,25)
            self.reg['resources'][field]=before
        with self.get(side_effect=AssertionError('No network')):
            with self.assertRaises(ResourceStop):self.t.download(0,33)
        self.assertEqual(self.journal.reserved,0)

    def test_HEAD_is_one_non_neural_request_exact_identity_no_body(self):
        response=self.response();response.status_code=200;response.headers={'ETag':self.item['etag'],'Content-Length':'100'}
        with patch('requests.Session.head',return_value=response) as call:self.t.head()
        self.assertEqual(call.call_count,1);self.assertEqual(response.raw.tell(),0)
        self.assertEqual(self.journal.payload,0);self.assertEqual(self.journal.by_source[self.item['session_id']]['requests'],1)

    def test_HEAD_identity_mismatch_stops_without_GET_fallback(self):
        response=self.response();response.status_code=200;response.headers={'ETag':'changed','Content-Length':'100'}
        with patch('requests.Session.head',return_value=response) as head,self.get(side_effect=AssertionError('No GET')):
            with self.assertRaises(SourceStop):self.t.head()
            self.assertEqual(head.call_count,1)

    def test_Final_altered_source_and_completed_R3_sources_denied(self):
        bad=dict(self.item,session_id=self.reg['denied_final_session_ids'][0])
        for item in [bad,dict(self.item,file_id='changed'),self.reg['objects'][0]]:
            with self.subTest(item=item['session_id']):
                with self.assertRaises(SourceStop):Transport(item,self.reg,stage(),self.journal)

    def test_cache_tamper_offline_missing_and_historical_partial_no_fallback(self):
        with RangeReader(self.t,offline=True) as reader:
            with self.assertRaises(SourceStop):reader.read(1)
        with self.get(return_value=self.response()):self.t.recover_historical()
        path=self.root/'work/private/ranges'/str(self.item['session_id'])/'0.bin';path.write_bytes(b'z'*32)
        with RangeReader(self.t,offline=True) as reader:
            with self.assertRaises(SourceStop):reader.read(1)

    def test_append_journal_restores_retry_byte_request_counters(self):
        response=self.response();response.raw=TimeoutBody()
        with self.get(side_effect=[response,self.response()]):self.t.download(7,25)
        self.journal.close();other=Journal(self.root/'journal.jsonl',self.reg,append=True)
        self.assertEqual(other.payload,29);self.assertEqual(other.reserved,52);self.assertEqual(other.recovery_slots,1)
        self.assertEqual(other.by_source[self.item['session_id']]['requests'],2);other.close()

    def test_exact_two_per_source_and_six_global_slot_boundaries(self):
        for item in self.reg['objects'][3:6]:
            self.journal.reserve(item,'GET',0,1,1)
            self.journal.retry_slot(item,0,1);self.journal.retry_slot(item,32,1)
        self.assertEqual(self.journal.recovery_slots,6)
        with self.assertRaises(ResourceStop):self.journal.retry_slot(self.item,64,1)
        other=self.reg['objects'][6];self.journal.reserve(other,'GET',0,1,1)
        with self.assertRaises(ResourceStop):self.journal.retry_slot(other,0,1)


if __name__=='__main__':unittest.main(verbosity=2)
