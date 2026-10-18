"""No protected inputs: D denial and exact frozen statistical/claim branches."""
import unittest
from unittest.mock import patch
import itertools
import numpy as np
from .d_support import raw_D
from .admission import verify_pre_D_gate
from .reference_metadata import control_coverage
from .statistics import CONTRASTS,PRIMARY,SECONDARY,sign_flip
from .final_statistics import analyze_final,claim_verdicts,MANDATORY_CASES


class DAdmissionStatistics(unittest.TestCase):
    def test_no_D_source_open_without_context(self):
        with patch('numpy.load',side_effect=AssertionError('Source must not open')) as loader:
            with self.assertRaises(PermissionError):raw_D('UCLA037',None)
            loader.assert_not_called()

    def test_empty_self_declared_preD_gate_denied(self):
        with patch('paper15_final1.admission.read',return_value={'approved_one_D_batch':True,'hashes':{}}):
            with self.assertRaises(PermissionError):verify_pre_D_gate()

    def test_metadata_coverage_without_D_draws_matches_original_operators(self):
        from .controls import reference
        ids=np.delete(np.arange(100),[5,17,39]);keys=[(int(i%2),int(i%3),int(i>=50)) for i in ids]
        expected=control_coverage(ids,keys,keys,[0,100]);dummy=np.zeros((len(ids),20,8),int)
        for suite in ['N1','N2','N3','N4']:
            _,ix,_=reference(dummy,suite,ids,np.random.Generator(np.random.PCG64(150107)),keys,[0,100])
            self.assertEqual(ids[ix].tolist(),expected[suite]['trial_ids'])

    def test_exact_sign_flips_and_fixed_secondary_slots(self):
        effects=np.array([.004,.002,-.001,.003,.005,.002])
        expected=sum(np.mean(np.array(s)*effects)>=effects.mean()-1e-14 for s in itertools.product([-1.,1.],repeat=6))/64
        self.assertEqual(sign_flip(effects),expected)
        subjects=[f'fixture{i}' for i in range(6)];families={f:subjects[:] for f in ['B0','B1','B2','B3','B4','C','D','S']}
        families['D']=subjects[:5]
        spec=dict(primary_subjects=subjects,family_subjects=families,contrast_subjects={k:[s for s in subjects if s in families[a] and s in families[b]] for k,(a,b) in CONTRASTS.items()})
        rows=[dict(subject=s,lab=f'lab{i%4}',models={f:dict(LL=10.+(effects[i]*1000 if f=='B4' else 0),unit_bins=1000) for f,ss in families.items() if s in ss}) for i,s in enumerate(subjects)]
        result=analyze_final(rows,spec)
        self.assertEqual(result['D-B4']['paired_sign_flip_p'],1.)
        self.assertEqual(result['D-S']['paired_sign_flip_p'],1.)
        self.assertEqual(result[PRIMARY]['n_mice'],6)
        self.assertTrue(all('Holm5_adjusted_p' in result[k] for k in SECONDARY))

    def test_favorable_statistics_cannot_promote_six_mouse_fallback(self):
        result=dict(n_mice=6,mouse_effects=[dict(subject=str(i),lab=f'lab{i%4}') for i in range(6)],
            CI95=[.004,.006],CI_width=.002,equal_mouse_mean=.005,paired_sign_flip_p=.015625,Holm5_adjusted_p=.03125,
            positive_mice=6,leave_one_mouse_out_means=[.005]*6,leave_one_lab_out_means={str(i):.005 for i in range(4)})
        stats={c:dict(result) for c in CONTRASTS}
        sens={s:{c:dict(n_mice=6,minimum6_coverage=True,equal_mouse_mean=.005) for c in ['B4-B1','B4-B3','B4-B2']} for s in MANDATORY_CASES}
        controls={c:{s:dict(n_mice=6,descriptive_disruption_gate=True) for s in ['N1','N2','N3','N4']} for c in CONTRASTS}
        spec=dict(source_main_numerical_valid=True,confirmatory_assumptions_defensible=False,static_capacity_pair_valid=True,mandatory_descriptive_only=True)
        verdict=claim_verdicts(stats,sens,controls,spec)
        self.assertTrue(all(v['verdict']=='DESCRIPTIVE ONLY' and not v['supported_under_complete_registered_conjunction'] for v in verdict.values()))


if __name__=='__main__':unittest.main()
