import io
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import time
import unittest
from unittest import mock
import h5py
import numpy as np
from .links import Inspector, LinkProblem, ALIAS, EXPECTED, normalized_target, no_dataset_values
from .inspect_source import MetadataRangeReader, Journal, ResourceLimit, validate_source, supervise
from .saved_ranges import SavedRangeReader, MissingSavedRange

PATHS = ['/processing','/processing/running','/processing/running/running_wheel_rotation',
         '/processing/running/running_wheel_rotation/data',ALIAS,'/processing/running/running_speed',EXPECTED,
         '/processing/running/running_speed_end_times','/processing/running/running_speed_end_times/timestamps']
WORK=Path(__file__).parent/'work'


def fixture(name, kind='soft'):
    f=h5py.File(name,'w',driver='core',backing_store=False)
    f.attrs['nwb_version']='2.2.2';f.attrs['namespace']='core';f.attrs['neurodata_type']='NWBFile'
    ts=f.create_dataset(EXPECTED,data=np.array([1.,2.]));ts.attrs['unit']='seconds'
    end=f.create_dataset('/processing/running/running_speed_end_times/timestamps',data=np.array([1.01,2.01]));end.attrs['unit']='seconds'
    data=f.create_dataset('/processing/running/running_wheel_rotation/data',data=np.array([.01,.02]));data.attrs['unit']='radians';data.attrs['conversion']=1.;data.attrs['offset']=0.
    if kind=='soft':f[ALIAS]=h5py.SoftLink(EXPECTED)
    if kind=='hard':f[ALIAS]=ts
    if kind=='relative':f[ALIAS]=h5py.SoftLink('../running_speed/timestamps')
    if kind=='external':f[ALIAS]=h5py.ExternalLink('NEVER_OPEN_EXTERNAL.nwb',EXPECTED)
    if kind=='selfcycle':f[ALIAS]=h5py.SoftLink(ALIAS)
    if kind=='twocycle':
        f[ALIAS]=h5py.SoftLink(EXPECTED);del f[EXPECTED];f[EXPECTED]=h5py.SoftLink(ALIAS)
    if kind=='neural':f[ALIAS]=h5py.SoftLink('/units/spike_times')
    if kind=='unexpected':f[ALIAS]=h5py.SoftLink('/processing/running/running_wheel_rotation/data')
    return f


class Response:
    def __init__(self,status=206,etag='fixed',body=b'1234',content_range='bytes 0-3/100'):
        self.status_code=status;self.headers={'ETag':etag,'Content-Range':content_range};self.raw=io.BytesIO(body)
    def __enter__(self):return self
    def __exit__(self,*a):pass


class HTTP:
    def __init__(self,response):self.response=response;self.calls=0
    def get(self,*a,**kw):self.calls+=1;return self.response
    def close(self):pass


class Tests(unittest.TestCase):
    def test_legitimate_internal_absolute_alias_metadata_identity_without_values(self):
        with tempfile.TemporaryDirectory(dir=WORK) as tmp, fixture(str(Path(tmp)/'fixture.h5')) as f:
            with no_dataset_values() as counts:
                i=Inspector(f);result=i.run(PATHS)
                self.assertEqual(result['status'],'INTERNAL_LINK_METADATA_COMPATIBLE')
                self.assertEqual(result['failed_component'],ALIAS);self.assertEqual(result['actual_link_class'],'SoftLink')
                self.assertEqual(result['literal_target'],EXPECTED);self.assertTrue(result['expected_object_match'])
                self.assertEqual(result['alias_object_address'],result['expected_object_address'])
                self.assertFalse(result['same_row_numeric_timing_validated']);self.assertEqual(counts['forbidden_value_calls'],0)

    def test_hard_link_metadata_safe_but_does_not_reproduce_old_failure(self):
        with tempfile.TemporaryDirectory(dir=WORK) as tmp, fixture(str(Path(tmp)/'fixture.h5'),'hard') as f, no_dataset_values():
            i=Inspector(f);a=i.inspect(ALIAS);b=i.inspect(EXPECTED)
            self.assertEqual(h5py.h5o.get_info(a.id).addr,h5py.h5o.get_info(b.id).addr)
            with self.assertRaises(LinkProblem) as c:i.run(PATHS)
            self.assertEqual(c.exception.kind,'UNRESOLVED')

    def test_missing_each_component_and_unexpected_parent(self):
        with tempfile.TemporaryDirectory(dir=WORK) as tmp:
            for missing in ['/processing','/processing/running','/processing/running/running_wheel_rotation',ALIAS]:
                with fixture(str(Path(tmp)/'fixture.h5')) as f:
                    del f[missing]
                    with no_dataset_values():
                        i=Inspector(f)
                        with self.assertRaises(LinkProblem) as c:i.inspect(ALIAS)
                        self.assertEqual(c.exception.kind,'MISSING');self.assertEqual(c.exception.path,missing)
                        self.assertFalse(i.rows[-1]['existence'])
            with fixture(str(Path(tmp)/'fixture.h5')) as f:
                del f['/processing/running'];f.create_dataset('/processing/running',data=np.ones(1))
                with no_dataset_values():
                    i=Inspector(f)
                    with self.assertRaises(LinkProblem) as c:i.inspect(ALIAS)
                    self.assertEqual(c.exception.kind,'SCHEMA')

    def test_external_neural_unexpected_and_cycles_block_before_dereference(self):
        with tempfile.TemporaryDirectory(dir=WORK) as tmp:
            for kind in ['external','neural','unexpected','selfcycle','twocycle']:
                with fixture(str(Path(tmp)/'fixture.h5'),kind) as f, no_dataset_values():
                    original=h5py.Group.__getitem__
                    def hard_only(group,name):
                        if name=='/' and isinstance(group,h5py.File):
                            return original(group,name)
                        link=group.get(name,getlink=True)
                        if isinstance(link,(h5py.SoftLink,h5py.ExternalLink)):
                            raise AssertionError('Blind unsafe link dereference')
                        return original(group,name)
                    with mock.patch.object(h5py.Group,'__getitem__',hard_only):
                        i=Inspector(f)
                        with self.assertRaises(LinkProblem) as c:i.inspect(ALIAS)
                        self.assertIn(c.exception.kind,['UNSAFE','CYCLE'])
                        self.assertTrue(any(x['literal_target'] is not None for x in i.rows))

    def test_relative_literal_and_candidate_kept_distinct_no_unproven_equivalence(self):
        with tempfile.TemporaryDirectory(dir=WORK) as tmp, fixture(str(Path(tmp)/'fixture.h5'),'relative') as f, no_dataset_values():
            self.assertEqual(normalized_target('/processing/running/running_wheel_rotation','../running_speed/timestamps'),EXPECTED)
            i=Inspector(f)
            with self.assertRaises(LinkProblem) as c:i.inspect(ALIAS)
            self.assertEqual(c.exception.kind,'UNRESOLVED');self.assertEqual(i.rows[-1]['literal_target'],'../running_speed/timestamps')
            self.assertEqual(i.rows[-1]['normalized_candidate'],EXPECTED)
            self.assertNotIn('resolved_metadata',i.rows[-1])
            self.assertTrue(i.rows[-1]['expected_target_path_match'])
            self.assertIsNone(i.rows[-1]['expected_object_match'])
            self.assertIsNone(i.rows[-1]['points_inside_same_file'])

    def test_forbidden_logical_path_denied_before_lookup_and_numeric_canaries(self):
        with tempfile.TemporaryDirectory(dir=WORK) as tmp, fixture(str(Path(tmp)/'fixture.h5')) as f:
            i=Inspector(f)
            with mock.patch.object(h5py.Group,'get',side_effect=AssertionError('Lookup forbidden')):
                with self.assertRaises(LinkProblem):i.inspect('/units/spike_times')
            dataset=f[EXPECTED]
            with no_dataset_values() as count:
                for fn in [lambda:dataset[:],lambda:dataset[()],lambda:np.asarray(dataset),lambda:iter(dataset),lambda:dataset.read_direct(np.empty(2))]:
                    with self.assertRaises(RuntimeError):fn()
                self.assertEqual(count['forbidden_value_calls'],5)

    def test_shape_match_alone_not_identity_and_schema_metadata_contradictions(self):
        with tempfile.TemporaryDirectory(dir=WORK) as tmp:
            for failure in ['independent_timestamp','unit','shape','dtype']:
                with fixture(str(Path(tmp)/'fixture.h5')) as f:
                    if failure=='independent_timestamp':
                        del f[ALIAS];f.create_dataset(ALIAS,data=np.array([1.,2.]))
                    if failure=='unit':f['/processing/running/running_wheel_rotation/data'].attrs['unit']='degrees'
                    if failure=='shape':
                        path='/processing/running/running_speed_end_times/timestamps';del f[path];f.create_dataset(path,data=np.ones(3))
                    if failure=='dtype':
                        path='/processing/running/running_speed_end_times/timestamps';del f[path];f.create_dataset(path,data=np.ones(2,dtype='float32'))
                    with no_dataset_values():
                        with self.assertRaises(LinkProblem):Inspector(f).run(PATHS)

    def test_target_source_identity_rejects_other_session_or_version(self):
        item={'session_id':750749662,'mouse_id':'726162197','role':'Development','etag':'fixed'};reg={'source':item}
        validate_source(item,reg)
        for change in [{'session_id':1},{'mouse_id':'wrong'},{'role':'Final_candidate'},{'etag':'wrong'}]:
            with self.assertRaises(ValueError):validate_source({**item,**change},reg)

    def make_reader(self,response,path):
        journal=Journal(path);r=MetadataRangeReader({'size':100,'file_id':'synthetic','etag':'fixed'},time.monotonic()+10,journal)
        r.http.close();r.http=HTTP(response);return r,journal

    def test_HTTP_exact_ranges_identity_cache_body_accounting_no_bulk(self):
        with tempfile.TemporaryDirectory(dir=WORK) as tmp:
            r,j=self.make_reader(Response(),Path(tmp)/'ok.jsonl')
            self.assertEqual(r.read(4),b'1234');r.seek(0);self.assertEqual(r.read(4),b'1234')
            self.assertEqual((r.calls,r.used,r.reserved),(1,4,5));j.close()
            events=[json.loads(x) for x in (Path(tmp)/'ok.jsonl').read_text().splitlines()]
            self.assertEqual(sum(x['bytes'] for x in events if x['event']=='PAYLOAD'),4)
            for k,response in enumerate([Response(status=200),Response(etag='changed'),Response(content_range='bytes 1-4/100'),Response(body=b'bad')]):
                r,j=self.make_reader(response,Path(tmp)/f'bad{k}.jsonl')
                with self.assertRaises(RuntimeError):r.read(4)
                self.assertEqual(r.http.calls,1);j.close()

    def test_budget_deadline_cache_and_stream_interruption_journal(self):
        with tempfile.TemporaryDirectory(dir=WORK) as tmp:
            for k,limit in enumerate(['calls','bytes','time']):
                r,j=self.make_reader(Response(),Path(tmp)/f'limit{k}.jsonl')
                if limit=='calls':r.calls=128
                if limit=='bytes':r.reserved=8388604
                if limit=='time':r.deadline=time.monotonic()-1
                with self.assertRaises(ResourceLimit):r.read(4)
                self.assertEqual(r.http.calls,0);j.close()
            r,j=self.make_reader(Response(),Path(tmp)/'cache.jsonl');r.read(4);r.seek(0);r.deadline=time.monotonic()-1
            with self.assertRaises(ResourceLimit):r.read(4)
            j.close()
            class Interrupted:
                def __init__(self):self.n=0
                def read(self,n):
                    self.n+=1
                    if self.n==1:return b'12'
                    raise OSError('Synthetic interruption')
            response=Response();response.raw=Interrupted();r,j=self.make_reader(response,Path(tmp)/'partial.jsonl')
            with self.assertRaises(OSError):r.read(4)
            self.assertEqual((r.calls,r.used,r.reserved,len(r.ranges)),(1,2,5,0));j.close()

    def test_external_watchdog_and_duplicate_attempt_no_second_child(self):
        with tempfile.TemporaryDirectory(dir=WORK) as tmp:
            slow=Path(tmp)/'slow';slow.mkdir();target=slow/'SUPERVISION.json'
            self.assertEqual(supervise([sys.executable,'-c','import time; time.sleep(60)'],.1,target),124)
            self.assertFalse(json.loads(target.read_text())['valid_completed_inspection'])
            with mock.patch('subprocess.Popen',side_effect=AssertionError('Duplicate child forbidden')):
                with self.assertRaises(FileExistsError):supervise([sys.executable,'-c','pass'],3,target)
            fast=Path(tmp)/'fast';fast.mkdir();target=fast/'SUPERVISION.json'
            self.assertEqual(supervise([sys.executable,'-c','pass'],3,target),0)
            self.assertTrue(json.loads(target.read_text())['valid_completed_inspection'])

    def test_compatibility_rejects_unit_scaling_parent_and_capacity_contradictions(self):
        with tempfile.TemporaryDirectory(dir=WORK) as tmp:
            for path in [EXPECTED,'/processing/running/running_speed_end_times/timestamps']:
                for field,value in [('unit','milliseconds'),('unit','unknown'),('conversion',1000.),('offset',.1)]:
                    with fixture(str(Path(tmp)/'fixture.h5')) as f:
                        f[path].attrs[field]=value
                        with no_dataset_values(),self.assertRaises(LinkProblem) as c:Inspector(f).run(PATHS)
                        self.assertEqual(c.exception.kind,'UNRESOLVED' if value=='unknown' else 'SCHEMA')
            with fixture(str(Path(tmp)/'fixture.h5')) as f:
                del f[EXPECTED].attrs['unit']
                with no_dataset_values(),self.assertRaises(LinkProblem) as c:Inspector(f).run(PATHS)
                self.assertEqual(c.exception.kind,'UNRESOLVED')
            with fixture(str(Path(tmp)/'fixture.h5')) as f:
                f['/processing/running/running_wheel_rotation'].attrs['unit']='degrees'
                with no_dataset_values(),self.assertRaises(LinkProblem):Inspector(f).run(PATHS)
            for n in [0,2000001]:
                with fixture(str(Path(tmp)/'fixture.h5')) as f:
                    for path in [EXPECTED,'/processing/running/running_speed_end_times/timestamps','/processing/running/running_wheel_rotation/data']:
                        del f[path];ds=f.create_dataset(path,shape=(n,),dtype='float64');ds.attrs['unit']='radians' if path.endswith('/data') else 'seconds'
                    with no_dataset_values(),self.assertRaises(LinkProblem) as c:Inspector(f).run(PATHS)
                    self.assertEqual(c.exception.kind,'SCHEMA')
            # A TimeSeries velocity unit is a different quantity from timestamp units.
            with fixture(str(Path(tmp)/'fixture.h5')) as f:
                f['/processing/running/running_speed'].attrs['unit']='cm/s'
                with no_dataset_values():self.assertEqual(Inspector(f).run(PATHS)['status'],'INTERNAL_LINK_METADATA_COMPATIBLE')

    def test_saved_metadata_payload_redecode_without_network_or_values(self):
        with tempfile.TemporaryDirectory(dir=WORK) as tmp:
            with fixture(str(Path(tmp)/'fixture.h5')) as f:
                f.flush();image=f.id.get_file_image()  # Synthetic file only.
            payload=Path(tmp)/'image.bin';payload.write_bytes(image)
            row={'payload_path':'image.bin','offset':0,'bytes':len(image),'sha256':hashlib.sha256(image).hexdigest()}
            source=SavedRangeReader(tmp,len(image),[row])
            with h5py.File(source,'r') as f,no_dataset_values():
                result=Inspector(f).run(PATHS)
                self.assertEqual(result['status'],'INTERNAL_LINK_METADATA_COMPATIBLE')
            with self.assertRaises(MissingSavedRange):SavedRangeReader(tmp,len(image),[]).read(8)
            with self.assertRaises(ValueError):SavedRangeReader(tmp,len(image),[{**row,'sha256':'0'*64}])
            with self.assertRaises(ValueError):SavedRangeReader(tmp,len(image),[{**row,'payload_path':'../image.bin'}])

    def test_completed_range_retention_and_immutable_pending_snapshot(self):
        with tempfile.TemporaryDirectory(dir=WORK) as tmp:
            j=Journal(Path(tmp)/'ranges.jsonl');directory=Path(tmp)/'payload'
            r=MetadataRangeReader({'size':100,'file_id':'synthetic','etag':'fixed'},time.monotonic()+10,j,directory)
            r.http.close();r.http=HTTP(Response());self.assertEqual(r.read(4),b'1234');j.close()
            self.assertEqual((directory/'META_RANGE_0001.bin').read_bytes(),b'1234')
            self.assertIn('payload_path',r.ranges[0])
            with fixture(str(Path(tmp)/'fixture.h5')) as f,no_dataset_values():
                i=Inspector(f);i.run(PATHS);rows=[x for x in i.rows if x['path']==ALIAS and x['link_class']=='SoftLink']
                self.assertIsNone(rows[0]['expected_object_match']);self.assertTrue(rows[1]['expected_object_match'])


if __name__=='__main__':unittest.main()
