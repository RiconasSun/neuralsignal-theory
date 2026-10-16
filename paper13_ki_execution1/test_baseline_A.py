"""Synthetic A-runner admission, role, scheduling and request-identity checks."""
import json
import uuid
import unittest
from unittest.mock import patch
import numpy as np
from . import baseline_A as b


class BaselineRunnerTests(unittest.TestCase):
    def fixture(self):
        root=b.P/'work'/('baseline_runner_'+uuid.uuid4().hex);root.mkdir(parents=True)
        units=[{'unit_id':i,'row':i,'electrode_row':i,'label':'PL5'} for i in range(8)]
        epochs=[{'ordinal':i+1,'start':i*5.,'stop':i*5.+3,'partition':'A'} for i in range(60)]
        record={'mouse_id':'synthetic','role':'development','QC_partition':'A','epochs':epochs}
        state=root/'A.npz';y=np.random.default_rng(81).poisson(.1,(60,30,8))
        with state.open('xb') as f:np.savez_compressed(f,counts=y,unit_ids=np.arange(8))
        qc={'partition':'A','selected_units':units,'training_state_file':str(state),'training_state_sha256':b.sha(state.read_bytes()),'source_freeze':'QC-frozen'}
        return root,record,qc,y

    def test_exact_39_schedule_and_parameter_counts(self):
        schedule=b.schedule();self.assertEqual(len(schedule),39);self.assertEqual(len(set(schedule)),39)
        _,_,_,y=self.fixture();q=np.zeros((60,30,11))
        for name,n in [('B0',8),('B1',96),('B2',32),('B3',176),('B4',288)]:
            x,state=b.design_state(y,q,name);self.assertEqual(state['parameters'],n)
            self.assertEqual(x.size,60*30*n);self.assertTrue(np.isfinite(x).all())
        self.assertEqual([s for n,r,s in schedule if n=='B0'],[11,23,37])

    def test_missing_independent_approval_denies_before_state_loading(self):
        root,_,_,_=self.fixture()
        with patch.object(b,'P',root),patch.object(b.np,'load',side_effect=AssertionError('values before approval')):
            with self.assertRaisesRegex(PermissionError,'Independent M3'):b.approval()

    def test_failed_or_insufficient_M2_denies_before_values(self):
        for gate in [{'M2':'DATA_INSUFFICIENT'},{'M2':'PASS','eligible_development':['x'],'eligible_final':['y']}]:
            with patch.object(b,'require_access_approval',return_value={}),patch.object(b,'read',return_value=gate),patch.object(b,'completed_result',side_effect=AssertionError('QC before gate')):
                with self.assertRaises(b.ScientificStop):b.load_m2()

    def test_training_identity_and_final_value_denial(self):
        root,record,qc,y=self.fixture()
        got,ids,epochs=b.training_state(record,qc)
        np.testing.assert_array_equal(got,y);np.testing.assert_array_equal(ids,np.arange(8));self.assertEqual(len(epochs),60)
        final={**record,'role':'final','QC_partition':'C'}
        with patch.object(b.np,'load',side_effect=AssertionError('C values loaded')):
            with self.assertRaisesRegex(PermissionError,'A only'):b.training_state(final,{**qc,'partition':'C'})
        (root/'A.npz').write_bytes(b'changed')
        with self.assertRaisesRegex(b.ScientificStop,'state hash'):b.training_state(record,qc)

    def test_seed_A_objective_tolerance_and_required_failures(self):
        records=[{'identity':{'configuration':{'seed':seed}},'status':'PASS','objective':value} for seed,value in [(11,1.+5e-13),(23,1.),(37,2.)]]
        self.assertEqual(b.choose_seed(records)['identity']['configuration']['seed'],11)
        records[0]['status']='FAILED_REQUIRED_GATE'
        with self.assertRaises(b.ScientificStop):b.choose_seed(records)

    def test_full_synthetic_runner_identity_and_no_extra_fits(self):
        root,record,qc,y=self.fixture();(root/'results').mkdir()
        (root/'results/M2_GATE.json').write_text('{"synthetic":"gate"}')
        captured=[]
        def fake_fit(path,kind,data,ridge,initial,**kwargs):
            self.assertEqual(kind,'GLM');self.assertEqual(data['y'].shape,(60,30,8))
            identity=kwargs['identity'];self.assertEqual(identity['partition'],'A')
            self.assertEqual(kwargs['source_hash'],'approved-code')
            self.assertEqual(identity['A_state_sha256'],qc['training_state_sha256'])
            self.assertEqual(identity['unit_ids_sha256'],b.digest_arrays(np.arange(8)))
            self.assertEqual(identity['epochs_sha256'],b.sha(b.canonical(record['epochs'])))
            self.assertTrue(identity['scaler_sha256']);self.assertEqual(initial.size,data['x'].shape[-1]*8)
            captured.append(identity['configuration'])
            result={'status':'PASS','identity':identity,'PG':0.,'objective':1.,'iterations':1,'calls':1}
            path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(result));return result
        gate={'eligible_development':['synthetic']}
        with patch.object(b,'P',root),patch.object(b,'ALLOCATION',[record]),patch.object(b,'approval',return_value='approved-code'),patch.object(b,'load_m2',return_value=(gate,{'synthetic':qc})),patch.object(b,'nuisance',return_value=np.zeros((60,30,11))),patch.object(b,'fit',side_effect=fake_fit),patch('builtins.print'):
            b.run()
        self.assertEqual(len(captured),39)
        self.assertEqual({(x['baseline'],x['ridge'],x['seed']) for x in captured},set(b.schedule()))
        result=b.read(root/'results/M3_A_GATE.json')
        self.assertEqual(result['completed'],39);self.assertFalse(result['B_E_D_accessed'])
        self.assertFalse(result['C_values_loaded_by_this_runner'])


if __name__=='__main__':unittest.main(verbosity=2)
