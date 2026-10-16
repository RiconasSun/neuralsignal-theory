import json
import uuid
import unittest
from unittest.mock import patch
import numpy as np
from . import final_C as c


class CalibrationTests(unittest.TestCase):
    def fixture(self):
        root=c.P/'work'/('final_C_tests_'+uuid.uuid4().hex);root.mkdir(parents=True)
        y=np.random.default_rng(313).poisson(.2,(60,30,8));state=root/'state.npz'
        with state.open('xb') as f:np.savez_compressed(f,counts=y,unit_ids=np.arange(8))
        (root/'PRE_D_STOPPING_RULE_AMENDMENT.json').write_text('{}',encoding='utf8')
        record={'mouse_id':'synthetic','role':'final','QC_partition':'C','epochs':[{'ordinal':i+1,'start':i*5.,'stop':i*5.+3,'partition':'C'} for i in range(60)]}
        units=[{'unit_id':i,'label':'PL5'} for i in range(8)]
        qc={'mouse_id':'synthetic','role':'final','partition':'C','training_state_file':'state.npz','training_state_sha256':c.sha(state.read_bytes()),
            'selected_units':units,'source_freeze':'QC-code','attempts':[{'unit_id':i,'pass':True,'rate_hz':1.,'refractory_fraction':0.} for i in range(8)]}
        m3={'selected_baselines':{name:{'selected_ridge':ridge} for name,ridge in [('B0',.1),('B1',10.),('B2',.1),('B3',1.),('B4',1.)]},'strongest_baseline':{'B_star':'B2'}}
        m4={'D_selection':{'selected_configuration':{'p':.9,'ridge':.1}},'S_selection':{'selected_ridge':.1},
            'C_selection':{'selected_configuration':{'tau':[.1,.3],'ridge':1.,'seed':23}}}
        return root,record,qc,y,m3,m4

    def test_missing_C_review_denies_before_policy_or_count_values(self):
        root,*_=self.fixture()
        with patch.object(c,'P',root),patch.object(c,'policies',side_effect=AssertionError('policy before review')):
            with self.assertRaises(PermissionError):c.run()

    def test_A_B_D_or_wrong_mouse_denied_before_saved_count_open(self):
        root,record,qc,*_=self.fixture()
        with patch.object(c.np,'load',side_effect=AssertionError('wrongrolecountaccess')):
            for changed in [{**record,'role':'development'},{**record,'QC_partition':'D'},{**record,'mouse_id':'wrong'}]:
                with self.assertRaises(PermissionError):c.load_C(changed,qc)

    def test_invalid_C_hash_or_units_fail_closed(self):
        root,record,qc,*_=self.fixture()
        with patch.object(c,'ROOT',root):
            with self.assertRaises(c.ScientificStop):c.load_C(record,{**qc,'training_state_sha256':'wrong'})
            with self.assertRaises(c.ScientificStop):c.load_C(record,{**qc,'selected_units':list(reversed(qc['selected_units']))})

    def test_complete22_from_scratch_frozen_schedule_shared_offset_and_state(self):
        root,record,qc,y,m3,m4=self.fixture();captured=[];offsets=[];out=root/'results/final_C';out.mkdir(parents=True);journal=out/'test_actions.jsonl'
        def fake_fit(path,kind,data,ridge,initial,**kw):
            i=kw['identity'];cfg=i['configuration'];captured.append((kind,cfg,initial.copy()))
            self.assertEqual(i['partition'],'C');self.assertEqual(i['C_state_sha256'],qc['training_state_sha256'])
            np.testing.assert_array_equal(data['y'],y);self.assertEqual(kw['source_hash'],'reviewed-C-code')
            if kind in ['HMM','C']:offsets.append(kw['offset'].copy());self.assertEqual(initial.shape,(16,))
            value={'status':'PASS','theta':initial.tolist(),'identity':i,'full_request_sha256':path.stem,
                'PG':0.,'objective':0. if cfg['seed']==23 else 1.,'iterations':1,'calls':1}
            path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(value),encoding='utf8');return value
        with patch.object(c,'P',root),patch.object(c,'ROOT',root),patch.object(c,'nuisance',return_value=np.zeros((60,30,11))),patch.object(c,'fit',side_effect=fake_fit),patch.object(c.sensitivity_plan,'metadata',return_value={'synthetic':'metadata'}),patch('builtins.print'):
            rows,identity=c.fit_mouse(record,qc,m3,m4,'reviewed-C-code',out,journal)
        self.assertEqual(len(rows),22);self.assertEqual(len(captured),22)
        self.assertEqual(sum(k=='GLM' for k,_,_ in captured),15);self.assertEqual(sum(k=='HMM' for k,_,_ in captured),6);self.assertEqual(sum(k=='C' for k,_,_ in captured),1)
        for offset in offsets[1:]:np.testing.assert_array_equal(offset,offsets[0])
        model=json.loads((root/identity['path']).read_text());self.assertEqual(model['training_partition'],'C');self.assertEqual(model['Bstar'],'B2')
        self.assertEqual(model['D']['C_selected_seed'],23);self.assertEqual(model['S']['C_selected_seed'],23)
        self.assertEqual(model['C']['seed'],23);self.assertEqual(len(model['all_C_fit_requests']),22)
        self.assertEqual(set(model['source_fit_requests']),{'B0','B1','B2','B3','B4','D','C','S'})
        np.testing.assert_allclose(model['C']['state']['count_mean'],y.mean(axis=(0,1)),rtol=0,atol=0)
        for name in model['baseline_scalers']:
            raw,_=c.m.raw_features(y,np.zeros((60,30,11)),name);expected=c.m.fit_scale(raw)
            np.testing.assert_array_equal(model['baseline_scalers'][name]['mean'],expected['mean'])
        self.assertEqual(model['sensitivity_unit_masks']['first4'],[True]*4+[False]*4)

    def test_required_fit_failure_stops_once_and_keeps_error_gate(self):
        root,record,qc,y,m3,m4=self.fixture();gate={'eligible_final':['synthetic']}
        with patch.object(c,'P',root),patch.object(c,'approved',return_value='reviewed'),patch.object(c,'policies',return_value=(gate,m3,m4)),patch.object(c,'ALLOCATION',[record]),patch.object(c.b,'read',return_value=qc),patch.object(c,'completed_result',return_value=qc),patch.object(c,'fit_mouse',side_effect=c.ScientificStop('injected frozen PG failure')) as fit:
            with self.assertRaises(c.ScientificStop):c.run()
            with self.assertRaises(FileExistsError):c.run()
            self.assertEqual(fit.call_count,1)
        failed=json.loads((root/'results/FINAL_C_GATE.json').read_text());self.assertEqual(failed['FINAL_C_NUMERICS'],'FAIL');self.assertFalse(failed['D_outcomes_accessed'])
