import json,math,struct,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import numpy as np
import pandas as pd
from .source import P,dump,load_json
from .native_table import encode_table,records,verify_native,decode_cell
from .features import held
from .metadata_qc import task_masks
from .metadata_access import verify_cache

class NativeTableTests(unittest.TestCase):
    def test_finite_extremes_and_bit_patterns(self):
        values=np.array([0.,-0.,np.nextafter(0.,1.),np.nextafter(1.,0.),np.nextafter(1.,2.),np.finfo(float).max,1150.1833035011502])
        f=pd.DataFrame({'stimOn_times':values});table=encode_table(f);view=records(table)
        self.assertTrue(verify_native(f,table,view)['bitwise_pass'])
        self.assertEqual(values.tobytes(),np.array([v['stimOn_times'] for v in view]).tobytes())

    def test_missing_and_nonfinite_classification_preserved(self):
        f=pd.DataFrame({'x':[np.nan,np.inf,-np.inf,0.],'nullable':pd.Series([pd.NA,1.,2.,3.],dtype='Float64')})
        table=encode_table(f);view=records(table)
        self.assertTrue(verify_native(f,table,view)['bitwise_pass'])
        self.assertIsNone(view[0]['x']);self.assertIsNone(view[0]['nullable'])
        self.assertEqual(view[1]['x'],np.inf);self.assertEqual(view[2]['x'],-np.inf)
        with tempfile.TemporaryDirectory(dir=P/'work/test_tmp') as d:
            path=Path(d)/'x.json';dump(path,dict(native_table=table,trials=view))
            raw=path.read_text();json.loads(raw,parse_constant=lambda s:(_ for _ in ()).throw(ValueError(s)))
            restored=load_json(raw);self.assertTrue(verify_native(f,restored['native_table'],restored['trials'])['bitwise_pass'])

    def test_infinite_contrast_does_not_become_missing(self):
        f=pd.DataFrame([dict(intervals_0=i*3.,stimOn_times=i*3.+1.2,goCue_times=i*3.+1.,feedback_times=i*3.+1.8,
            intervals_1=i*3.+2.5,contrastLeft=np.inf if i==5 else np.nan,contrastRight=.25) for i in range(20)])
        view=records(encode_table(f));a=task_masks(f,[0,100],[],True)[1];b=task_masks(pd.DataFrame(view),[0,100],[],True)[1]
        np.testing.assert_array_equal(a,b);self.assertFalse(a[5])

    def test_hex_bits_contradiction_denied(self):
        cell=encode_table(pd.DataFrame({'x':[1.]}))['columns']['x'][0];cell['hex']='0x1.0000000000001p+0'
        with self.assertRaises(AssertionError):decode_cell(cell)

    def test_pl033_and_all_predecessor_queries(self):
        event=1150.1833035011502;wt=np.array([event-1,event,event+1]);wp=np.array([0.,1.,2.])
        f=pd.DataFrame({'stimOn_times':[event]});exact=records(encode_table(f))[0]['stimOn_times']
        self.assertEqual(struct.pack('>d',event),struct.pack('>d',exact))
        for label in ('bin','bin-.05','bin-.1','bin-.25','bin-.5','epoch'):
            with self.subTest(query=label):
                self.assertEqual(int(held(wt,wp,exact)[1]),0)
                self.assertEqual(int(held(wt,wp,np.nextafter(exact,-np.inf))[1]),0)
                self.assertEqual(int(held(wt,wp,np.nextafter(exact,np.inf))[1]),1)
        with self.assertRaises(ValueError):held(wt,wp,event-1)

    def test_metadata_missing_and_tampered_receipt_denied(self):
        import hashlib
        with tempfile.TemporaryDirectory(dir=P/'work/test_tmp') as d:
            root=Path(d);path=root/'body';path.write_bytes(b'abcd');row=dict(eid='test');file=dict(key='native',bytes=4)
            with patch('paper15_r1.metadata_access.R',root):
                with self.assertRaises(PermissionError):verify_cache(row,file,path)
                rec=root/'paper15_m0/results/FILE_RECEIPTS.json';rec.parent.mkdir(parents=True)
                rec.write_text(json.dumps([dict(key='native',status='COMPLETE',sha256=hashlib.sha256(b'abcd').hexdigest())]))
                self.assertEqual(verify_cache(row,file,path),path)
                path.write_bytes(b'abce')
                with self.assertRaises(AssertionError):verify_cache(row,file,path)

if __name__=='__main__':unittest.main()
