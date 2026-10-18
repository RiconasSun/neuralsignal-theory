"""Synthetic end-to-end prediction/reference integration; no real E or fitting."""
import copy
import unittest
import json
import tempfile
from pathlib import Path
from unittest.mock import patch
import numpy as np
from scipy.special import logsumexp
from .evaluation_support import control_arrays,FrozenPredictors,pre_epoch_wheel,raw_E,source_state
from .evaluation import effect_vector,control_summary,sensitivity_summary,verify_E_gate,run_controls,append_event
from .features import design,dct_state,scale
from .controls import history_from_microbins
from .training import build_model
from .source import P
from .source import dump
from .training import sha
from .sensitivities import CASES


class EvaluationTests(unittest.TestCase):
    def setUp(self):
        rng=np.random.Generator(np.random.PCG64(19))
        y=rng.poisson(.2,(4,20,2));nx=rng.normal(0,.2,(4,20,37));h=history_from_microbins(y)
        x,scales,active=design(nx,h,10)
        self.arrays=dict(x=x,y=y,active=active,trial_ids=np.array([10,12,15,18]));self.prep=dict(scales=scales,C_scales={})
        for rank in [1,2]:
            for tau in [.1,.25]:
                key=f'C_r{rank}_tau{tau}';q,cs=dct_state(y,rank,tau)
                self.arrays[key]=q;self.arrays[key+'_active']=np.array(cs['q_scale']['active']);self.prep['C_scales'][key]=cs
    def predictors(self):
        p=FrozenPredictors.__new__(FrozenPredictors);p.parameters={};p.configs={}
        for family in ['B0','B1','B2','B3','B4','D','C','S']:
            configs=[dict(family=family,k=2 if family=='D' else 3,rank=1,tau=.1,ridge=.1,seed=s) for s in ([11,23,37] if family in ('D','S') else [11])]
            p.configs[family]=configs;p.parameters[family]=[build_model(self.arrays,c).initialize(c['seed']) for c in configs]
        return p
    def test_donor_history_changes_only_history_state_and_D_past(self):
        ix=np.array([0,2]);surrogate=self.arrays['y'][[1,3]]
        out=control_arrays(self.arrays,self.prep,surrogate,ix)
        np.testing.assert_array_equal(out['y'],self.arrays['y'][ix])
        np.testing.assert_array_equal(out['x'][:,:,:38],self.arrays['x'][ix,:,:38])
        expected=scale(history_from_microbins(surrogate),{k:self.prep['scales'][k][37:] for k in ['mean','sd','active']})
        np.testing.assert_array_equal(out['x'][:,:,38:],expected)
        for key,cs in self.prep['C_scales'].items():
            q,_=dct_state(surrogate,cs['rank'],cs['tau'],10,cs);np.testing.assert_array_equal(out[key],q)
    def test_wheel_only_indices_and_original_history_C_state(self):
        ix=np.array([0,2]);donors=np.array([1,3]);out=control_arrays(self.arrays,self.prep,self.arrays['y'][donors],ix,donors)
        np.testing.assert_array_equal(out['x'][:,:,24:38],self.arrays['x'][donors,:,24:38])
        for cols in [slice(None,24),slice(38,None)]:np.testing.assert_array_equal(out['x'][:,:,cols],self.arrays['x'][ix,:,cols])
        np.testing.assert_array_equal(out['C_r1_tau0.1'],self.arrays['C_r1_tau0.1'][ix])
    def test_ensemble_is_prebin_logmass_mean_not_sequence_mean(self):
        p=self.predictors();actual=p.score(self.arrays)
        for family in ['D','S']:
            masses=[build_model(self.arrays,c).prebin_logmasses(t) for c,t in zip(p.configs[family],p.parameters[family])]
            expected=(logsumexp(np.stack(masses),axis=0)-np.log(3))[:,10:].sum()
            self.assertAlmostEqual(actual[family]['LL'],expected,12)
            self.assertEqual(actual[family]['unit_bins'],80)
    def test_D_filter_uses_surrogate_past_and_original_current_target(self):
        p=self.predictors();c=p.configs['D'][0];model=build_model(self.arrays,c);theta=p.parameters['D'][0]
        surrogate=self.arrays['y'].copy();surrogate[:,12]+=10
        original=model.prebin_logmasses(theta);changed=model.prebin_logmasses(theta,surrogate)
        np.testing.assert_array_equal(original[:,:13],changed[:,:13])
        self.assertGreater(np.max(np.abs(original[:,13:]-changed[:,13:])),1e-8)
    def test_strict_pre_epoch_wheel_and_A_threshold_inputs(self):
        metadata=dict(trials=[dict(stimOn_times=2.)]);wt=np.array([0.,.9,1.,1.4,1.5,2.]);wp=np.array([0.,1.,99.,3.,200.,5.])
        np.testing.assert_array_equal(pre_epoch_wheel(metadata,[0],wt,wp),[2.])
    def test_missing_model_preserves_effect_slots_and_Q_mismatch_denied(self):
        scores=dict(B4=dict(LL=10.,unit_bins=100),B1=dict(LL=5.,unit_bins=100))
        self.assertEqual(effect_vector(scores),[.05,None,None,None,None,None])
        scores['B1']['unit_bins']=99
        with self.assertRaises(AssertionError):effect_vector(scores)
    def test_finite_reference_summary_pseudocount_and_fixed4_holm(self):
        rows=[]
        for i in range(6):
            panel=dict(status='COMPLETE_FINITE_DESTRUCTIVE_REFERENCE',observed=[1.]*6,reference_effects=[[0.]*6]*999)
            rows.append(dict(subject=str(i),suites={k:copy.deepcopy(panel) for k in ['N1','N2','N3','N4']}))
        subjects=[r['subject'] for r in rows];result=control_summary(rows,subjects)
        for panels in result.values():
            for p in panels.values():self.assertEqual(p['p_reference'],.001);self.assertEqual(p['Holm4_reference_p'],.004)
        rows[0]['suites']['N1']=dict(status='UNAVAILABLE_REGISTERED_COVERAGE')
        self.assertEqual(control_summary(rows,subjects)['B4-B1']['N1']['p_reference'],1.)
        bad=copy.deepcopy(rows);bad[-1]['subject']=bad[0]['subject']
        with self.assertRaises(AssertionError):control_summary(bad,subjects)
        with self.assertRaises(AssertionError):control_summary(rows[:-1],subjects)
    def test_unavailable_sensitivity_retained_without_dynamic_robustness(self):
        rows=[dict(subject='x',lab='l',case=c['id'],status='UNAVAILABLE') for c in CASES]
        result=sensitivity_summary(rows,['x'])
        self.assertEqual(len(result),11);self.assertEqual(set(result['S01']),{'B4-B1','B4-B3','B4-B2'})
        self.assertFalse(result['S01']['B4-B1']['minimum6_coverage'])
        with self.assertRaises(AssertionError):sensitivity_summary(rows+[rows[0]],['x'])
        with self.assertRaises(AssertionError):sensitivity_summary(rows[:-1],['x'])
    def test_Final_subject_rejected_before_source_or_neural_read(self):
        with patch('paper15_r1.evaluation_support.admitted',return_value=['dev']):
            with self.assertRaises(PermissionError):source_state('final')
    def test_missing_E_gate_blocks_before_neural_read(self):
        with patch('paper15_r1.evaluation.require_stage',side_effect=PermissionError('not staged')):
            with self.assertRaises(PermissionError):verify_E_gate()
    def refmeta(self):
        return dict(E_trial_ids=self.arrays['trial_ids'].tolist(),role_bounds=[10,30],
            coverage={s:dict(available=s=='N1',trial_ids=self.arrays['trial_ids'].tolist(),epochs=4,total_epochs=4) for s in ['N1','N2','N3','N4']})
    def test_interruption_preserves_prefix_seed_failure_and_denies_repeat(self):
        (P/'work/test_tmp').mkdir(parents=True,exist_ok=True)
        predictor=self.predictors();original=predictor.score;calls=[]
        def fail(arrays,**kwargs):
            calls.append(kwargs)
            if len(calls)==3:raise RuntimeError('injected second-replicate interruption')
            return original(arrays,**kwargs)
        predictor.score=fail
        with tempfile.TemporaryDirectory(dir=P/'work/test_tmp') as temp:
            root=Path(temp)
            with self.assertRaises(RuntimeError):run_controls('synthetic',self.arrays,predictor,self.prep,self.refmeta(),root)
            events=[json.loads(x) for x in (root/'N1.jsonl').read_text().splitlines()]
            completed=[x for x in events if x['event']=='REPLICATE_COMPLETE']
            self.assertEqual(len(completed),1);self.assertNotIn('B0',completed[0]['models'])
            self.assertEqual(len(completed[0]['models']),7)
            self.assertEqual(events[-1]['event'],'REPLICATE_FAILED_IMMUTABLE');self.assertEqual(events[-1]['replicate'],1)
            prefix=(root/'N1.jsonl').read_bytes()
            with self.assertRaises(FileExistsError):run_controls('synthetic',self.arrays,predictor,self.prep,self.refmeta(),root)
            self.assertEqual(prefix,(root/'N1.jsonl').read_bytes())
    def test_missing_journal_cannot_be_silently_regenerated(self):
        with tempfile.TemporaryDirectory(dir=P/'work/test_tmp') as temp:
            with self.assertRaises(FileNotFoundError):append_event(Path(temp)/'missing.jsonl',dict(event='COMPLETE'))
    def test_all_unavailable_cases_still_bound_and_required_before_E(self):
        (P/'work/test_tmp').mkdir(parents=True,exist_ok=True)
        with tempfile.TemporaryDirectory(dir=P/'work/test_tmp') as temp:
            root=Path(temp);subject='dev'
            for rel in ['evaluation.py','evaluation_support.py','controls.py','statistics.py','sensitivities.py','sensitivity_fits.py',
                'models.py','features.py','training.py','selection.py','independent_ad.py','source.py','reader.py','source_integrity.py',
                'SOURCE_FILE_FREEZE.json','NEURAL_HEADER_FREEZE.json','READER_GATE.json','results/M2_PHYSIOLOGY_GATE.json','PRODUCTION_GATE.json',
                'engineering.md','mathematics.md','results/dev_A_QC.json']:
                dump(root/rel,dict(synthetic=True))
            selected=dict(subjects=[subject],selected={f:f for f in ['B0','B1','B2','B3','B4']})
            dump(root/'paper15_m1/PROTOCOL_FREEZE.json',dict(synthetic=True))
            dump(root/'results/dev_A_QC.json',dict(selected_unit_ids=[0,1]))
            dump(root/'metadata/dev_task.json',dict(subject=subject,synthetic=True))
            dump(root/'states/dev_A_PREPROCESSING.json',dict(subject=subject,role='A',units=[0,1],
                QC_sha256=sha(root/'results/dev_A_QC.json'),task_sha256=sha(root/'metadata/dev_task.json'),
                M1_freeze_sha256=sha(root/'paper15_m1/PROTOCOL_FREEZE.json')))
            dump(root/'PRODUCTION_GATE.json',dict(PRODUCTION_NUMERICAL_PASS=True,
                hashes={'states/dev_A_PREPROCESSING.json':sha(root/'states/dev_A_PREPROCESSING.json')}))
            dump(root/'READER_GATE.json',dict(approved_for_A_only=True,hashes={'metadata/dev_task.json':sha(root/'metadata/dev_task.json')}))
            dump(root/'SELECTION_FREEZE.json',selected)
            candidates=[dict(id=f,available=True,configurations=[dict(family=f,ridge=.1)]) for f in selected['selected']]
            dump(root/'results/B_CANDIDATE_SCORES.json',candidates)
            records=[]
            for case in CASES:
                item=dict(subject=subject,case=case['id'],status='UNAVAILABLE',reasons=['registered capacity'])
                records.append(item)
                dump(root/'sensitivity_states'/subject/(case['id']+'.json'),dict(subject=subject,case=case,status='UNAVAILABLE',
                    B_selection_sha256=sha(root/'SELECTION_FREEZE.json'),source_QC_sha256=sha(root/'results/dev_A_QC.json'),unavailability_reasons=item['reasons']))
            dump(root/'results/SENSITIVITY_PREPARATION.json',dict(cases=CASES,records=records))
            dump(root/'SENSITIVITY_FIT_PLAN.json',dict(attempts=[],expected_attempts=0,max_retries=0,new_hyperparameter_search=False,
                Final_fits=0,maximum_Development=550,maximum_all_registered_sensitivities=1100,
                B_selection_sha256=sha(root/'SELECTION_FREEZE.json'),solver=dict(maxiter=2000,maxfun=80000,maxls=40,ftol=1e-12,gtol=1e-6)))
            dump(root/'results/SENSITIVITY_ATTEMPTS_COMPLETE.json',dict(attempted=0,completed=0,records=[]))
            dump(root/'REFERENCE_METADATA_FREEZE.json',dict(subjects=[subject],records=[dict(subject=subject,
                A_preprocessing_sha256=sha(root/'states/dev_A_PREPROCESSING.json'),task_sha256=sha(root/'metadata/dev_task.json'))],replicates=999,suites=['N1','N2','N3','N4']))
            sg_files=['SENSITIVITY_FIT_PLAN.json','SELECTION_FREEZE.json','results/B_CANDIDATE_SCORES.json','results/SENSITIVITY_PREPARATION.json',
                'models.py','independent_ad.py','features.py','sensitivities.py','sensitivity_fits.py','PRODUCTION_GATE.json']
            dump(root/'SENSITIVITY_GATE.json',dict(approved_for_fixed_A_sensitivity_refits=True,hashes={rel:sha(root/rel) for rel in sg_files}))
            hashes={p.relative_to(root).as_posix():sha(p) for p in root.rglob('*') if p.is_file()}
            gate=dict(approved_for_one_frozen_E_batch=True,subjects=[subject],E_batches=1,Final_access=False,hashes=hashes,
                independent_review_evidence={role:dict(path=role+'.md',sha256=sha(root/(role+'.md'))) for role in ['engineering','mathematics']})
            dump(root/'E_EXPLORATORY_GATE.json',gate)
            with patch('paper15_r1.evaluation.P',root),patch('paper15_r1.evaluation.R',root),patch('paper15_r1.evaluation.admitted',return_value=[subject]),patch('paper15_r1.evaluation.require_stage'):
                verify_E_gate()
                for missing_main in ['states/dev_A_PREPROCESSING.json','metadata/dev_task.json','results/dev_A_QC.json']:
                    removed=gate['hashes'].pop(missing_main);dump(root/'E_EXPLORATORY_GATE.json',gate)
                    with self.assertRaises(AssertionError):verify_E_gate()
                    gate['hashes'][missing_main]=removed
                dump(root/'E_EXPLORATORY_GATE.json',gate)
                missing='sensitivity_states/dev/S11.json';del gate['hashes'][missing];dump(root/'E_EXPLORATORY_GATE.json',gate)
                with self.assertRaises(AssertionError):verify_E_gate()
                gate['hashes'][missing]=sha(root/missing);dump(root/'E_EXPLORATORY_GATE.json',gate)
                state=json.loads((root/missing).read_text());state['unavailability_reasons']=[];dump(root/missing,state)
                with self.assertRaises(AssertionError):verify_E_gate()
                state['unavailability_reasons']=['registered capacity'];dump(root/missing,state)
                dump(root/'metadata/dev_task.json',dict(subject=subject,tampered=True))
                with self.assertRaises(AssertionError):verify_E_gate()


if __name__=='__main__':unittest.main()
