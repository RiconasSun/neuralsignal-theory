import copy
import unittest
import tempfile
from pathlib import Path
import study
from reproduce_saved import validate_row

def row():
    x=1.;h=.01;v=[(x+k*h)**4 for k in (-2,-1,-.5,.5,1,2)];fm2,fm,fmh,fph,fp,fp2=v;c=(fp-fm)/(2*h);q=(fm2-8*fm+8*fp-fp2)/(12*h);z=(4*(fph-fmh)/h-c)/3
    r=dict(h=h,theta=x,scale=h,analytical=4.,AD=4.,ridge_AD=.001,likelihood_AD=3.999,central=c,fourth_order=q,richardson=z,AD_abs_error=0.,AD_scaled_error=0.)
    r.update(dict(zip(('f_minus2','f_minus1','f_minus_half','f_plus_half','f_plus1','f_plus2'),v)))
    for k,d in (('central',c),('fourth',q),('richardson',z)):r[k+'_abs_error']=abs(d-4);r[k+'_scaled_error']=abs(d-4)/max(1,abs(d),4)
    return {k:str(v) for k,v in r.items()}

def scratch():
    root=Path(__file__).resolve().parent/'replay'/'audit-tests';root.mkdir(parents=True,exist_ok=True)
    return root

class SavedAudit(unittest.TestCase):
    def test_saved_arithmetic(self):validate_row(row())
    def test_changed_probe_rejected(self):
        r=row();r['f_plus1']='100.'
        with self.assertRaises(RuntimeError):validate_row(r)
    def test_ridge_omission_rejected(self):
        r=row();r['ridge_AD']='0.'
        with self.assertRaises(RuntimeError):validate_row(r)
    def test_changed_step_rejected(self):
        r=row();r['scale']='.1'
        with self.assertRaises(RuntimeError):validate_row(r)
    def test_archived_launcher_third_argument_supported_append_only(self):
        root=scratch()
        with tempfile.TemporaryDirectory(dir=root) as d:
            self.assertTrue(Path(d).resolve().is_relative_to(root.resolve()))
            p=Path(d)/'receipt.json';study.save(p,{'completed':True},True)
            with self.assertRaises(FileExistsError):study.save(p,{'completed':False},True)
            self.assertTrue(study.load(p)['completed'])
    def test_overwrite_receipt_forbidden(self):
        root=scratch()
        with tempfile.TemporaryDirectory(dir=root) as d:
            self.assertTrue(Path(d).resolve().is_relative_to(root.resolve()))
            with self.assertRaises(ValueError):study.save(Path(d)/'receipt.json',{},False)

if __name__=='__main__':unittest.main(verbosity=2)
