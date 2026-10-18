"""Saved-proof counterexamples: completeness, exposure and cached-effect forgery."""
import copy
import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch
import numpy as np
from .source import P
from .saved_audit import verify_archive,score_table,require_exact_files,audit_control_panel
from .controls import seed,reference
from .reference_evaluation import digest,effect_vector


def synthetic_panel(suite='N1'):
    subject='SYNTHETIC_SAVED_AUDIT';ids=np.arange(30);q=2400
    families=['B1','B2','B3','B4','D','C','S'];selected=['B1','B4'] if suite=='N3' else families
    scores={f:dict(LL=-100.-i,unit_bins=q) for i,f in enumerate(selected)}
    keys=[(0,)]*len(ids);cov=dict(trial_ids=ids.tolist(),available=True)
    meta=dict(D_trial_ids=ids.tolist(),role_bounds=[0,30],keys_N3=keys,coverage={suite:cov})
    events=[dict(event='SUITE_STARTED',subject=subject,suite=suite,coverage=cov,replicates=999)]
    vec=effect_vector(scores);observed=[scores['B4']['LL']/q]*6 if suite=='N3' else vec
    panel=dict(status='COMPLETE_FINITE_DESTRUCTIVE_REFERENCE',coverage=cov,replicates_completed=999,
               original_model_scores=scores,observed=observed,reference_effects=[],mapping_sha256=[],seeds=[],
               wheel_gain_original=vec[0] if suite=='N3' else None,wheel_gain_reference=[] if suite=='N3' else None,
               original_targets_preserved=True,D_filter_assimilates_surrogate_past_counts=suite!='N3')
    dummy=np.zeros((len(ids),20,8),int)
    for r in range(999):
        s=seed(suite,subject,'D',r)
        events.append(dict(event='REPLICATE_STARTED',replicate=r,seed=s))
        if r==0:events.append(dict(event='ORIGINAL_CONTROL_EXPOSURE',models=scores,trial_ids=ids.tolist()))
        _,_,mapping=reference(dummy,suite,ids,np.random.Generator(np.random.PCG64(s)),keys,[0,30]);mh=digest(mapping)
        values=[scores['B4']['LL']/q]*6 if suite=='N3' else vec
        gain=vec[0] if suite=='N3' else None
        events.append(dict(event='REPLICATE_COMPLETE',replicate=r,seed=s,mapping_sha256=mh,models=scores,reference_effects=values,wheel_gain=gain))
        panel['reference_effects'].append(values);panel['mapping_sha256'].append(mh);panel['seeds'].append(s)
        if suite=='N3':panel['wheel_gain_reference'].append(gain)
    events.append(dict(event='SUITE_COMPLETE',replicates_completed=999,summary_sha256=digest(panel)))
    return panel,events,subject,suite,meta,families


class SavedAudit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.fixture=synthetic_panel()

    def test_empty_manifest_denied(self):
        with self.assertRaises(AssertionError):verify_archive(dict(hashes={},external_hashes={}))

    def test_omitted_planned_certificate_denied(self):
        root=P/'work/saved_audit_tests';root.mkdir(parents=True,exist_ok=True)
        with tempfile.TemporaryDirectory(dir=root) as name:
            folder=Path(name);(folder/'present.json').write_text('{}')
            with patch('paper15_final1.saved_audit.P',folder):
                with self.assertRaises(AssertionError):require_exact_files(folder,{'present.json','missing.json'})
                with self.assertRaises(AssertionError):require_exact_files(folder,set())

    def test_wrong_score_exposure_and_missing_family_denied(self):
        with self.assertRaises(AssertionError):score_table({'B4':dict(LL=-1.,unit_bins=1)},4800,['B4'])
        with self.assertRaises(AssertionError):score_table({},4800,['B4'])

    def test_complete_999_synthetic_journal_verified(self):
        self.assertEqual(audit_control_panel(*self.fixture),999)

    def test_self_consistent_false_observed_gain_denied(self):
        args=copy.deepcopy(self.fixture);args[0]['observed']=[9.]*6
        args[1][-1]['summary_sha256']=digest(args[0])
        with self.assertRaises(AssertionError):audit_control_panel(*args)

    def test_missing_or_interrupted_journal_denied(self):
        args=copy.deepcopy(self.fixture);args[1].pop(10)
        with self.assertRaises(AssertionError):audit_control_panel(*args)
        args=copy.deepcopy(self.fixture);args[1][3]['event']='REPLICATE_FAILED_IMMUTABLE'
        with self.assertRaises(AssertionError):audit_control_panel(*args)

    def test_consistently_changed_seed_denied(self):
        args=copy.deepcopy(self.fixture);args[0]['seeds'][0]+=1;args[1][1]['seed']+=1;args[1][3]['seed']+=1
        args[1][-1]['summary_sha256']=digest(args[0])
        with self.assertRaises(AssertionError):audit_control_panel(*args)

    def test_consistently_changed_donor_mapping_denied(self):
        args=copy.deepcopy(self.fixture);args[0]['mapping_sha256'][0]='0'*64;args[1][3]['mapping_sha256']='0'*64
        args[1][-1]['summary_sha256']=digest(args[0])
        with self.assertRaises(AssertionError):audit_control_panel(*args)

    def test_consistently_changed_reference_effect_denied(self):
        args=copy.deepcopy(self.fixture);args[0]['reference_effects'][0]=[9.]*6;args[1][3]['reference_effects']=[9.]*6
        args[1][-1]['summary_sha256']=digest(args[0])
        with self.assertRaises(AssertionError):audit_control_panel(*args)

    def test_N3_copied_LL_and_wheel_gain_verified_separately(self):
        args=synthetic_panel('N3');self.assertEqual(audit_control_panel(*args),999)
        args[0]['wheel_gain_reference'][0]=9.;args[1][3]['wheel_gain']=9.
        args[1][-1]['summary_sha256']=digest(args[0])
        with self.assertRaises(AssertionError):audit_control_panel(*args)

    def test_unavailable_suite_cannot_hide_completed_draw(self):
        cov=dict(available=False,trial_ids=[]);subject='SYNTHETIC_UNAVAILABLE'
        panel=dict(status='UNAVAILABLE_REGISTERED_COVERAGE',coverage=cov,replicates_completed=0)
        events=[dict(event='SUITE_STARTED',subject=subject,suite='N4',coverage=cov,replicates=999),dict(event='UNAVAILABLE_REGISTERED_COVERAGE',coverage=cov)]
        self.assertEqual(audit_control_panel(panel,events,subject,'N4',dict(coverage={'N4':cov}),[]),0)
        events.insert(1,dict(event='REPLICATE_COMPLETE'))
        with self.assertRaises(AssertionError):audit_control_panel(panel,events,subject,'N4',dict(coverage={'N4':cov}),[])


if __name__=='__main__':unittest.main()
