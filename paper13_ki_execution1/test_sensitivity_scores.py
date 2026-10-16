import unittest
from unittest.mock import patch
import numpy as np
from . import sensitivity_scores as s
from . import test_predictive as fixtures
from . import descriptive_metadata as descriptors
from .source import ALLOCATION,P
from .baseline_A import read
from .sensitivity_plan import shifted


class SensitivityScoreTests(unittest.TestCase):
    def fixture(self):
        y,q,bundle=fixtures.PredictiveTests().fixture();y=np.tile(y,(4,1,1))[:30];q=np.tile(q,(4,1,1))[:30]
        epochs=[{'ordinal':91+i,'partition':'E','start':i*5.,'stop':i*5.+3} for i in range(30)]
        bundle['training_partition']='A';bundle['units']=[{'unit_id':j,'label':'PL5' if j<5 else 'PL2/3'} for j in range(8)]
        bundle['sensitivity_unit_masks']={'first4':[True]*4+[False]*4,'rate4':[False]*4+[True]*4,'quality005':[True]*8,'deep_PL5_PL6a':[True]*5+[False]*3}
        bundle['sensitivity_metadata']={'recent_event':{str(e['ordinal']):i<7 for i,e in enumerate(epochs)},'provider_active':{str(e['ordinal']):False for e in epochs}}
        aligned={}
        for name,T in [('alignment_minus01',30),('alignment_plus01',29)]:
            bundle['sensitivity_metadata'][name]=shifted(epochs,-.1 if T==30 else .1,[-10,10000])
            aligned[name]={'counts':y[:,:T],'q':q[:,:T],'parent_ordinals':[e['ordinal'] for e in epochs],'unit_ids':list(range(8))}
        return y,q,bundle,{'role':'development','epochs':epochs},{'depth_rank_masks':{}},aligned

    def test_all_mandatory_panels_and_subthreshold_values_retained(self):
        args=self.fixture();out=s.score_mouse(*args)
        self.assertTrue(set(s.MANDATORY)<=set(out))
        self.assertEqual(out['first4']['retained_units'],4);self.assertEqual(out['first4']['nominal_unit_bins'],30*25*4)
        self.assertEqual(out['recent_event']['retained_epochs'],7);self.assertIsNotNone(out['recent_event']['scores']);self.assertFalse(out['recent_event']['coverage_eligible'])
        self.assertEqual(out['provider_active']['retained_epochs'],0);self.assertIsNone(out['provider_active']['scores'])
        self.assertEqual(out['alignment_plus01']['nominal_unit_bins'],30*24*8)
        self.assertEqual(out['label_PL']['retained_units'],0);self.assertIn('STRUCTURALLY_EMPTY',out['label_PL']['structural_status'])
        self.assertEqual(out['session_order_quartile1']['retained_epochs'],0)

    def test_final_c_role_required_and_alignment_parent_tamper_denied(self):
        y,q,bundle,record,d,aligned=self.fixture();record['role']='final'
        with self.assertRaises(PermissionError):s.score_mouse(y,q,bundle,record,d,aligned)
        record['role']='development';aligned['alignment_plus01']['parent_ordinals']=[]
        with self.assertRaises(ValueError):s.score_mouse(y,q,bundle,record,d,aligned)

    def test_six_contributors_never_become_eight_by_pooling_subthreshold(self):
        args=self.fixture();template=s.score_mouse(*args);mice=[str(i) for i in range(9)]
        import copy
        rows={m:copy.deepcopy(template) for m in mice}
        for m in mice[:6]:rows[m]['recent_event'].update(retained_epochs=10,coverage_eligible=True)
        result=s.aggregate(rows,mice);panel=result['panels']['recent_event']
        self.assertEqual(len(panel['contributing_mice']),6);self.assertFalse(panel['required_coverage_pass'])
        self.assertEqual(len(panel['computed_mice_including_subthreshold']),9)
        self.assertEqual(result['associated_broad_primary_verdict'],'INCONCLUSIVE_LOCKED_PRE_D_COVERAGE_AMENDMENT')
        self.assertFalse(result['optional_panels_can_rescue'])

    def test_saved_provider_DV_described_without_inventing_units_or_genotype(self):
        record=next(a for a in ALLOCATION if a['role']=='final');qc=read(P/'results/qc'/(record['mouse_id']+'.json'))
        out=descriptors.describe(record,qc['selected_units'])
        self.assertIn('DV',out['provider_coordinates']);self.assertEqual(sum(out['depth_rank_masks']['lower_raw_DV_rank4']),4)
        self.assertFalse(out['physical_depth_units_verified']);self.assertIn('NOT_DECODED',out['genotype'])
        self.assertFalse(out['independent_probe_replication'])

    def test_forbidden_response_bin_rows_nuisance_and_units_rejected_before_scoring(self):
        import copy
        base=self.fixture()
        changes=[('plus30',lambda a:a[-1]['alignment_plus01'].update(counts=a[0]+np.pad(np.full((30,1,8),1000),((0,0),(29,0),(0,0))),q=a[1])),
            ('minus29',lambda a:a[-1]['alignment_minus01'].update(counts=a[0][:,:29],q=a[1][:,:29])),
            ('extra_row',lambda a:a[-1]['alignment_plus01'].update(counts=np.zeros((31,29,8)),q=np.zeros((31,29,11)))),
            ('missing_row',lambda a:a[-1]['alignment_plus01'].update(counts=np.zeros((29,29,8)),q=np.zeros((29,29,11)))),
            ('qcols',lambda a:a[-1]['alignment_plus01'].update(q=np.zeros((30,29,10)))),
            ('qtime',lambda a:a[-1]['alignment_plus01'].update(q=np.zeros((30,30,11)))),
            ('units',lambda a:a[-1]['alignment_plus01'].update(unit_ids=list(reversed(range(8)))))]
        for label,change in changes:
            args=copy.deepcopy(base);change(args)
            with self.subTest(label=label),patch.object(s,'evaluate',side_effect=AssertionError('Forbidden aligned data reached scoring')):
                with self.assertRaises(ValueError):s.score_mouse(*args)

    def test_missing_inconsistent_plan_bounds_rejected_before_scoring(self):
        import copy
        base=self.fixture()
        for key,value in [('observed_full_bins',30),('export_stop',1000.),('original_tone',-1.),('start',4.)]:
            args=copy.deepcopy(base);args[2]['sensitivity_metadata']['alignment_plus01'][0][key]=value
            with self.subTest(key=key),patch.object(s,'evaluate',side_effect=AssertionError('Invalid plan reached scoring')):
                with self.assertRaises(ValueError):s.score_mouse(*args)
        args=copy.deepcopy(base);del args[2]['sensitivity_metadata']['alignment_plus01'][0]['export_stop']
        with patch.object(s,'evaluate',side_effect=AssertionError('Missing plan reached scoring')):
            with self.assertRaises(ValueError):s.score_mouse(*args)

    def test_empty_alignment_requires_empty_exact_arrays(self):
        y,q,bundle,record,desc,aligned=self.fixture();bundle['sensitivity_metadata']['alignment_plus01']=[]
        aligned['alignment_plus01']={'counts':np.zeros((0,29,8),dtype=int),'q':np.zeros((0,29,11)),
            'parent_ordinals':[],'unit_ids':list(range(8))}
        out=s.score_mouse(y,q,bundle,record,desc,aligned);self.assertIsNone(out['alignment_plus01']['scores'])
        self.assertEqual(out['alignment_plus01']['retained_epochs'],0)
        aligned['alignment_plus01']['counts']=np.zeros((1,29,8))
        with patch.object(s,'evaluate',side_effect=AssertionError('Hidden nonempty aligned data reached scoring')):
            with self.assertRaises(ValueError):s.score_mouse(y,q,bundle,record,desc,aligned)
