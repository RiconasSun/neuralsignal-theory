"""Synthetic metadata-only contract tests. No neural/scientific worker import."""
import copy,unittest,time
from unittest.mock import patch
import numpy as np
from . import metadata_compat as m

def fixture(explicit=False):
    a=np.arange(150,dtype=np.float64)*2
    arrays={'start':a,'stop':a+.25,'id':np.arange(150,dtype=np.int64)+1000,'ordinal':np.arange(150,dtype=np.int64),
        'color':np.tile([-1.,1.],75),'main_valid':np.ones(150,bool),'invalid_intervals':np.array([[2.05,2.07],[10.1,10.12]])}
    arrays['main_valid'][[1,5]]=False
    if explicit:arrays['stimulus_invalid_intervals']=np.array([[10.1,10.12]])
    inv={'start_time':[2.05,4.05,10.1],'stop_time':[2.07,4.07,10.12],
        'tags':['EcephysProbe','7','probeA','EcephysProbe','8','probeB','EcephysSession','123','stimulus'],'tags_index':[3,6,9]}
    header={'session_id':123,'decoded_neural_values':False,'all_interval_names':['flashes_presentations','invalid_times'],'tables':{'invalid_times':inv}}
    item={'session_id':123,'probe_id':7};probes=[{'id':7,'name':'probeA'},{'id':8,'name':'probeB'}]
    return header,item,probes,arrays,arrays['main_valid'].copy()

class MetadataTests(unittest.TestCase):
    def test_both_variants_exact_stimulus_vs_support_and_no_mutation(self):
        outputs=[]
        for explicit in [False,True]:
            args=fixture(explicit);before={k:m.array_identity(v) for k,v in args[3].items()};out=m.derive(*args)
            self.assertTrue(out['stimulus_valid'][1]);self.assertFalse(out['original_main_valid'][1]);self.assertFalse(out['stimulus_valid'][5])
            self.assertEqual(before,{k:m.array_identity(v) for k,v in args[3].items()});self.assertTrue(out['complete_validity_equal_original']);outputs.append(out)
        self.assertEqual(outputs[0]['stimulus_valid'],outputs[1]['stimulus_valid'])
        self.assertEqual(outputs[0]['stimulus_invalid_intervals'],outputs[1]['stimulus_invalid_intervals'])

    def test_absence_requires_complete_native_inventory_not_missing_field(self):
        header,item,probes,arrays,common=fixture();header['all_interval_names']=['flashes_presentations'];header['tables']={}
        app,stim,proof=m.labeled_invalidity(header,item,probes);self.assertEqual(app.shape,(0,2));self.assertEqual(stim.shape,(0,2));self.assertIn('VERIFIED_ABSENT',proof['status'])
        for changes in [{'all_interval_names':None},{'all_interval_names':['invalid_times']},{'tables':None}]:
            with self.assertRaises(m.ProvenanceStop):m.labeled_invalidity({**header,**changes},item,probes)

    def test_session_probe_global_labels_original_scope(self):
        header,item,probes,*_=fixture()
        for scope,scope_id,label,applies,is_stim in [('EcephysSession','123','all_probes',True,False),('EcephysSession','123','stimulus',True,True),('EcephysSession','123','optotagging',True,False),('EcephysProbe','7','probeA',True,False),('EcephysProbe','8','probeB',False,False)]:
            header['tables']['invalid_times']={'start_time':[1.],'stop_time':[2.],'tags':[scope,scope_id,label],'tags_index':[3]}
            app,stim,_=m.labeled_invalidity(header,item,probes);self.assertEqual(len(app),int(applies));self.assertEqual(len(stim),int(is_stim))

    def test_malformed_unknown_scopes_tags_indices_intervals(self):
        header,item,probes,*_=fixture();base=header['tables']['invalid_times']
        variants=[{'tags':['Unknown','7','probeA']+base['tags'][3:]},{'tags':['EcephysSession','999','stimulus']+base['tags'][3:]},
            {'tags':['EcephysProbe','7','wrong']+base['tags'][3:]},{'tags_index':[True,6,9]},{'tags_index':[3,3,9]},
            {'stop_time':[2.05,4.07,10.12]},{'start_time':[float('nan'),4.05,10.1]},{'tags':base['tags']+['unused']},{'tags':[3]+base['tags'][1:]}]
        for change in variants:
            bad=copy.deepcopy(header);bad['tables']['invalid_times']={**base,**change}
            with self.subTest(change=change),self.assertRaises(m.ProvenanceStop):m.labeled_invalidity(bad,item,probes)

    def test_missing_native_table_fields_and_partial_error_fail(self):
        for field in ['start_time','stop_time','tags','tags_index']:
            header,item,probes,*_=fixture();del header['tables']['invalid_times'][field]
            with self.assertRaises(m.ProvenanceStop):m.labeled_invalidity(header,item,probes)
        header,item,probes,*_=fixture()
        for change in [{'error':'partial header'},{'session_id':999},{'decoded_neural_values':True}]:
            with self.assertRaises(m.ProvenanceStop):m.labeled_invalidity({**header,**change},item,probes)

    def test_conflicting_saved_complete_or_stimulus_intervals_stop(self):
        args=fixture(True);args[3]['stimulus_invalid_intervals'][0,0]+=.001
        with self.assertRaises(m.ContractStop):m.derive(*args)
        args=fixture();args[3]['invalid_intervals'][0,0]+=.001
        with self.assertRaises(m.ContractStop):m.derive(*args)

    def test_no_main_valid_substitution_or_mask_redefinition(self):
        args=fixture();args[3]['main_valid'][1]=True
        with self.assertRaises(m.ContractStop):m.derive(*args)
        args=fixture();args[4][1]=True
        with self.assertRaises(m.ContractStop):m.derive(*args)
        args=fixture();args[4][:90]=False
        with self.assertRaises(m.ContractStop):m.derive(*args)

    def test_original_dtype_order_role_and_archive_denial(self):
        for field in ['start','stop','invalid_intervals']:
            args=fixture();args[3][field]=args[3][field].astype(np.float32)
            with self.assertRaises(m.ProvenanceStop):m.derive(*args)
        args=fixture();args[3]['ordinal'][1]=9
        with self.assertRaises(m.ProvenanceStop):m.derive(*args)
        args=fixture();args[3]['spike_times']=np.array([1.])
        with self.assertRaises(m.ProvenanceStop):m.derive(*args)

    def test_corrupt_archive_wrong_hash_missing_path_no_decode(self):
        root=m.P/'work'/('test_metadata_'+str(time.time_ns()));root.mkdir(parents=True)
        path=root/'good.npz';np.savez_compressed(path,**fixture()[3]);out=m.read_archive(path,m.sha(path));self.assertEqual(len(out['start']),150)
        with patch.object(m.np,'load',side_effect=AssertionError('Must stop before decode')):
            with self.assertRaises(m.ProvenanceStop):m.read_archive(path,'0'*64)
            with self.assertRaises(m.ProvenanceStop):m.read_archive(root/'missing.npz','0'*64)
        path=root/'corrupt.npz';path.write_bytes(b'not a numpy archive')
        with self.assertRaises(m.ProvenanceStop):m.read_archive(path,m.sha(path))

    def test_unregistered_source_identity_denied_before_archive_or_network(self):
        row=copy.deepcopy(m.records()[0]);row['source']['session_id']+=1
        with patch.object(m.np,'load',side_effect=AssertionError('No neural/archive open')):
            with self.assertRaises(m.ProvenanceStop):m.read_input(row)

if __name__=='__main__':unittest.main(verbosity=2)
