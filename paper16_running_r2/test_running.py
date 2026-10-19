"""Synthetic precision, restricted-source and bounded-stage regressions only."""
import contextlib
import io
import json
from pathlib import Path
import sys
import tempfile
import time
import unittest
from unittest.mock import patch
import h5py
import numpy as np

from .precision import native_arrays, derive, array_identity, admission_possible
from .reader import ALIAS,TARGET,ROT,END,SCALARS,resolve,native_running,value_scope
from .run_sources import BudgetJournal,RangeReader,ResourceStop,validate_source,supervise

WORK=Path(__file__).resolve().parent/'work';WORK.mkdir(exist_ok=True)


@contextlib.contextmanager
def fixture(path,kind='soft',rotation_dtype='<f4'):
    with h5py.File(path,'w',driver='core',backing_store=False) as f:
        f.attrs['nwb_version']='2.2.2'
        for name,value in zip(SCALARS,['750749662','clock0','clock0']):f.create_dataset(name,data=value)
        f.create_dataset(ROT,data=np.array([.1,-.2],dtype=rotation_dtype));f[ROT].attrs['unit']='radians';f[ROT].attrs['conversion']=1.
        f.create_dataset(TARGET,data=np.array([.1,.2],dtype='<f8'));f[TARGET].attrs['unit']='seconds'
        f.create_dataset(END,data=np.array([.15,.25],dtype='<f8'));f[END].attrs['unit']='seconds'
        f[ALIAS]=h5py.SoftLink(TARGET) if kind=='soft' else f[TARGET]
        yield f


def read_fixture(f,first=True):
    audit=[];reads=[];captured={}
    result=native_running(f,{'session_id':750749662},{SCALARS[1]:'clock0',SCALARS[2]:'clock0'},audit,reads,captured,first)
    return result,audit,reads,captured


def flash_fixture():
    onset=np.arange(150,dtype=np.float64)*2+100
    target=onset[:,None]+np.arange(5,11,dtype=np.float64)[None,:]*.02
    end=(target-.01).ravel();start=end-.01
    return start,end,np.full(900,.1,dtype=np.float32),onset,np.tile([-1.,1.],75),np.ones(150,dtype=bool)


class Response:
    def __init__(self,status=206,etag='fixed',content_range='bytes 0-3/100',body=b'abcd'):
        self.status_code=status;self.headers={'ETag':etag,'Content-Range':content_range};self.raw=io.BytesIO(body)
    def __enter__(self):return self
    def __exit__(self,*a):pass


class HTTP:
    def __init__(self,response):self.response=response;self.calls=0;self.kw=None
    def get(self,*a,**kw):self.calls+=1;self.kw=kw;return self.response
    def close(self):pass


class RunningTests(unittest.TestCase):
    def test_exact_float32_extremes_subnormal_signed_zero(self):
        x=np.array([0.,-0.,1.,-1.,np.nextafter(np.float32(0),np.float32(1)),np.finfo(np.float32).max,-np.finfo(np.float32).max],dtype='<f4')
        a=np.arange(len(x),dtype=np.float64);b=a+.05;before=[array_identity(z) for z in [a,b,x]]
        y,r=native_arrays(a,b,x,True)
        self.assertEqual(y.dtype,np.dtype('float64'));self.assertEqual(y.astype('<f4').tobytes(),x.tobytes())
        self.assertTrue(np.signbit(y[1]));self.assertTrue(r['float64_promotion_exact'])
        self.assertEqual(before,[array_identity(z) for z in [a,b,x]])

    def test_float64_rotation_preserved_and_first_dtype_fixed(self):
        a=np.array([1.,2.]);b=a+.05;x=np.array([.1,np.nextafter(.1,1.)])
        y,_=native_arrays(a,b,x);self.assertEqual(y.tobytes(),x.tobytes())
        with self.assertRaises(ValueError):native_arrays(a,b,x,True)

    def test_nonfinite_unsupported_order_correspondence_duration_rejected(self):
        a=np.array([1.,2.]);b=a+.05;x=np.array([.1,.2],dtype='<f4')
        for bad in [x.astype('float16'),x.astype('int32'),x.astype('>f4'),np.array([np.nan,.2],dtype='<f4'),np.array([np.inf,.2],dtype='<f4')]:
            with self.assertRaises(ValueError):native_arrays(a,b,bad)
        for one,two,rot in [(a.astype('float32'),b,x),(a,b.astype('float32'),x),(a,b[:1],x),(a[::-1],b,x),(a,b[::-1],x),(a,a.copy(),x),(a,np.array([np.inf,3.]),x)]:
            with self.assertRaises(ValueError):native_arrays(one,two,rot)

    def test_frozen_features_bits_masks_and_all_role_color_coverage(self):
        data=flash_fixture();start,end,rot,onset,color,valid=data;before=[z.tobytes() for z in [start,end,rot]]
        arrays,report=derive(*data,[],True)
        self.assertTrue(report['direct_running_coverage_pass']);self.assertTrue(report['potential_running_coverage_pass'])
        self.assertFalse(arrays['missing'].any());self.assertTrue((end[arrays['parent_original_row']]<arrays['targets']).all())
        np.testing.assert_array_equal(arrays['running_squared'],arrays['running']**2)
        np.testing.assert_array_equal(arrays['color_running'],color[:,None]*arrays['running'])
        self.assertEqual(before,[z.tobytes() for z in [start,end,rot]])
        for role,n in [('A',45),('B',15),('E',15)]:
            for c in ['-1.0','1.0']:self.assertEqual(report['coverage'][role][c]['presentations'],n)

    def test_strict_past_invalid_long_interval_and_removed_rows_missing(self):
        from paper16_dev.m2_core import running_features
        a=np.array([.1,.2,.4]);b=np.array([.15,.25,.6]);q=np.array([0.,.2,.3])
        r,m,p=running_features(a,b,q,np.array([.15,.16,.25,.26,.61]),[])
        self.assertTrue(m[0]);self.assertEqual(p[1],0);self.assertFalse(m[1]);self.assertEqual(r[1],0.)
        self.assertNotEqual(p[2],1);self.assertEqual(p[3],1);self.assertTrue(m[4])
        _,bad,_=running_features(a,b,q,np.array([.26]),[[.2,.24]]);self.assertTrue(bad[0])
        empty=np.array([],dtype=np.float64);_,gap,_=running_features(empty,empty,empty,np.array([.16]),[]);self.assertTrue(gap[0])

    def test_zero_rows_retained_and_float64_overflow_not_silently_saturated(self):
        data=list(flash_fixture());data[2][0]=np.float32(-0.)
        _,r=derive(*data,[],True);self.assertEqual(r['stored_zero_rows_retained'],1)
        data[2]=np.full(900,np.finfo(np.float64).max)
        with self.assertRaises(FloatingPointError):derive(*data,[])

    def test_valid_soft_and_hard_alias_exact_object_identity_and_reads(self):
        with tempfile.TemporaryDirectory(dir=WORK) as tmp:
            for kind in ['soft','hard']:
                with fixture(str(Path(tmp)/'f.h5'),kind) as f:
                    result,audit,reads,captured=read_fixture(f)
                    self.assertTrue(result['same_file_alias_identity'])
                    self.assertEqual(result['objects'][ALIAS]['address'],result['objects'][TARGET]['address'])
                    self.assertEqual(captured['rotation'].dtype,np.dtype('float32'))
                    self.assertEqual(set(reads),set((*SCALARS,ROT,TARGET,END)))

    def test_external_cycle_relative_spoofed_missing_and_dataset_parent_denied(self):
        with tempfile.TemporaryDirectory(dir=WORK) as tmp:
            for link in [h5py.ExternalLink('never_open.h5',TARGET),h5py.SoftLink(ALIAS),h5py.SoftLink('../running_speed/timestamps'),h5py.SoftLink('/units/spike_times'),h5py.SoftLink(TARGET+'/../timestamps')]:
                with fixture(str(Path(tmp)/'f.h5')) as f:
                    del f[ALIAS];f[ALIAS]=link
                    with self.assertRaises(ValueError):resolve(f,ALIAS,[])
            for path in ['/processing','/processing/running','/processing/running/running_wheel_rotation',ALIAS,TARGET]:
                with fixture(str(Path(tmp)/'f.h5')) as f:
                    del f[path]
                    with self.assertRaises(ValueError):resolve(f,ALIAS,[])
            with fixture(str(Path(tmp)/'f.h5')) as f:
                del f['/processing/running/running_wheel_rotation'];f.create_dataset('/processing/running/running_wheel_rotation',data=[1.])
                with self.assertRaises(ValueError):resolve(f,ROT,[])

    def test_unknown_path_neural_values_and_unrestricted_value_apis_denied(self):
        with tempfile.TemporaryDirectory(dir=WORK) as tmp,fixture(str(Path(tmp)/'f.h5')) as f:
            neural=f.create_dataset('/units/spike_times',data=[1.,2.])
            for path in ['/units/spike_times','/processing/running/running_speed/data']:
                with self.assertRaises(ValueError):resolve(f,path,[])
            allowed={int(h5py.h5o.get_info(f[ROT].id).addr):ROT}
            with value_scope(f,allowed,[]):
                with self.assertRaises(ValueError):neural[:]
                with self.assertRaises(ValueError):np.asarray(f[ROT])
                with self.assertRaises(ValueError):f[ROT].read_direct(np.empty(2))
                with self.assertRaises(ValueError):f[ROT][0]

    def test_units_scaling_clock_dtype_and_fake_timestamp_identity_denied(self):
        with tempfile.TemporaryDirectory(dir=WORK) as tmp:
            for path,field,value in [(ROT,'unit','degrees'),(ROT,'conversion',2.),(ROT,'offset',1.),(TARGET,'unit','milliseconds'),(END,'offset',1.),('/processing/running/running_wheel_rotation','unit','degrees')]:
                with fixture(str(Path(tmp)/'f.h5')) as f:
                    f[path].attrs[field]=value
                    with self.assertRaises(ValueError):read_fixture(f)
            with fixture(str(Path(tmp)/'f.h5')) as f:
                del f[ALIAS];f.create_dataset(ALIAS,data=np.array([.1,.2]))
                with self.assertRaises(ValueError):read_fixture(f)
            with fixture(str(Path(tmp)/'f.h5')) as f:
                del f[SCALARS[1]];f.create_dataset(SCALARS[1],data='wrongclock')
                with self.assertRaises(ValueError):read_fixture(f)

    def test_final_altered_and_unregistered_source_denied(self):
        item={'session_id':750749662,'role':'Development','etag':'frozen'};reg={'objects':[item],'denied_final_session_ids':[9]}
        validate_source(item,reg)
        for bad in [{**item,'etag':'wrong'},{**item,'role':'Final'},{**item,'session_id':9}]:
            with self.assertRaises(ValueError):validate_source(bad,reg)

    def test_HTTP_ranges_no_redirect_retry_cache_and_partial_accounting(self):
        with tempfile.TemporaryDirectory(dir=WORK) as tmp:
            for k,response in enumerate([Response(),Response(status=302),Response(etag='changed'),Response(content_range='wrong'),Response(body=b'bad')]):
                j=BudgetJournal(Path(tmp)/f'{k}.jsonl');r=RangeReader({'session_id':1,'size':100,'file_id':'synthetic','etag':'fixed'},time.monotonic()+10,j);r.http.close();r.http=HTTP(response)
                if k==0:
                    self.assertEqual(r.read(4),b'abcd');r.seek(0);self.assertEqual(r.read(4),b'abcd');self.assertEqual((r.used,r.reserved,r.calls),(4,5,1))
                else:
                    with self.assertRaises(ResourceStop):r.read(4)
                self.assertEqual(r.http.calls,1);self.assertIs(r.http.kw['allow_redirects'],False);j.close()
            j=BudgetJournal(Path(tmp)/'partial.jsonl');r=RangeReader({'session_id':1,'size':100,'file_id':'x','etag':'fixed'},time.monotonic()+10,j)
            class Interrupted:
                n=0
                def read(self,n):
                    self.n+=1
                    if self.n==1:return b'ab'
                    raise OSError('injected stream crash')
            response=Response();response.raw=Interrupted();r.http.close();r.http=HTTP(response)
            with self.assertRaises(OSError):r.read(4)
            self.assertEqual((r.used,r.reserved,len(r.ranges)),(2,5,0));j.close()

    def test_per_object_global_request_and_cache_deadline_limits(self):
        with tempfile.TemporaryDirectory(dir=WORK) as tmp:
            for k,limit in enumerate(['calls','source','global','deadline']):
                j=BudgetJournal(Path(tmp)/f'{k}.jsonl');r=RangeReader({'session_id':1,'size':100,'file_id':'x','etag':'fixed'},time.monotonic()+10,j);r.http.close();r.http=HTTP(Response())
                if limit=='calls':r.calls=4096
                if limit=='source':r.reserved=134217725
                if limit=='global':j.total_reserved=3758096381
                if limit=='deadline':r.cache[(0,4)]=b'abcd';r.deadline=time.monotonic()-1
                with self.assertRaises(ResourceStop):r.read(4)
                self.assertEqual(r.http.calls,0);j.close()

    def test_watchdog_duplicate_and_cohort_floors_not_physiology(self):
        with tempfile.TemporaryDirectory(dir=WORK) as tmp:
            target=Path(tmp)/'supervision.json'
            self.assertEqual(supervise([sys.executable,'-c','import time;time.sleep(60)'],time.monotonic()+.1,target),124)
            self.assertFalse(json.loads(target.read_text(encoding='utf8'))['valid_completed_worker'])
            with patch('subprocess.Popen',side_effect=AssertionError('no second child')):
                with self.assertRaises(FileExistsError):supervise([sys.executable,'-c','pass'],time.monotonic()+10,target)
        rows=[{'mouse_id':str(i),'protocol':'brain_observatory_1.1' if i<3 else 'functional_connectivity','potential_running_coverage_pass':True} for i in range(14)]
        self.assertTrue(admission_possible(rows)['possible_A_physiological_admission'])
        rows[0]['potential_running_coverage_pass']=False
        self.assertFalse(admission_possible(rows)['possible_A_physiological_admission'])


if __name__=='__main__':unittest.main()
