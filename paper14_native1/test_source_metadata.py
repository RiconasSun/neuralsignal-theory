"""Synthetic metadata canaries and HTTP range/integrity tests before source use."""
import copy,io,json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import h5py
import numpy as np
from . import source_metadata as m

def fixture():
    b=io.BytesIO()
    with h5py.File(b,'w') as f:
        f['general/subject/subject_id']='TEST'
        f['units/id']=[0,1];f['units/probe_name']=np.array(['Probe00','Probe00'],dtype=h5py.string_dtype());f['units/ibl_quality_score']=[1.,0.]
        f['units/max_electrode']=[0,1];f['units/cluster_uuid']=np.array(['uuid1','uuid2'],dtype=h5py.string_dtype())
        f['general/extracellular_ephys/electrodes/location']=np.array(['MOs5','PL6a'],dtype=h5py.string_dtype())
        f['intervals/trials/probability_left']=[.2,.8];f['intervals/trials/start_time']=[0.,3.]
        f['units/spike_times']=[777.,888.];f['units/spike_times_index']=[1,2];f['units/spike_count']=[999,111]
        f['units/firing_rate']=[88.,99.];f['acquisition/wheel/data']=[12345.]
    b.seek(0);return b

class Response:
    def __init__(self,url,headers,*,status=206,wrong_range=False,etag='"frozen"',truncate=False):
        self.url=url;self.history=[];self.status_code=status;start,end=map(int,headers['Range'][6:].split('-'));self.data=bytes(i%256 for i in range(start,end+1))
        self.headers={'ETag':etag,'Content-Range':f'bytes {start}-{end}/{self.size}'}
        if wrong_range:self.headers['Content-Range']='bytes 0-0/1'
        if truncate:self.data=self.data[:-1]
    def __enter__(self):return self
    def __exit__(self,*args):pass
    def close(self):pass
    def iter_content(self,*args):yield self.data
class Session:
    def __init__(self,size,**opts):self.size=size;self.opts=opts;self.calls=0
    def get(self,url,headers,**kw):
        self.calls+=1;Response.size=self.size;return Response(url,headers,**self.opts)

class MetadataTests(unittest.TestCase):
    def test_historical_inputs(self):self.assertEqual(m.verify_history(),772)
    def test_metadata_values_and_missingness_only(self):
        with h5py.File(fixture(),'r') as f:
            self.assertEqual(m.value(f,'/units/probe_name'),['Probe00','Probe00']);self.assertEqual(m.value(f,'/intervals/trials/probability_left'),[.2,.8])
    def test_neural_rawbehavior_and_arbitrary_values_denied(self):
        with h5py.File(fixture(),'r') as f:
            for p in ['/units/spike_times','/units/spike_times_index','/units/spike_count','/units/firing_rate','/acquisition/wheel/data']:
                with self.assertRaises(PermissionError):m.value(f,p)
    def test_schema_never_opens_neural_datasets_or_shapes(self):
        old=m.hard;calls=[]
        def guarded(f,p):
            calls.append(p)
            if p in ['/units/spike_times','/units/spike_times_index','/units/spike_count','/units/firing_rate']:raise AssertionError('Protected dataset opened')
            return old(f,p)
        with h5py.File(fixture(),'r') as f,patch.object(m,'hard',side_effect=guarded):
            rows=m.schema(f)
        for r in rows:
            if r['path']=='/units/spike_times':self.assertFalse(r['opened']);self.assertNotIn('shape',r)
        self.assertNotIn('/units/spike_times',calls)
    def test_soft_external_links_fail_closed(self):
        b=io.BytesIO()
        with h5py.File(b,'w') as f:f['units/probe_name']=h5py.ExternalLink('never','secret')
        with h5py.File(b,'r') as f:
            with self.assertRaises(ValueError):m.value(f,'/units/probe_name')
    def test_oversized_metadata_rejected(self):
        b=io.BytesIO()
        with h5py.File(b,'w') as f:f['units/id']=np.zeros(100001,dtype='i1')
        with h5py.File(b,'r') as f:
            with self.assertRaises(ValueError):m.value(f,'/units/id')
    def run_range(self,check,**opts):
        with tempfile.TemporaryDirectory(dir=m.P/'work') as temp:
            root=Path(temp);root.joinpath('SOURCE_REGISTRATION.json').write_bytes((m.P/'SOURCE_REGISTRATION.json').read_bytes());root.joinpath('SOURCE_AUDIT_ROSTER.json').write_bytes((m.P/'SOURCE_AUDIT_ROSTER.json').read_bytes())
            record=m.read(root/'SOURCE_AUDIT_ROSTER.json')['records'][0];session=Session(record['asset']['size'],**opts)
            with patch.object(m,'P',root):reader=m.Ranges(record,session=session);check(reader,session,root)
    def test_exact_range_cache_and_seek(self):
        def check(r,s,p):
            self.assertEqual(r.read(8),bytes(range(8)));r.seek(0);self.assertEqual(r.read(8),bytes(range(8)));self.assertEqual(s.calls,1)
            r.seek(10);self.assertEqual(r.read(2),bytes([10,11]));self.assertEqual(s.calls,2)
        self.run_range(check)
    def test_unbounded_or_badseek_before_network(self):
        def check(r,s,p):
            with self.assertRaises(ValueError):r.read()
            with self.assertRaises(ValueError):r.seek(-1)
            with self.assertRaises(ValueError):r.read(1000001)
            self.assertEqual(s.calls,0)
        self.run_range(check)
    def test_bulk_response_denied_before_body(self):
        def check(r,s,p):
            with self.assertRaises(RuntimeError):r.read(8)
            self.assertEqual(s.calls,2)
            rows=[json.loads(t) for t in (p/'results/SOURCE_ACCESS.jsonl').read_text().splitlines()];self.assertTrue(all(x['bytes']==0 for x in rows))
        self.run_range(check,status=200)
    def test_wrong_range_denied(self):
        def check(r,s,p):
            with self.assertRaises(RuntimeError):r.read(8)
        self.run_range(check,wrong_range=True)
    def test_truncated_range_denied(self):
        def check(r,s,p):
            with self.assertRaises(RuntimeError):r.read(8)
        self.run_range(check,truncate=True)
    def test_etag_change_denied(self):
        def check(r,s,p):
            r.read(8);s.opts['etag']='"changed"';r.seek(10)
            with self.assertRaises(RuntimeError):r.read(8)
        self.run_range(check)
    def test_corrupt_disk_cache_denied(self):
        def check(r,s,p):
            r.read(8);next(r.folder.glob('*.bin')).write_bytes(b'BAD');r.memory.clear();r.seek(0)
            with self.assertRaises(ValueError):r.read(8)
            self.assertEqual(s.calls,1)
        self.run_range(check)
    def test_unregistered_asset_denied(self):
        record=copy.deepcopy(m.read(m.P/'SOURCE_AUDIT_ROSTER.json')['records'][0]);record['asset']['asset_id']='unregistered'
        with self.assertRaises(PermissionError):m.Ranges(record,session=Session(10))
    def test_equal_length_wrong_offset_cache_swap_denied(self):
        def check(r,s,p):
            r.read(8);r.seek(10);r.read(8)
            (r.folder/'10_8.bin').write_bytes((r.folder/'0_8.bin').read_bytes())
            (r.folder/'10_8.json').write_bytes((r.folder/'0_8.json').read_bytes())
            r.memory.clear();r.seek(10)
            with self.assertRaises(ValueError):r.read(8)
            self.assertEqual(s.calls,2)
        self.run_range(check)
    def test_unapproved_redirect_not_contacted(self):
        def check(r,s,p):
            calls=[]
            def redirect(url,headers,**kw):
                calls.append(url);self.assertFalse(kw['allow_redirects'])
                response=Response(url,headers,status=302);response.headers['Location']='https://outside.example/secret';return response
            r.session.get=redirect
            with self.assertRaises(RuntimeError):r.read(8)
            self.assertEqual(len(calls),2);self.assertTrue(all('api.dandiarchive.org' in u for u in calls))
        self.run_range(check)
    def test_wrong_blob_redirect_not_contacted(self):
        def check(r,s,p):
            calls=[]
            def redirect(url,headers,**kw):
                calls.append(url);response=Response(url,headers,status=307);response.headers['Location']='https://dandiarchive.s3.amazonaws.com/blobs/not-this-asset';return response
            r.session.get=redirect
            with self.assertRaises(RuntimeError):r.read(8)
            self.assertEqual(len(calls),2)
        self.run_range(check)
    def test_every_http_hop_counts_toward_budget(self):
        def check(r,s,p):
            calls=[]
            blob=f"https://dandiarchive.s3.amazonaws.com/blobs/{r.asset['blob']}"
            def redirect(url,headers,**kw):
                calls.append(url);response=Response(url,headers,status=307 if 'api.dandiarchive.org' in url else 206)
                if response.status_code==307:response.headers['Location']=blob
                return response
            r.session.get=redirect;r.read(8)
            self.assertEqual(len(calls),2)
            rows=[json.loads(l) for l in (p/'results/SOURCE_HTTP_ACCESS.jsonl').read_text().splitlines()];self.assertEqual(len(rows),2)
        self.run_range(check)

if __name__=='__main__':
    (m.P/'work').mkdir(exist_ok=True)
    unittest.main()
