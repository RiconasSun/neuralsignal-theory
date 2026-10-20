"""Native synthetic integration and guard regressions; no protected A values."""
import json,math,os,sys,tempfile,time,unittest
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import patch
import numpy as np
from .common import *
from . import broker,access
from .fixtures import Fixture

class Tests(unittest.TestCase):
    def test_policy_only_ftol_change(self):verify_policy();self.assertEqual(NUMERIC['options']['ftol'],0.)
    def test_runtime_and_static_semantics(self):
        self.assertEqual(verify_runtime()['scipy'],'1.16.3')
        code=(R/'paper16_m1/work/runtime/Lib/site-packages/scipy/optimize/_lbfgsb_py.py').read_text(encoding='utf8')
        self.assertIn('factr = ftol / np.finfo(float).eps',code)
    def test_external_FG_cap_before_extra_evaluation(self):
        c=broker.Counter();c.calls=5999;c.value_gradient();self.assertEqual(c.calls,6000)
        calls=[]
        def attempt():c.value_gradient();calls.append('evaluated')
        with self.assertRaises(BudgetStop):attempt()
        self.assertEqual(calls,[]);self.assertEqual(c.calls,6000)
    def test_iteration_cap_before_extra_iteration_or_FG(self):
        c=broker.Counter();c.iterations=1499;c.accepted()
        with self.assertRaises(BudgetStop):c.accepted()
        with self.assertRaises(BudgetStop):c.value_gradient()
        self.assertEqual((c.iterations,c.calls),(1500,0))
    def test_finite_guard(self):
        with self.assertRaises(NumericalStop):broker.finite(float('inf'),np.zeros(2))
        with self.assertRaises(NumericalStop):broker.finite(1.,np.array([float('nan')]))
    def test_original_PG_sign_epsilon(self):
        x=np.array([-1.,-1.,1.,1.,0.,-1.+2e-12]);g=np.array([2.,-2.,-3.,3.,4.,5.])
        np.testing.assert_array_equal(spec.projected_gradient(x,g,np.full(6,-1.),np.ones(6)),[0,-2,0,3,4,5])
        np.testing.assert_array_equal(spec.projected_gradient([-1.+5e-13],np.array([1.]),np.array([-1.]),np.array([1.])),[0.])
    def test_clock_cap_and_expiry(self):
        stage=load(Path(os.environ['P16_TF1_FOLDER'])/'STAGE.json');guard(stage)
        with self.assertRaises(Exception):guard({**stage,'deadline_monotonic':stage['start_monotonic']+7201})
    def test_A_allowlist_and_neural_denials(self):
        identity=load(P/'INPUT_IDENTITY.json');self.assertTrue(access.allowed_protected(R/identity['A_state']['path']))
        access.check_open(R/identity['A_state']['path'])
        for path in ['paper16_development_r3/work/B_selection/733457989/1.0.npz','paper16_development_r3/work/prepared/726162197/MAIN/state.npz','paper16_final/work/D/counts.npz','paper16_m1/work/nonruntime.npz']:
            with self.assertRaises(AccessStop):access.check_open(R/path)
    def test_no_worker_score_or_source_controller(self):
        text=(P/'worker.py').read_text(encoding='utf8')+(P/'access.py').read_text(encoding='utf8')
        self.assertNotIn('import source',text);self.assertNotIn('import controller',text);self.assertNotIn('.score(',text)
    def test_claim_repeat_and_concurrency(self):
        with tempfile.TemporaryDirectory(dir=P/'work') as folder:
            path=Path(folder)/'CLAIM.json'
            def run(_):
                try:claim(path,{'test':True});return True
                except FileExistsError:return False
            with ThreadPoolExecutor(max_workers=2) as pool:self.assertEqual(sum(pool.map(run,range(2))),1)
            with self.assertRaises(FileExistsError):claim(path,{})
    def test_code_tamper_denial(self):
        with patch('paper16_termination_feasibility1.common.sha',return_value='0'*64):
            with self.assertRaises(ImplementationStop):verify_code()
    def test_prefit_missing_denial(self):
        with patch('paper16_termination_feasibility1.common.verify_history'),patch('paper16_termination_feasibility1.common.verify_code'),patch('paper16_termination_feasibility1.common.load',side_effect=FileNotFoundError('approval missing')):
            with self.assertRaises(FileNotFoundError):verify_prefit()
    def test_poisson_closed_form_reference(self):
        row=load(P/'PROSPECTIVE_REGISTRATION.json')['synthetic_fixtures'][0];o=Fixture(row);x=o.x0
        value,g=o.analytic(x);eta=o.X@x;mu=o.exposure*np.exp(eta)
        independent=sum(float(m-y*(math.log(.02)+z)+math.lgamma(y+1)) for m,y,z in zip(mu,o.y,eta))/12+.05*sum(x[1:]**2)
        grad=np.array([sum(float(o.X[j,k]*(mu[j]-o.y[j])) for j in range(12))/12+(.1*x[k] if k else 0) for k in range(3)])
        self.assertAlmostEqual(value,independent,places=14);np.testing.assert_allclose(g,grad,atol=1e-14,rtol=0)
        advalue,ad=o.AD(x);np.testing.assert_allclose(ad,g,atol=1e-14,rtol=0);self.assertAlmostEqual(advalue,value,places=14)
    def test_four_fixed_fixtures(self):
        root=Path(os.environ['P16_TF1_FOLDER']);stage=load(root/'STAGE.json');outcomes=[]
        for row in load(P/'PROSPECTIVE_REGISTRATION.json')['synthetic_fixtures']:
            folder=root/row['name'];o=Fixture(row)
            try:broker.fit(o,folder,stage,{'id':'synthetic:'+row['name']})
            except NumericalStop:
                if row['name']!='rounded_plateau':raise
            result=load(folder/'RESULT.json');diag=load(folder/'DIAGNOSTICS.json')
            if row['name']=='rounded_plateau':
                self.assertFalse(result['numerical_pass']);self.assertGreater(result['projected_gradient_inf'],1e-5)
                self.assertTrue(result['success']);self.assertIn('RELATIVE REDUCTION',result['message'])
            else:self.assertTrue(result['numerical_pass']);self.assertTrue(diag['all_checkpoints_pass'])
            self.assertEqual(diag['FD_objective_calls'],24*len(o.x0));self.assertEqual(diag['AD_calls'],3);self.assertEqual(diag['analytic_checkpoint_calls'],3)
            self.assertLessEqual(result['nfev'],6000);self.assertLessEqual(result['nit'],1500)
            outcomes.append({'fixture':row['name'],'numerical_pass':result['numerical_pass'],'expected_negative':row['name']=='rounded_plateau','objective':result['objective'],'PG':result['projected_gradient_inf'],'termination':result['message'],'iterations':result['nit'],'FG':result['nfev'],'diagnostics':diag})
        once(root/'FIXTURE_OUTCOMES.json',{'outcomes':outcomes,'candidate_count':1,'real_A_attempts':0})
    def test_native_job_and_external_deadline(self):
        from .supervisor import supervise_child
        stage=make_stage(1.0);folder=Path(os.environ['P16_TF1_FOLDER'])
        result=supervise_child([sys.executable,'-B','-c','import time; time.sleep(60)'],stage,folder/'DEADLINE_NEGATIVE.log',f'Local\\P16_TF1_DEADLINE_{time.time_ns()}')
        once(folder/'DEADLINE_NEGATIVE.json',result)
        self.assertTrue(result['killed_at_deadline']);self.assertTrue(result['assigned_before_resume']);self.assertNotEqual(result['returncode'],0)

def run(folder):
    result=unittest.TextTestRunner(stream=sys.stdout,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Tests))
    report={'tests_run':result.testsRun,'errors':len(result.errors),'failures':len(result.failures),'skipped':len(result.skipped),'mandatory_tests_pass':result.wasSuccessful() and not result.skipped,'real_A_attempts':0,'code_freeze_sha256':sha(P/'CODE_FREEZE.json')}
    once(folder/'TEST_RESULT.json',report)
    if not report['mandatory_tests_pass']:raise ImplementationStop('Synthetic certification failed; no real execution')

