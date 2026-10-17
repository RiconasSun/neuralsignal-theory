import unittest
from .audit import task,region,support_inventory,units,validate_references,verify_subject,TP,UP,EP

def fixture():
    v={TP+k:[] for k in ['start_time','gabor_stimulus_onset_time','auditory_cue_time','feedback_time','stop_time','probability_left','gabor_stimulus_contrast','gabor_stimulus_side']}
    for block in range(8):
        for j in range(30):
            t=3*(block*30+j)
            for k,x in zip(['start_time','gabor_stimulus_onset_time','auditory_cue_time','feedback_time','stop_time','probability_left','gabor_stimulus_contrast','gabor_stimulus_side'],[t,t+.2,t+.21,t+1.,t+2.,.2 if block%2==0 else .8,25.,'left']):v[TP+k].append(x)
    return v

class CanonicalAuditTests(unittest.TestCase):
    def test_documented_filename_alias_preserves_original_subject(self):
        r=dict(mouse='A_1',canonical_subject='A-1');x=dict(values={'/general/subject/subject_id':'A_1'});official=dict(wasAttributedTo=[dict(schemaKey='Participant',identifier='A_1')])
        self.assertEqual(verify_subject(r,x,official),'A_1')
    def test_alias_cannot_substitute_another_animal(self):
        with self.assertRaises(ValueError):verify_subject(dict(mouse='A_1',canonical_subject='A-1'),dict(values={'/general/subject/subject_id':'B_1'}),dict(wasAttributedTo=[dict(schemaKey='Participant',identifier='B_1')]))
    def test_source_reference_bound_to_electrodes(self):
        validate_references(dict(schema=[dict(path=UP+'max_electrode',attrs=dict(table=EP.rstrip('/'),neurodata_type='DynamicTableRegion'))]))
    def test_wrong_source_reference_fails_closed(self):
        with self.assertRaises(ValueError):validate_references(dict(schema=[dict(path=UP+'max_electrode',attrs=dict(table='/units',neurodata_type='DynamicTableRegion'))]))
    def test_canonical_only_no_old_masks_or_movement_required(self):
        v=fixture();s,r,rows=task(v);self.assertTrue(s['potential_task_capacity']);self.assertEqual(set(s['cell_trials'].values()),{60});self.assertEqual(s['original_cut'],4)
    def test_old_masks_and_movement_cannot_change_validity(self):
        v=fixture();a=task(v);v[TP+'bwm_include']=[False]*240;v[TP+'saturation_stim_plus06']=[True]*240;v[TP+'wheel_movement_onset_time']=[None]*240
        self.assertEqual(a,task(v))
    def test_original_cut_before_event_exclusions(self):
        v=fixture();v[TP+'feedback_time'][:60]=[None]*60;s,r,_=task(v);self.assertEqual(s['original_cut'],4);self.assertFalse(s['potential_task_capacity']);self.assertEqual(s['cell_trials']['0.8_evaluation'],60)
    def test_fifteen_trial_qualifying_run(self):
        v=fixture();v[TP+'feedback_time'][:16]=[None]*16;s,r,_=task(v);self.assertFalse(r[0]['qualifying'])
    def test_original_window_inside_trial(self):
        v=fixture();v[TP+'stop_time'][0]=.6;s,_,rows=task(v);self.assertIn('stimulus_window_outside_trial',rows[0]['exclusion_reasons'])
    def test_context_order_not_randomized(self):
        v=fixture();v[TP+'probability_left'][20]=.5;s,r,rows=task(v);self.assertEqual(rows[20]['half'],'nonprimary');self.assertEqual(s['original_runs'],9)
    def test_future_event_order_invalid(self):
        v=fixture();v[TP+'auditory_cue_time'][0]=.1;self.assertIn('invalid_event_order',task(v)[2][0]['exclusion_reasons'])
    def test_exact_anatomical_descendants(self):
        self.assertEqual(region('MOs6a'),'MOs');self.assertEqual(region('PL2/3'),'PL');self.assertIsNone(region('MOp5'));self.assertIsNone(region('MOsAdjacent'))
    def test_task_epochs_not_observation_certificate(self):
        s=support_inventory(dict(values={'/intervals/epochs/start_time':[0.],'/intervals/epochs/stop_time':[100.]}));self.assertTrue(s['task_epoch_present']);self.assertEqual(s['neural_recording_coverage'],'UNKNOWN');self.assertIsNone(s['source_support_eligible'])
    def test_empty_undocumented_artifact_table_never_pass(self):
        s=support_inventory(dict(values={'/intervals/invalid_times/start_time':[],'/intervals/invalid_times/stop_time':[]}));self.assertNotEqual(s['documented_artifact_validity'],'PASS');self.assertIsNone(s['source_support_eligible'])
    def test_observation_intervals_not_artifact_certificate(self):
        s=support_inventory(dict(values={'/units/obs_intervals':[[0.,100.]]}));self.assertEqual(s['documented_artifact_validity'],'UNKNOWN');self.assertIsNone(s['source_support_eligible'])
    def test_canonical_unit_electrode_atlas_mapping(self):
        v={UP+'id':[0,1],UP+'cluster_uuid':['a','b'],UP+'probe_name':['Probe00']*2,UP+'max_electrode':[0,1],UP+'ibl_quality_score':[1.,1.],EP+'id':[0,1],EP+'group_name':['Probe00']*2,EP+'x':[1.,2.],EP+'y':[1.,2.],EP+'z':[1.,2.]}
        prefix='/general/localization/ElectrodesIBLBregma/';v.update({prefix+'brain_region':['MOs5','PL6a'],prefix+'localized_entity':[0,1],prefix+'probe_name':['Probe00']*2})
        s,rows=units(v,'probe00');self.assertEqual(s['qualified_target_units'],2);self.assertEqual(s['non_MOs_units'],1)
        v[UP+'probe_name'][0]='Probe01'
        with self.assertRaises(ValueError):units(v,'probe00')

if __name__=='__main__':unittest.main()
