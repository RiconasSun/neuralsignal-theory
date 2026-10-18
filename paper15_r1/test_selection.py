"""Synthetic global selection and role-gate tests, without B/E neural access."""
import unittest
import json
import tempfile
from pathlib import Path
from unittest.mock import patch
from .selection import groups,choose,nominal,require_stage,extract_role
from .training import configurations,sha
from .source import P


class SelectionTests(unittest.TestCase):
    def candidate(self,cid='B4_l0.1',ridge=.1,score=-.2,family='B4',rank=1):
        return dict(id=cid,configurations=[dict(id=cid,family=family,ridge=ridge,rank=rank,tau=.1)],
            available=True,equal_mouse_LL_per_unit_bin=score)
    def test_exact_candidate_groups_and_seed_membership(self):
        g=groups();self.assertEqual(len(g),37)
        self.assertEqual(len(g['D_k2_l0.01']),3);self.assertEqual(len(g['S_k4_l1.0']),3)
        self.assertEqual({x['seed'] for x in g['D_k2_l0.01']},{11,23,37})
    def test_stronger_ridge_within_exact_fixed_tie_band(self):
        a=self.candidate(ridge=.1,score=-.2);b=self.candidate('B4_l1.0',ridge=1.,score=-.2000005)
        self.assertEqual(choose([a,b])['id'],b['id'])
        b['equal_mouse_LL_per_unit_bin']=-.200002;self.assertEqual(choose([a,b])['id'],a['id'])
    def test_unavailable_candidate_never_wins(self):
        a=self.candidate();b=self.candidate('bad',score=1.);b['available']=False
        self.assertEqual(choose([a,b])['id'],a['id']);self.assertIsNone(choose([b]))
    def test_smaller_nominal_count_first_tie(self):
        a=self.candidate('C_rank2',family='C',rank=2);b=self.candidate('C_rank1',family='C',rank=1)
        self.assertEqual(choose([a,b])['id'],b['id'])
    def test_registered_static_capacity_pair(self):
        for kd in [2,3]:
            d=dict(family='D',k=kd);s=dict(family='S',k=kd+1)
            self.assertGreaterEqual(nominal(s),nominal(d))
    def test_final_roles_denied_before_stage_io(self):
        for role in ['C','D','A','FINAL']:
            with self.assertRaises(PermissionError):require_stage(role)
    def test_nonadmitted_or_Final_subject_denied_before_neural_io(self):
        with patch('paper15_r1.selection.require_stage'),patch('paper15_r1.selection.admitted',return_value=['dev']):
            with self.assertRaises(PermissionError):extract_role('FinalMouse','B')
    def test_E_gate_not_implicit_in_B(self):
        (P/'work/test_tmp').mkdir(parents=True,exist_ok=True)
        with tempfile.TemporaryDirectory(dir=P/'work/test_tmp') as d:
            root=Path(d);(root/'results').mkdir();(root/'fits/dev').mkdir(parents=True)
            configs=configurations();(root/'A_FIT_PLAN.json').write_text(json.dumps(dict(subjects=['dev'],configurations=configs)))
            for c in configs:(root/'fits/dev'/(c['id']+'.json')).write_text(json.dumps(dict(status='NUMERICAL_PASS')))
            for baseline,name in [(True,'BASELINE_ATTEMPTS_COMPLETE.json'),(False,'DYNAMIC_ATTEMPTS_COMPLETE.json')]:
                expected={'dev/'+c['id']:sha(root/'fits/dev'/(c['id']+'.json')) for c in configs if c['family'].startswith('B')==baseline}
                (root/'results'/name).write_text(json.dumps(dict(attempted=len(expected),completed=len(expected),attempt_hashes=expected,PRIMARY_BASELINE_NUMERICAL_GATE=True)))
            with patch('paper15_r1.selection.P',root),patch('paper15_r1.selection.admitted',return_value=['dev']):
                require_stage('B')
                with self.assertRaises(FileNotFoundError):require_stage('E')
                candidates=[dict(id='B1_l0.1',available=True,configurations=[dict(family='B1')]),dict(id='B4_l0.1',available=True,configurations=[dict(family='B4')])]
                (root/'results/B_CANDIDATE_SCORES.json').write_text(json.dumps(candidates))
                selection=dict(subjects=['dev'],selected=dict(B1='B1_l0.1',B4='B4_l0.1'),candidates_sha256=sha(root/'results/B_CANDIDATE_SCORES.json'))
                (root/'SELECTION_FREEZE.json').write_text(json.dumps(selection))
                (root/'E_EXPLORATORY_GATE.json').write_text(json.dumps(dict(approved_for_one_frozen_E_batch=False)))
                with self.assertRaises(AssertionError):require_stage('E')
                (root/'E_EXPLORATORY_GATE.json').write_text(json.dumps(dict(approved_for_one_frozen_E_batch=True,hashes={})))
                with self.assertRaises(AssertionError):require_stage('E')
                for name in ['models.py','features.py','training.py','selection.py']:(root/name).write_text('synthetic source identity')
                hashes={name:sha(root/name) for name in ['SELECTION_FREEZE.json','results/B_CANDIDATE_SCORES.json','models.py','features.py','training.py','selection.py']}
                (root/'E_EXPLORATORY_GATE.json').write_text(json.dumps(dict(approved_for_one_frozen_E_batch=True,hashes=hashes)))
                require_stage('E')
                selection['altered']=True;(root/'SELECTION_FREEZE.json').write_text(json.dumps(selection))
                with self.assertRaises(AssertionError):require_stage('E')
    def test_empty_attempt_marker_cannot_release_B(self):
        (P/'work/test_tmp').mkdir(parents=True,exist_ok=True)
        with tempfile.TemporaryDirectory(dir=P/'work/test_tmp') as d:
            root=Path(d);(root/'results').mkdir()
            (root/'A_FIT_PLAN.json').write_text(json.dumps(dict(subjects=['dev'],configurations=configurations())))
            (root/'results/BASELINE_ATTEMPTS_COMPLETE.json').write_text(json.dumps(dict(attempted=0,completed=0,attempt_hashes={},PRIMARY_BASELINE_NUMERICAL_GATE=True)))
            with patch('paper15_r1.selection.P',root),patch('paper15_r1.selection.admitted',return_value=['dev']):
                with self.assertRaises(AssertionError):require_stage('B')


if __name__=='__main__':unittest.main(verbosity=2)
