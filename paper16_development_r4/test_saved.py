"""Pure saved arithmetic regressions; no neural/model functions imported."""
import unittest
from . import reproduce_saved as saved


class SavedTests(unittest.TestCase):
    def test_unknown_or_partial_call_record_never_counted_as_complete(self):
        a={'event':'RESERVED_BEFORE_EVALUATION','call':1,'iterations':0,'x':[0.]}
        self.assertEqual(saved.prior.call_prefix([a],1),(1,0))
        with self.assertRaises(RuntimeError):saved.prior.call_prefix([{'event':'COMPLETED','call':1}],1)
        with self.assertRaises(RuntimeError):saved.prior.call_prefix([{**a,'call':2}],1)

    def test_full_coordinate_diagnostic_prefix_keeps_frozen_step(self):
        d=[{'kind':'ANALYTIC_RESERVED','checkpoint':'initial','index':1},
           {'kind':'AD_RESERVED','checkpoint':'initial','index':1}]
        self.assertEqual(saved.prior.diagnostic_prefix(d,1),{'FD_RESERVED':0,'AD_RESERVED':1,'ANALYTIC_RESERVED':1})
        with self.assertRaises(RuntimeError):saved.prior.diagnostic_prefix(d+[{'kind':'FD_RESERVED','checkpoint':'initial','index':1,'h':.003,'coordinate':0,'side':'plus'}],1)

    def test_bound_signs_do_not_zero_inward_gradient(self):
        import numpy as np
        np.testing.assert_array_equal(saved.prior.projected(np.array([-1.,1.,-1.,1.]),np.array([2.,-3.,-4.,5.]),-1,1),[0.,0.,-4.,5.])

    def test_missing_and_tampered_manifest_fail_closed(self):
        from unittest.mock import patch
        with self.assertRaises(RuntimeError):saved.identities({'files':[{'path':'paper16_development_r4/MISSING_REQUIRED_STATE','sha256':'0'*64}]})
        row={'path':'paper16_development_r4/UNIFORM_NUMERICAL_AMENDMENT.json','sha256':'0'*64}
        with self.assertRaises(RuntimeError):saved.identities({'files':[row]})

    def test_duplicate_or_wrong_terminal_events_rejected(self):
        a={'event':'ATTEMPTED','task':{'id':'one'},'ftol':0.0}
        b={'event':'COMPLETED','task':{'id':'one'}}
        for rows in [[b],[a,a],[a,{**b,'task':{'id':'other'}}],[a,b,b]]:
            with self.subTest(rows=rows),self.assertRaises(RuntimeError):saved.strict_journal(rows)
        attempts,terminal,active=saved.strict_journal([a,b])
        self.assertEqual(len(attempts),1);self.assertIsNone(active)
        self.assertEqual(terminal['one'],b)

    def test_no_new_task_after_first_failed_mandatory_attempt(self):
        a={'event':'ATTEMPTED','task':{'id':'one'}}
        f={'event':'FAILED','task':a['task'],'retry':False,'error_type':'NumericalStop','message':'required gate'}
        self.assertIsNone(saved.strict_journal([a,f])[2])
        with self.assertRaises(RuntimeError):saved.strict_journal([a,f,{'event':'ATTEMPTED','task':{'id':'two'}}])
        with self.assertRaises(RuntimeError):saved.strict_journal([a,{**f,'retry':True}])

    def test_native_supervision_is_not_inferred_from_missing_files(self):
        with self.assertRaises(RuntimeError):saved.abnormal({})
        s={'returncode':1,'killed_at_deadline':False,'completed_before_deadline':True,
           'native_job_tree_enforced':True,'assigned_before_resume':True,'clock_failure':None}
        self.assertTrue(saved.abnormal(s));self.assertFalse(saved.abnormal({**s,'returncode':0}))

    def test_M4_review_decision_string_without_binding_does_not_pass(self):
        import tempfile,json
        from pathlib import Path
        from unittest.mock import patch
        with tempfile.TemporaryDirectory(dir=saved.P/'work') as name:
            root=Path(name);e=root/'ops/evidence/2026-10-20/p16-m3-m5-uniform-numerical-amendment-r4';e.mkdir(parents=True)
            (e/'M4_APPROVAL.json').write_text(json.dumps({'decision':'ACCEPTED_R4_COMPLETE_M4','open_P0':0,'open_P1':0}))
            with patch.object(saved,'R',root):
                with self.assertRaises((KeyError,RuntimeError,FileNotFoundError)):saved.verify_m4()

    def test_consumed_attempt_before_folder_creation_is_preserved(self):
        import tempfile,json
        from pathlib import Path
        from unittest.mock import patch
        with tempfile.TemporaryDirectory(dir=saved.P/'work') as name:
            p=Path(name);(p/'results').mkdir()
            stage=saved.load(saved.P/'results/STAGE_CLAIM.json')
            def write(path,value):path.write_text(json.dumps(value),encoding='utf-8')
            write(p/'results/STAGE_CLAIM.json',stage)
            write(p/'results/SUPERVISOR.json',{'original_stage_sha256':saved.sha(p/'results/STAGE_CLAIM.json')})
            write(p/'results/SUPERVISION.json',{'returncode':1,'killed_at_deadline':False,'completed_before_deadline':True,
                  'native_job_tree_enforced':True,'assigned_before_resume':True,'clock_failure':None})
            plan=saved.load(saved.P/'NEW_TASK_PLAN_CANDIDATE.json');write(p/'NEW_TASK_PLAN_CANDIDATE.json',plan)
            task=plan['tasks'][0];attempt={'event':'ATTEMPTED','task':task,'ftol':0.0}
            failure={'event':'FAILED','task':task,'error_type':'ImplementationStop','message':'constructor error','retry':False}
            (p/'results/FIT_JOURNAL.jsonl').write_text(json.dumps(attempt)+'\n'+json.dumps(failure)+'\n')
            write(p/'results/SCIENTIFIC_STOP.json',{'no_retry':True,'all_later_tasks_not_executed':True})
            with patch.object(saved,'P',p):
                out,states=saved.facts()
            self.assertEqual((out['new_optimizer_attempts'],out['incomplete_attempted_tasks'],out['new_numerical_passes']),(1,1,0))
            self.assertIsNone(states[0]['numerical_pass'])

    def test_incomplete_accepted_vectors_need_bounds_finiteness_and_FG_identity(self):
        import numpy as np
        initial={k:np.array([v]) for k,v in [('x0',0.),('lo',-1.),('hi',1.)]}
        calls=[{'event':'RESERVED_BEFORE_EVALUATION','call':1,'iterations':0,'x':[0.]},
               {'event':'COMPLETED','call':1,'gradient':[0.],'gradient_inf':0.,'objective':1.}]
        self.assertEqual(saved.accepted_prefix(calls,[{'iteration':1,'x':[0.]}],initial),(1,1))
        for x in [[float('nan')],[2.],[.1],[0.,0.]]:
            with self.subTest(x=x),self.assertRaises(RuntimeError):saved.accepted_prefix(calls,[{'iteration':1,'x':x}],initial)

    def test_missing_initializer_cannot_hide_later_artifacts(self):
        import tempfile
        from pathlib import Path
        with tempfile.TemporaryDirectory(dir=saved.P/'work') as name:
            folder=Path(name);saved.pre_fit_prefix(folder)
            for n in ['CALLS.jsonl','CLIENT.json','ACCEPTED.jsonl','DIAGNOSTIC_CALLS.jsonl','endpoint.npz']:
                p=folder/n;p.write_bytes(b'')
                with self.assertRaises(RuntimeError):saved.pre_fit_prefix(folder)
                p.unlink()

    def test_empty_refit_effects_nonfinite_scores_or_wrong_difference_denied(self):
        row={'absolute':{'B1':-.2,'B4':-.1},'effects':{'B4-B1':.1}}
        saved.scalar_effects(row,['B1','B4'],['B4-B1'])
        for bad in [{**row,'effects':{}},{**row,'absolute':{'B1':float('nan'),'B4':-.1}},
                    {**row,'effects':{'B4-B1':.2}}]:
            with self.assertRaises(RuntimeError):saved.scalar_effects(bad,['B1','B4'],['B4-B1'])

    def test_N2_saved_summaries_preserve_seven_models_allow_C_variation(self):
        row={'absolute':{k:-.1 for k in ['B0','B1','B2','B3','B4','C','D','S']}}
        saved.n2_invariant({'absolute':{**row['absolute'],'C':-.2}},row)
        for model in ['B0','B1','B2','B3','B4','D','S']:
            with self.subTest(model=model),self.assertRaises(RuntimeError):saved.n2_invariant({'absolute':{**row['absolute'],model:0.}},row)

    def test_E_exports_reject_duplicate_or_unregistered_sessions_before_decode(self):
        account={'m':{'source':{'session_id':1}}}
        for rows in [[{'role':'E','session_id':2}],[{'role':'E','session_id':1},{'role':'E','session_id':1}]]:
            with self.assertRaises(RuntimeError):saved.exports(rows,account)


if __name__=='__main__':unittest.main(verbosity=2)
