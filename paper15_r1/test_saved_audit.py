"""Saved arithmetic and manifest counterexamples; synthetic values only."""
import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import numpy as np
from .source import P
from .saved_audit import numerical_record,original_control,score_table
from .saved_verify import archive_paths,verify_archive
from .models import Model,pg
from .independent_ad import coordinate_check


class SavedAuditTests(unittest.TestCase):
    def test_sensitivity_bounds_and_PG_independently_recomputed(self):
        x=np.ones((1,20,46));y=np.zeros((1,20,2));model=Model(x,y,'B0')
        theta=np.full(model.size,-8.);j,g=model.objective(theta);check=coordinate_check(model,theta,True)
        state=dict(status='A_PREPROCESSING_SEALED',units=[0,1],active=[True]*46,warm=10,delta=.05,nuisance_columns=37)
        record=dict(status='NUMERICAL_PASS',coefficients=theta.tolist(),independent=check,objective=j,
            full_gradient_inf=float(np.abs(g).max()),PG=pg(theta,g,model.bounds),optimizer_status=0,
            plan_item=dict(family='B0',ridge=.1),free_parameters=model.size)
        numerical_record(record,True,state)
        for coeff,reportedPG in [([-9.,-8.],0.),([-7.,-8.],0.),(theta.tolist(),.0001)]:
            bad=copy.deepcopy(record);bad['coefficients']=coeff;bad['PG']=reportedPG
            with self.assertRaises(AssertionError):numerical_record(bad,True,state)
    def test_archive_exact_set_excludes_only_cache_and_root_freeze(self):
        (P/'work/test_tmp').mkdir(parents=True,exist_ok=True)
        with tempfile.TemporaryDirectory(dir=P/'work/test_tmp') as temp:
            root=Path(temp)
            for rel in ['models.py','work/neural.npy','__pycache__/x.pyc','ARCHIVE_FREEZE.json','sub/ARCHIVE_FREEZE.json']:
                path=root/rel;path.parent.mkdir(parents=True,exist_ok=True);path.write_text('synthetic')
            with patch('paper15_r1.saved_verify.P',root):
                self.assertEqual(archive_paths(),{'models.py','sub/ARCHIVE_FREEZE.json'})
                with self.assertRaises(AssertionError):verify_archive(dict(hashes={}))
                with self.assertRaises(AssertionError):verify_archive(dict(hashes={'models.py':'fabricated'}))
    def test_cached_original_control_cannot_forge_observed_or_N3_gain(self):
        panel=dict(original_model_scores=dict(B4=dict(LL=30.,unit_bins=100),B1=dict(LL=10.,unit_bins=100)),
            observed=[.2,None,None,None,None,None],wheel_gain_original=None)
        original_control(panel,'N1',100)
        bad=copy.deepcopy(panel);bad['observed'][0]=9.
        with self.assertRaises(AssertionError):original_control(bad,'N1',100)
        panel['observed']=[.3]*6;panel['wheel_gain_original']=.2;original_control(panel,'N3',100)
        for field,value in [('wheel_gain_original',9.),('observed',[.2]*6)]:
            bad=copy.deepcopy(panel);bad[field]=value
            with self.assertRaises(AssertionError):original_control(bad,'N3',100)
        for score in [dict(LL=float('inf'),unit_bins=100),dict(LL=1.,unit_bins=0),dict(LL=1.,unit_bins=99)]:
            with self.assertRaises(AssertionError):score_table(dict(B4=score),100)


if __name__=='__main__':unittest.main()
