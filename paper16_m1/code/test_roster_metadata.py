import io,unittest,uuid
from pathlib import Path
import h5py,numpy as np
from .source_ranges import RangeReader
from .roster_metadata import read_meta,evaluate,invalid_rows,ALLOWED
class Response:
 def __init__(self,status=206,etag='fixed',body=b'1234',content_range='bytes 0-3/100'):
  self.status_code=status;self.headers={'ETag':etag,'Content-Range':content_range};self.raw=io.BytesIO(body)
 def __enter__(self):return self
 def __exit__(self,*args):pass
class HTTP:
 def __init__(self,response):self.response=response;self.calls=0
 def get(self,*args,**kwargs):self.calls+=1;return self.response
 def close(self):pass
class MetadataTests(unittest.TestCase):
 def test_invalid_tuple_order_identity_and_ragged_index_failclosed(self):
  item={'session_id':123,'probe_id':7};probes=[{'id':7,'name':'probeA'},{'id':8,'name':'probeB'}]
  self.assertEqual(invalid_rows([0],[1],['EcephysProbe','7','probeA'],[3],item,probes),[[0.,1.]])
  self.assertEqual(invalid_rows([0],[1],['EcephysProbe','8','probeB'],[3],item,probes),[])
  for tags in [['EcephysProbe','7'],['EcephysProbe','probeA'],['EcephysProbe','probeA','7'],['7','EcephysProbe','probeA'],['EcephysProbe','7','7'],['EcephysProbe','7','probeB'],['EcephysProbe','999','probeA'],['EcephysSession','all_probes','123'],['123','EcephysSession','all_probes']]:
   with self.subTest(tags=tags),self.assertRaises(ValueError):invalid_rows([0],[1],tags,[len(tags)],item,probes)
  for index in [[2.5],[4],[-1],[True]]:
   with self.subTest(index=index),self.assertRaises(ValueError):invalid_rows([0],[1],['EcephysProbe','7','probeA'],index,item,probes)
  with self.assertRaises(ValueError):invalid_rows([0,2],[1,3],['EcephysProbe','7','probeA'],[3,2],item,probes)
 def test_canonical_global_session_scope_and_wrong_identity(self):
  item={'session_id':123,'probe_id':7};probes=[{'id':7,'name':'probeA'}]
  self.assertEqual(invalid_rows([0],[1],['EcephysSession','123','all_probes'],[3],item,probes),[[0.,1.]])
  self.assertEqual(invalid_rows([0],[1],['EcephysSession','123','optotagging'],[3],item,probes),[[0.,1.]])
  for tags in [['EcephysSession','999','all_probes'],['EcephysSession','123','unknown'],['EcephysSession','all_probes']]:
   with self.assertRaises(ValueError):invalid_rows([0],[1],tags,[len(tags)],item,probes)
 def reader(self,res,maximum=100):
  r=RangeReader('https://example.invalid',100,maximum,'fixed');r.http.close();r.http=HTTP(res);return r
 def test_range_identity_budget_and_cache(self):
  r=self.reader(Response());self.assertEqual(r.read(4),b'1234');r.seek(0);self.assertEqual(r.read(4),b'1234');self.assertEqual(r.http.calls,1)
  self.assertEqual(r.reserved,5)
  r=self.reader(Response(),4)
  with self.assertRaises(RuntimeError):r.read(4)
  self.assertEqual(r.http.calls,0)
 def test_bulk_wrong_range_etag_truncated_failclosed(self):
  for res in [Response(status=200),Response(etag='altered'),Response(content_range='bytes 1-4/100'),Response(body=b'bad')]:
   r=self.reader(res)
   with self.subTest(res=res),self.assertRaises(RuntimeError):r.read(4)
  r=self.reader(Response());r.calls=256
  with self.assertRaises(RuntimeError):r.read(4)
 def test_no_neural_lookup_and_no_external_links(self):
  class Spy:
   def __getitem__(self,x):raise AssertionError('Lookup forbidden')
  for name in ['/units/spike_times','/acquisition/raw','/processing/running/running_speed/data']:
   with self.assertRaises(ValueError):read_meta(Spy(),name,[])
  work=Path(__file__).resolve().parents[1]/'work';work.mkdir(exist_ok=True)
  with h5py.File(str(work/(uuid.uuid4().hex+'.h5')),'w',driver='core',backing_store=False) as f:
   f.create_dataset('/identifier',data='synthetic');f['/session_start_time']=h5py.SoftLink('/identifier')
   self.assertEqual(read_meta(f,'/identifier',[]).item(),b'synthetic')
   with self.assertRaises(RuntimeError):read_meta(f,'/session_start_time',[])
 def test_synthetic_flash_coverage_invalid_late(self):
  a=np.arange(150,dtype=float)*2;b=a+.25;c=np.tile([-1.,1.],75)
  arrays={'start':a,'stop':b,'id':np.arange(150),'color':c}
  params={k:[v]*150 for k,v in {'contrast':.8,'opacity':1.,'phase':[0.,0.],'spatial_frequency':[0.,0.],'size':[300.,300.],'mask':None}.items()}
  facts,valid=evaluate(arrays,params,[]);self.assertTrue(facts['source_stimulus_compatible']);self.assertEqual(facts['per_role_color_valid']['A'],{'-1.0':45,'1.0':45})
  facts,valid=evaluate(arrays,params,[[.215,.22]]);self.assertFalse(valid[0]);self.assertEqual(facts['per_role_color_valid']['A']['-1.0'],44)
  self.assertFalse(evaluate(arrays,params,[],[[.235,.24]])[1][0])
  params['contrast']=[.1]*150;self.assertFalse(evaluate(arrays,params,[])[0]['source_stimulus_compatible'])
if __name__=='__main__':unittest.main()
