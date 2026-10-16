import copy
import uuid
import unittest
from unittest.mock import patch
import numpy as np
from . import final_D as d
from paper13_ki_execution1 import test_calibration_state as states
from paper13_ki_execution1 import test_predictive as prediction
from paper13_ki_execution1.sensitivity_plan import shifted


class IntegrationTests(unittest.TestCase):
    def fixture(self):
        root=d.P/'work'/('D_integration_tests_'+uuid.uuid4().hex);root.mkdir(parents=True)
        (root/'PRE_D_STOPPING_RULE_AMENDMENT.json').write_text('{}',encoding='utf8')
        mice=['synthetic'+str(j) for j in range(9)];allocation=[];models={};descriptors={}
        for mouse in mice:
            epochs=[{'ordinal':i+1,'start':10.+5*i,'stop':13.+5*i,'partition':'C' if i<60 else 'D'} for i in range(120)]
            record={'mouse_id':mouse,'role':'final','epochs':epochs};allocation.append(record)
            model=states.StateTests().fixture();model['mouse_id']=mouse
            model['sensitivity_metadata']={name:shifted(epochs,shift,[0,1000]) for name,shift in [('alignment_minus01',-.1),('alignment_plus01',.1)]}
            model['sensitivity_metadata'].update(recent_event={str(e['ordinal']):True for e in epochs},provider_active={str(e['ordinal']):False for e in epochs})
            models[mouse]=model;descriptors[mouse]={'depth_rank_masks':{'lower_raw_DV_rank4':[True]*4+[False]*4},
                'documented_conditions':['synthetic'],'genotype':'NOT_DECODED_FROM_SOURCE','provider_coordinates':{'DV':list(range(8))},'probe_id':'probe0'}
        y,_,_=prediction.PredictiveTests().fixture();y=np.tile(y,(8,1,1))[:60]
        def export(record,bundle,folder,journal):
            sets=d.window_sets(record,bundle)
            receipt={'state_sha256':'synthetic-derived-state','parent_ordinals':{name:[e['ordinal'] for e in value['epochs']] for name,value in sets.items()},'unit_ids':list(range(8))}
            arrays={'primary_counts':y.copy(),'alignment_minus01_counts':y.copy(),'alignment_plus01_counts':y[:,:29].copy()}
            return receipt,sets,arrays
        c={'mouse_order':mice,'models':{mouse:{'sha256':'synthetic-model'} for mouse in mice}}
        sealed={'descriptive_metadata':descriptors}
        return root,allocation,c,sealed,models,export

    def test_coupled_primary_sensitivity_statistics_and_once_rule_with_stubbed_null_loop(self):
        root,allocation,c,sealed,models,export=self.fixture()
        with patch.object(d,'P',root),patch.object(d,'ROOT',root),patch.object(d,'ALLOCATION',allocation),patch.object(d,'approved',return_value='synthetic-source'),patch.object(d,'prior_gates',return_value=(c,sealed,models)),patch.object(d,'export',side_effect=export) as source,patch.object(d,'nuisance',side_effect=lambda record,epochs:np.zeros((len(epochs),30,11))),patch.object(d,'run_controls',return_value={'synthetic_stub_only':True,'replicates_per_suite':999}) as nulls,patch.object(d,'SourceReader',side_effect=AssertionError('Real source in synthetic integration')),patch('builtins.print'):
            d.run()
            with self.assertRaises(FileExistsError):d.run()
        result=d.b.read(root/'results/FINAL_D_RESULTS.json')
        self.assertEqual(result['FINAL_D_EXECUTION'],'VALIDLY_COMPLETED_ONCE_DESCRIPTIVE');self.assertEqual(len(result['per_mouse']),9)
        self.assertEqual(source.call_count,9);self.assertEqual(nulls.call_count,1)
        self.assertTrue(result['null_controls']['synthetic_stub_only'])
        for name in ['D_minus_B4','C_minus_B4','D_minus_C']:self.assertIn('INCONCLUSIVE',result['statistics']['contrasts'][name]['final_claim_status'])
        self.assertTrue(result['sensitivity_report']['all_mandatory_panel_names_preserved'])
        self.assertTrue(result['descriptive_group_dependence']['individual_probe_leaveout_equals_mouse_leaveout'])
        self.assertEqual(result['fits_or_model_selection_on_D'],0);self.assertFalse(result['D_reassessment_authorized'])

    def test_required_null_failure_keeps_primary_evidence_and_never_restarts(self):
        root,allocation,c,sealed,models,export=self.fixture();failure=ValueError('injected required null failure')
        failure.final_control_context={'stage':'null_control','suite':'conditional_Bstar','replicate':0,'mouse_id':c['mouse_order'][0]}
        with patch.object(d,'P',root),patch.object(d,'ROOT',root),patch.object(d,'ALLOCATION',allocation),patch.object(d,'approved',return_value='synthetic-source'),patch.object(d,'prior_gates',return_value=(c,sealed,models)),patch.object(d,'export',side_effect=export) as source,patch.object(d,'nuisance',side_effect=lambda record,epochs:np.zeros((len(epochs),30,11))),patch.object(d,'run_controls',side_effect=failure),patch('builtins.print'):
            with self.assertRaises(ValueError):d.run()
            with self.assertRaises(FileExistsError):d.run()
        failed=d.b.read(root/'results/FINAL_D_FAILURE.json');self.assertEqual(failed['context'],failure.final_control_context)
        self.assertTrue(failed['one_shot_marker_consumed']);self.assertFalse(failed['retry_or_post_D_repair_authorized'])
        partial=d.b.read(root/'results/final_D/primary_results.json');self.assertEqual(len(partial['per_mouse']),9)
        self.assertFalse((root/'results/FINAL_D_RESULTS.json').exists());self.assertEqual(source.call_count,9)
