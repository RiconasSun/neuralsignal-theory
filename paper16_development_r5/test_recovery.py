"""R5-only synthetic contracts; no real saved-array evaluation."""
import copy,ctypes,json,os,subprocess,sys,time,unittest
from pathlib import Path
from unittest.mock import patch
import numpy as np
from . import core,controller,optimizer,models,features,evidence_checks
from .core import *
from paper16_dev_r3 import clock_bound

def folder(name):
    p=P/'work/synthetic'/f'{name}_{time.time_ns()}';p.mkdir(parents=True);return p

def stage():return load(os.environ['P16_R5_TEST_STAGE'])

def dead(pid):
    k=ctypes.WinDLL('kernel32',use_last_error=True)
    k.OpenProcess.argtypes=[ctypes.c_ulong,ctypes.c_int,ctypes.c_ulong];k.OpenProcess.restype=ctypes.c_void_p
    k.WaitForSingleObject.argtypes=[ctypes.c_void_p,ctypes.c_ulong];k.WaitForSingleObject.restype=ctypes.c_ulong
    k.CloseHandle.argtypes=[ctypes.c_void_p]
    h=k.OpenProcess(0x100000,False,pid)
    if not h:return True
    try:return k.WaitForSingleObject(h,0)==0
    finally:k.CloseHandle(h)

class RecoveryTests(unittest.TestCase):
    def test_real_integrity_guard_rejects_R3_fit_and_B0_unregistered_extras(self):
        for kind in ['fits','B0']:
            root=folder('R3_extra');old=root/'old';four=root/'four';state=old/'work'/kind/'synthetic';state.mkdir(parents=True)
            path=state/'RESULT.json';path.write_bytes(b'synthetic original registered state')
            rows=[{'path':path.relative_to(R).as_posix(),'sha256':sha(path)}]
            targets={'B0_targets':[{'result_path':path.relative_to(R).as_posix()}] if kind=='B0' else []}
            admitted={'synthetic':{'origin':'R3','result_path':path.relative_to(R).as_posix()}} if kind=='fits' else {}
            def metadata(p):return {'files':rows} if str(p).endswith('INDEPENDENT_R5_PROTECTED_HASH_READBACK.json') else targets
            with patch.object(controller,'OLD',old),patch.object(controller,'FOUR',four),patch.object(controller,'verify_pins'),patch.object(controller,'admitted_lookup',return_value=admitted),patch.object(controller,'load',side_effect=metadata):
                controller.verify_historical_integrity(stage())
                (state/'unregistered.npz').write_bytes(b'injected unrelated state')
                with self.assertRaisesRegex(AccessStop,'Exact registered historical state folder'):controller.verify_historical_integrity(stage())

    def saved_fixture(self,bad_frozen_fd=False):
        root=folder('saved_certificate');task={'id':'SYNTHETIC_SAVED_FIXTURE','model':'B1','synthetic_only':True}
        initial=arrays(root/'initial.npz',x0=np.zeros(1),lo=np.full(1,-1.),hi=np.full(1,1.));saved={};rows=[]
        for name in ['initial','halfway','endpoint']:
            saved.update({name+'_x':np.zeros(1),name+'_analytic':np.zeros(1),name+'_AD':np.zeros(1),name+'_AD_error':np.zeros(1)})
            errors={}
            for h in [.001,.0001,.00001,.000001]:
                error=3e-5 if bad_frozen_fd and h==1e-5 else 0.
                saved[name+'_FD_'+str(h)]=np.full(1,error);saved[name+'_FD_error_'+str(h)]=np.full(1,error);errors[str(h)]=error
            rows.append({'checkpoint':name,'objective':0.,'AD_objective':0.,'AD_scaled_coordinate_error_max':0.,'FD_scaled_coordinate_errors':errors,'frozen_FD_scaled_error':errors['1e-05'],'pass':True})
        coordinate=arrays(root/'coordinate_certificates.npz',**saved)
        once(root/'DIAGNOSTICS.json',{'checkpoints':rows,'free_coordinates':1,'FD_objective_calls':24,'AD_calls':3,'analytic_checkpoint_calls':3,'coordinate_state':coordinate,'all_checkpoints_pass':True,'FD_step_not_selected_post_result':True})
        once(root/'ATTEMPT.json',{'task':task,'parameters':1,'bounds':initial,'synthetic_only':True})
        endpoint=arrays(root/'endpoint.npz',x=np.zeros(1),gradient=np.zeros(1))
        once(root/'RESULT.json',{'task':task,'numerical_pass':True,'projected_gradient_inf':0.,'objective':0.,'fun':0.,'x':[0.],'jac':[0.],'diagnostic_state_sha256':sha(root/'DIAGNOSTICS.json'),'endpoint_state':endpoint,'external_value_gradient_pairs':1,'external_accepted_iterations':0,'nfev':1,'nit':0,'accepted_vector_count':0,'halfway_accepted_iteration':0,'synthetic_only':True})
        event(root/'CALLS.jsonl',event='RESERVED_BEFORE_EVALUATION',call=1,iterations=0,x=[0.])
        event(root/'CALLS.jsonl',event='COMPLETED',call=1,objective=0.,gradient_inf=0.,gradient=[0.])
        return root,task

    def test_complete_boolean_cannot_replace_missing_corrupt_coordinates(self):
        root,task=self.saved_fixture();evidence_checks.fit(root,task)
        path=root/'coordinate_certificates.npz';path.rename(root/'preserved_coordinate_certificates.npz')
        with patch.object(controller,'admitted_lookup',return_value={}),patch.object(controller,'task_folder',return_value=root):
            with self.assertRaises(FileNotFoundError):controller.verify_completed([task])
        root,task=self.saved_fixture()
        with (root/'coordinate_certificates.npz').open('ab') as f:f.write(b'corrupt')
        with patch.object(controller,'admitted_lookup',return_value={}),patch.object(controller,'task_folder',return_value=root):
            with self.assertRaisesRegex(AccessStop,'member file hash'):controller.verify_completed([task])

    def test_original_B0_diag_coordinates_and_prep_hashes_required(self):
        for name in ['RESULT.json','DIAGNOSTICS.json','coordinate_certificates.npz','A_PREP.npz']:
            root=folder('historical_hash');path=root/name;path.write_bytes(b'synthetic original saved state')
            rows=[{'path':path.relative_to(R).as_posix(),'sha256':sha(path)}]
            evidence_checks.frozen_files(rows,stage(),[rows[0]['path']])
            path.write_bytes(b'changed historical saved state')
            with self.assertRaisesRegex(AccessStop,'Original historical file bytes changed'):evidence_checks.frozen_files(rows,stage())
        root=folder('historical_extra');path=root/'original';path.write_bytes(b'original');rows=[{'path':path.relative_to(R).as_posix(),'sha256':sha(path)}]
        with self.assertRaisesRegex(AccessStop,'Exact original inventory'):evidence_checks.frozen_files(rows,actual_paths=[rows[0]['path'],'extra'])

    def test_new_completed_journal_cannot_accept_changed_RESULT_bytes(self):
        root,task=self.saved_fixture();row={'event':'COMPLETED','task':task,'result_path':(root/'RESULT.json').relative_to(R).as_posix(),'result_sha256':sha(root/'RESULT.json')}
        evidence_checks.terminal(task,root,[row])
        with (root/'RESULT.json').open('ab') as f:f.write(b' ')
        # JSON semantics and numerical flags still pass; original termination identity does not.
        evidence_checks.fit(root,task)
        with self.assertRaisesRegex(AccessStop,'original hash join'):evidence_checks.terminal(task,root,[row])
        with self.assertRaises(AccessStop):evidence_checks.terminal(task,root,[row,row])

    def test_historical_RESULT_requires_canonical_registered_digest(self):
        root,task=self.saved_fixture()
        with patch.object(controller,'admitted_lookup',return_value={task['id']:{'result_sha256':'0'*64}}),patch.object(controller,'task_folder',return_value=root):
            with self.assertRaisesRegex(AccessStop,'Canonical historical RESULT hash'):controller.verify_completed([task])

    def test_favorable_FD_scale_cannot_replace_frozen_failed_h(self):
        root,task=self.saved_fixture(bad_frozen_fd=True)
        diag=load(root/'DIAGNOSTICS.json')
        self.assertEqual(diag['checkpoints'][0]['FD_scaled_coordinate_errors']['1e-06'],0.)
        self.assertGreater(diag['checkpoints'][0]['frozen_FD_scaled_error'],2e-5)
        with self.assertRaisesRegex(AccessStop,'Fixed h1e-5'):evidence_checks.fit(root,task)

    def test_failed_partial_and_diagnostic_state_cannot_enter_reuse(self):
        import hashlib
        task={'id':'SYNTHETIC_ORIGINAL','unit_id':101}
        path='paper16_development_r4/work/fits/'+hashlib.sha256(task['id'].encode()).hexdigest()+'/RESULT.json'
        target={'task':task,'origin':'R4','historical_ftol':0.,'result_path':path,'result_sha256':'a'*64}
        row={**target,'status':'PASS','PG':0.,'AD_error_max':0.,'fixed_FD_error_max':0.}
        evidence_checks.reuse([row],[target])
        for status in ['FAILED','INTERRUPTED_INCOMPLETE','DIAGNOSTIC_ONLY']:
            with self.assertRaises(AccessStop):evidence_checks.reuse([{**row,'status':status}],[target])
        for changed in [{'result_path':'paper16_termination_feasibility1/work/RESULT.json'},{'origin':'DIAGNOSTIC'},{'result_sha256':'b'*64},{'task':{**task,'unit_id':102}}]:
            with self.assertRaises(AccessStop):evidence_checks.reuse([{**row,**changed}],[target])

    def test_wrong_unit_and_scaler_members_cannot_enter_prepared_A(self):
        values={'ordinals':np.array([0]),'unit_ids':np.array([101,102]),'mean':np.zeros((2,1)),'scale':np.ones((2,1)),'active':np.ones((2,1),bool)}
        row={'role':'A','arrays':{k:array_id(v) for k,v in values.items()},'key':'synthetic/MAIN'}
        evidence_checks.prepared(row,values,copy.deepcopy(row))
        for field in ['unit_ids','scale','mean','active']:
            changed={k:v.copy() for k,v in values.items()};changed[field]=changed[field]+1
            with self.assertRaisesRegex(AccessStop,'member identity'):evidence_checks.prepared(row,changed,row)
            altered={**row,'arrays':{k:array_id(v) for k,v in changed.items()}}
            with self.assertRaisesRegex(AccessStop,'index/source/unit/scaler'):evidence_checks.prepared(altered,changed,row)

    def test_missing_one_original_DS_seed_rejects_group(self):
        prep=[{'key':'synthetic/MAIN','panel':'MAIN'}]
        tasks=[{'id':f'{m}_{s}','mouse_id':'synthetic','panel':'MAIN','model':m,'seed':s} for m in ['D','S'] for s in [11,23,37]]
        def metadata(path):
            if str(path).endswith('A_PREPROCESSING_STATES.json'):return prep
            return {'numerical_pass':True,'objective':0.}
        with patch.object(controller,'load',side_effect=metadata),patch.object(controller,'task_folder',return_value=folder('seed_metadata')):
            self.assertEqual(len(controller.selected_seeds(tasks)),2)
            with self.assertRaisesRegex(AccessStop,'Every original seed required'):controller.selected_seeds(tasks[:-1])

    def test_actual_phaseA_and_phaseB_clock_extension_rejected(self):
        actual=stage()
        for phase,seconds in [('A_PREFLIGHT',86401),('B_A_M4',172801)]:
            altered={**actual,'phase':phase}
            altered['deadline_monotonic']=altered['start_monotonic']+seconds
            altered['deadline_UTC']=(clock_bound.parse_utc(altered['start_UTC'])+__import__('datetime').timedelta(seconds=seconds)).isoformat()
            with self.assertRaises(Exception):core.guard(altered)

    def test_actual_clock_exception_types_have_registered_stop_categories(self):
        for exc,expected in [
            (ResourceStop('Original Development48h deadline/stale clock; no phase reset'),'STOP_BUDGET_REQUIRED_GATE'),
            (ResourceStop('Changed Windows boot epoch; original stage cannot resume'),'STOP_EXECUTION_INTERRUPTED_REQUIRED_GATE'),
            (ResourceStop('Windows boot epoch unavailable; no source access'),'STOP_EXECUTION_INTERRUPTED_REQUIRED_GATE'),
            (BudgetStop('cap'),'STOP_BUDGET_REQUIRED_GATE'),
            (ProcessStop('Job lost'),'STOP_EXECUTION_INTERRUPTED_REQUIRED_GATE'),
            (NumericalStop('frozen FD failed'),'STOP_NUMERICAL_REQUIRED_GATE'),
            (AccessStop('source hash'),'STOP_ACCESS_OR_IMPLEMENTATION_REQUIRED_GATE'),
        ]:
            self.assertEqual(controller.stop_category(exc),expected)

    def test_worker_bootstrap_clock_stop_before_private_arrays(self):
        for message,status in [('Original Development48h deadline/stale clock; no phase reset','STOP_BUDGET_REQUIRED_GATE'),('Changed Windows boot epoch; original stage cannot resume','STOP_EXECUTION_INTERRUPTED_REQUIRED_GATE')]:
            root=folder('bootstrap_stop');once(root/'results/STAGE_CLAIM.json',{'synthetic_only':True})
            with patch.object(controller,'P',root),patch.object(controller,'require_phase',side_effect=ResourceStop(message)),patch.object(controller,'load_prepared',side_effect=AssertionError('No private arrays after stop')):
                with self.assertRaises(ResourceStop):controller.worker()
            self.assertEqual(load(root/'results/SCIENTIFIC_STOP.json')['scientific_status'],status)
            self.assertFalse((root/'results/WORKER_CLAIM.json').exists())

    def test_native_outcome_classification_preserves_exact_receipts(self):
        for code,killed,clock,status in [(124,True,None,'STOP_BUDGET_REQUIRED_GATE'),(1,False,'Changed Windows boot epoch; original stage cannot resume','STOP_EXECUTION_INTERRUPTED_REQUIRED_GATE'),(1,False,None,'STOP_EXECUTION_INTERRUPTED_REQUIRED_GATE'),(0,False,None,'STOP_ACCESS_OR_IMPLEMENTATION_REQUIRED_GATE')]:
            root=folder('supervision');result={'returncode':code,'killed_at_deadline':killed,'clock_failure':clock,'synthetic_unit_test':True}
            with patch.object(controller,'P',root):controller.record_supervision(result)
            self.assertEqual(load(root/'results/SUPERVISION.json'),result)
            self.assertEqual(load(root/'results/SCIENTIFIC_STOP.json')['scientific_status'],status)

    def test_supervisor_failure_does_not_invent_native_exit(self):
        root=folder('supervisor_failure')
        with patch.dict(os.environ),patch.object(controller,'P',root),patch.object(controller,'E',root),patch.object(controller,'verify_prefit'),patch.object(controller,'make_stage',return_value=stage()),patch.object(controller,'supervise_child',side_effect=OSError('injected native launch failure')):
            with self.assertRaises(OSError):controller.supervise()
        receipt=load(root/'results/SUPERVISOR_FAILURE.json')
        self.assertIsNone(receipt['native_returncode']);self.assertFalse(receipt['native_supervision_receipt_available'])
        self.assertEqual(load(root/'results/SCIENTIFIC_STOP.json')['scientific_status'],'STOP_EXECUTION_INTERRUPTED_REQUIRED_GATE')

    def test_math_copy_and_original_policy(self):
        core.verify_pins()
        self.assertEqual(NUMERIC['options'],load(Q/'PROPOSED_EXECUTION_POLICY.json')['options'])
        self.assertEqual(len(controller.tasks()),2479)
        self.assertEqual(controller.tasks()[0]['id'],'763236014:S02:S:None:11:GLOBAL')

    def test_every_non_A_role_denied_before_loading_even_with_M4(self):
        for role in ['B','E','C','D','Final','QC','scaling','scoring','unknown']:
            with self.subTest(role=role),patch.object(controller.np,'load',side_effect=AssertionError('No neural read')):
                with self.assertRaises(AccessStop):controller.load_prepared(role)
        self.assertFalse(hasattr(controller,'evaluate_E'));self.assertFalse(hasattr(controller,'run_controls'))

    def test_missing_tampered_duplicate_manifest(self):
        root=folder('manifest');a=root/'a.txt';a.write_text('original');manifest=root/'manifest.json'
        row={'path':a.relative_to(R).as_posix(),'sha256':sha(a)};once(manifest,{'files':[row]})
        controller.check_manifest(manifest)
        a.write_text('tampered')
        with self.assertRaises(AccessStop):controller.check_manifest(manifest)
        duplicate=root/'duplicate.json';once(duplicate,{'files':[row,row]})
        with self.assertRaises(AccessStop):controller.check_manifest(duplicate)
        with self.assertRaises(FileNotFoundError):controller.check_manifest(root/'missing.json')

    def test_task_order_consumption_and_interruption_no_retry(self):
        root=folder('consume');plan=controller.tasks()[:2]
        with patch.object(controller,'P',root),patch.object(controller,'tasks',return_value=plan):
            with self.assertRaises(AccessStop):controller.consume(plan[1])
            controller.consume(plan[0])
            for task in plan:
                with self.assertRaises(AccessStop):controller.consume(task)
            event(root/'results/FIT_JOURNAL.jsonl',event='COMPLETED',task=plan[0])
            controller.consume(plan[1])
            with self.assertRaises(AccessStop):controller.consume(plan[1])

    def test_atomic_claim_and_concurrent_task_consumption(self):
        from concurrent.futures import ThreadPoolExecutor
        root=folder('concurrency');p=root/'claim.json'
        def claim(i):
            try:once(p,{'i':i});return True
            except FileExistsError:return False
        with ThreadPoolExecutor(2) as pool:self.assertEqual(sum(pool.map(claim,[1,2])),1)
        plan=controller.tasks()[:1]
        def attempt(i):
            try:controller.consume(plan[0]);return True
            except (AccessStop,FileExistsError):return False
        with patch.object(controller,'P',root),patch.object(controller,'tasks',return_value=plan),ThreadPoolExecutor(2) as pool:
            self.assertEqual(sum(pool.map(attempt,[1,2])),1)

    def test_missing_prefit_and_incomplete_M4_fail_closed(self):
        root=folder('incomplete')
        with patch.object(controller,'E',root):
            with self.assertRaises(FileNotFoundError):controller.verify_prefit()
        with patch.object(controller,'admitted_lookup',return_value={}):
            with self.assertRaises(FileNotFoundError):controller.verify_completed(controller.tasks()[:1])
        with patch.object(controller,'P',root):
            with self.assertRaisesRegex(AccessStop,'Missing D/S panel group'):controller.selected_seeds([])

    def test_phase_extension_deadline_sleep_backward_and_boot_change(self):
        actual=stage();core.guard(actual)
        bad=copy.deepcopy(actual);bad['phase']='UNKNOWN'
        with self.assertRaises(AccessStop):core.guard(bad)
        bad=copy.deepcopy(actual);bad['no_reset']=False
        with self.assertRaises(Exception):core.guard(bad)
        with patch.object(clock_bound.time,'monotonic',return_value=actual['deadline_monotonic']+1):
            with self.assertRaises(Exception):core.guard(actual)
        with patch.object(clock_bound.time,'monotonic',return_value=actual['start_monotonic']-1):
            with self.assertRaises(Exception):core.guard(actual)
        with patch.object(clock_bound,'utc_now',return_value=clock_bound.parse_utc(actual['deadline_UTC'])):
            with self.assertRaises(Exception):core.guard(actual)
        with patch.object(clock_bound,'boot_identity',return_value='different boot'):
            with self.assertRaises(Exception):clock_bound.verify_stage_environment(actual)

    def test_monotonic_float_rounding_never_extends_registered_span(self):
        for i in range(8):
            start=500000+i*2**-34
            original={'start_monotonic':start,'deadline_monotonic':start+172800,'start_UTC':'2026-01-01T00:00:00+00:00','deadline_UTC':'2026-01-03T00:00:00+00:00','no_reset':True}
            with patch.object(core,'original_make_stage',return_value=copy.deepcopy(original)):
                corrected=core.make_stage(172800)
            self.assertLessEqual(corrected['deadline_monotonic']-start,172800)
            self.assertLessEqual(corrected['deadline_monotonic'],original['deadline_monotonic'])
            self.assertEqual(corrected['start_monotonic'],start);self.assertEqual(corrected['deadline_UTC'],original['deadline_UTC'])

    def test_original_initialization_and_partial_vector_substitution_denied(self):
        from paper16_development_r4.test_production import batch
        b=batch(u=2);s=features.Scaling.fit(b);task=copy.deepcopy(controller.tasks()[0]);root=folder('initializer')
        obj=models.Objective(b,s,'S',1.,None,11)
        import hashlib
        path=root/'work/fits'/hashlib.sha256(task['id'].encode()).hexdigest()/'initial.npz'
        arrays(path,x0=obj.x0+1,lo=obj.lo,hi=obj.hi)
        with patch.object(controller,'FOUR',root):
            with self.assertRaises(AccessStop):controller.original_objective(task,b,s)
        for role in ['E','C','D']:
            with self.assertRaises(AccessStop):controller.original_objective(task,__import__('dataclasses').replace(b,role=role),s)

    def test_wrong_saved_role_hash_and_scaler_denied(self):
        root=folder('prep');index=root/'results/A_PREPROCESSING_STATES.json'
        once(index,[{'role':'E','path':'no-file','sha256':'0'*64}])
        with patch.object(controller,'OLD',root),patch.object(controller,'require_phase'):
            with self.assertRaises(AccessStop):controller.load_prepared()
        from paper16_development_r4.test_production import batch
        b=batch(u=2);s=features.Scaling.fit(b)
        with self.assertRaises(ImplementationStop):s.transform(__import__('dataclasses').replace(b,psth=b.psth+1))

    def test_original_outward_PG_and_fixed_FD_step(self):
        np.testing.assert_array_equal(spec.projected_gradient(np.array([-1.,1.]),np.array([-2.,3.]),-1.,1.),[-2.,3.])
        np.testing.assert_array_equal(spec.projected_gradient(np.array([-1.,1.]),np.array([2.,-3.]),-1.,1.),[0.,0.])
        self.assertEqual(NUMERIC['FD_frozen_acceptance_step'],1e-5)
        self.assertEqual(NUMERIC['FD_steps'],[.001,.0001,.00001,.000001])

    def test_diagnostic_reservation_interruption_preserved(self):
        class Interrupt:
            x0=np.zeros(1)
            def analytic(self,x):return 0.,np.zeros(1)
            def AD(self,x):raise RuntimeError('injected interruption after reservation')
        root=folder('reservation')
        with self.assertRaises(RuntimeError):optimizer.certificate(Interrupt(),[np.zeros(1)]*3,root,stage())
        rows=controller.journal(root/'DIAGNOSTIC_CALLS.jsonl')
        self.assertEqual([r['kind'] for r in rows],['ANALYTIC_RESERVED','AD_RESERVED'])
        self.assertFalse((root/'DIAGNOSTICS.json').exists())

    def test_inclusive_6000_FG_1500_iterations_full_certificate(self):
        class Constant:
            x0=np.zeros(1);lo=np.full(1,-1.);hi=np.full(1,1.)
            def analytic(self,x):return 0.,np.zeros(1)
            def AD(self,x):return 0.,np.zeros(1)
        root=folder('inclusive');client=root/'client.py'
        client.write_text("import json,sys\nfor i in range(6000):\n print(json.dumps({'op':'FG','x':[0.]}),flush=True);json.loads(sys.stdin.readline())\n if i%4==3: print(json.dumps({'op':'ITER','x':[0.]}),flush=True);json.loads(sys.stdin.readline())\nprint(json.dumps({'op':'DONE','x':[0.],'fun':0.,'jac':[0.],'success':True,'message':'synthetic inclusive boundary','nit':1500,'nfev':6000}),flush=True)\n",encoding='utf8')
        original=subprocess.Popen
        def launch(command,**kw):return original([sys.executable,'-B',str(client)],**kw)
        with patch.object(optimizer.subprocess,'Popen',side_effect=launch):
            _,result=optimizer.fit(Constant(),root/'fit',stage(),{'id':'SYNTHETIC_INCLUSIVE'})
        self.assertTrue(result['numerical_pass']);self.assertEqual(result['external_value_gradient_pairs'],6000);self.assertEqual(result['external_accepted_iterations'],1500)
        rows=controller.journal(root/'fit/CALLS.jsonl');self.assertEqual(len(rows),12000)
        c=optimizer.Counter();c.calls=6000
        with self.assertRaises(BudgetStop):c.value_gradient()
        c=optimizer.Counter();c.iterations=1500
        with self.assertRaises(BudgetStop):c.accepted()

    def test_native_parent_loss_kills_entire_job_tree(self):
        root=folder('parent_loss');pids=root/'pids.json'
        code="import os,sys,subprocess,time,json;from pathlib import Path;from paper16_dev_r3.windows_job import Job;\nwith Job('Local\\\\P16_R5_PARENT_'+str(os.getpid())) as job:\n p=subprocess.Popen([sys.executable,'-c','import time;time.sleep(60)']);job.assign(p);Path(sys.argv[1]).write_text(json.dumps([p.pid]));os._exit(17)\n"
        proc=subprocess.run([sys.executable,'-B','-c',code,str(pids)],cwd=R,timeout=15,capture_output=True,text=True)
        self.assertEqual(proc.returncode,17,proc.stderr);self.assertTrue(pids.exists())
        for pid in load(pids):
            until=time.monotonic()+5
            while not dead(pid) and time.monotonic()<until:time.sleep(.05)
            self.assertTrue(dead(pid))

if __name__=='__main__':unittest.main(verbosity=2)
