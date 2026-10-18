"""Synthetic attempt ledger/stage/coordinate integration regressions; no real fits."""
import concurrent.futures
import json
import tempfile
import unittest
from pathlib import Path
import numpy as np
from .source import P
from .training import configurations, baseline_availability, claim_attempt, verify_completed_attempt, build_model
from .models import pg


class WorkerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):(P/'work/test_tmp').mkdir(parents=True,exist_ok=True)
    def test_exact_grid_start_denominators(self):
        configs=configurations();self.assertEqual(len(configs),61)
        self.assertEqual(len({x['id'] for x in configs}),61)
        self.assertEqual([sum(x['family']==f for x in configs) for f in ['B0','B1','B2','B3','B4','D','C','S']],[1,3,3,3,3,18,12,18])
        self.assertEqual({x['seed'] for x in configs if x['family']=='D'},{11,23,37})
    def records(self):
        return [dict(subject=s,configuration=c,status='NUMERICAL_PASS') for s in ['mouseA','mouseB'] for c in configurations() if c['family'].startswith('B')]
    def test_global_baseline_availability_not_partial_success(self):
        records=self.records()
        self.assertTrue(baseline_availability(records,['mouseA','mouseB'])['PRIMARY_BASELINE_NUMERICAL_GATE'])
        for x in records:
            if x['subject']=='mouseA' and x['configuration']['family']=='B4':x['status']='NUMERICAL_FAIL'
        self.assertFalse(baseline_availability(records,['mouseA','mouseB'])['PRIMARY_BASELINE_NUMERICAL_GATE'])
    def test_missing_or_started_baseline_cannot_open_dynamic_gate(self):
        records=self.records()
        with self.assertRaises(AssertionError):baseline_availability(records[:-1],['mouseA','mouseB'])
        records[0]['status']='STARTED'
        with self.assertRaises(AssertionError):baseline_availability(records,['mouseA','mouseB'])
    def test_only_one_concurrent_attempt_claim(self):
        with tempfile.TemporaryDirectory(dir=P/'work/test_tmp') as d:
            path=Path(d)/'attempt.json';record=dict(status='STARTED',sentinel='original')
            def one(_):
                try:claim_attempt(path,record);return True
                except FileExistsError:return False
            with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:results=list(pool.map(one,range(2)))
            self.assertEqual(sum(results),1);self.assertEqual(json.loads(path.read_text())['sentinel'],'original')
            with self.assertRaises(FileExistsError):claim_attempt(path,dict(status='replacement'))
    def test_started_attempt_never_retried(self):
        with self.assertRaises(AssertionError):verify_completed_attempt(dict(status='STARTED'),{},'gate')
    def test_gate_and_config_mismatch_denied(self):
        c=dict(id='B0');old=dict(status='NUMERICAL_PASS',configuration=c,production_gate_sha256='old')
        with self.assertRaises(AssertionError):verify_completed_attempt(old,c,'new')
        with self.assertRaises(AssertionError):verify_completed_attempt(old,dict(id='B1'),'old')
        verify_completed_attempt(old,c,'old')
    def test_C_coordinate_activity_frozen_from_A_not_B(self):
        arrays=dict(x=np.zeros((2,20,70)),y=np.zeros((2,20,8)),active=np.ones(70,bool),
            C_r2_tau0_1=None)
        arrays['x'][:,:,0]=1;arrays['C_r2_tau0.1']=np.zeros((2,20,2))
        arrays['C_r2_tau0.1_active']=np.ones(2,bool)
        model=build_model(arrays,dict(family='C',rank=2,tau=.1,ridge=.1))
        self.assertEqual(model.size,576)
    def test_stationary_MLE_zero_and_positive_target_bound_sign(self):
        arrays=dict(x=np.ones((1,20,70)),y=np.zeros((1,20,8)),active=np.ones(70,bool))
        arrays['y'][0,10:,1]=1
        model=build_model(arrays,dict(family='B0',ridge=0.))
        theta=np.clip(np.log(np.maximum(model.y[:,10:].sum(axis=(0,1)),np.finfo(float).tiny)/(model.T*.05)),-8,8)
        self.assertLessEqual(pg(theta,model.objective(theta)[1],model.bounds),1e-12)


if __name__=='__main__':unittest.main(verbosity=2)
