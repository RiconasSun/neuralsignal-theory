import json
import uuid
import unittest
from unittest.mock import patch
from . import development_bundle as d


class BundleTests(unittest.TestCase):
    def fixture(self):
        root=d.P/'work'/('bundle_tests_'+uuid.uuid4().hex)
        mouse='synthetic';baselines={};families={}
        qc={'mouse_id':mouse,'role':'development','partition':'A','training_state_sha256':'A-state',
            'selected_units':[{'unit_id':i} for i in range(8)],'attempts':[{'unit_id':i,'pass':True} for i in range(8)]}
        m3={'selected_baselines':{name:{'selected_ridge':1} for name in ['B0','B1','B2','B3','B4']},'strongest_baseline':{'B_star':'B2'}}
        for name in m3['selected_baselines']:
            p=root/'results/m3_A/preprocessing'/(mouse+'_'+name+'.json');p.parent.mkdir(parents=True,exist_ok=True)
            p.write_text(json.dumps({'baseline':name}),encoding='utf8')
            for seed in d.f.SEEDS:
                baselines[(mouse,name,1,seed)]={'status':'PASS','objective':1 if seed in [23,37] else 2,'theta':[seed],
                    'identity':{'configuration':{'seed':seed},'scaler_sha256':d.sha(p.read_bytes())},'full_request_sha256':name+str(seed)}
        for p in [.5,.9]:
            for seed in d.f.SEEDS:
                families[(mouse,d.f.D_key(p,.1,seed))]={'status':'PASS','objective':0 if seed==37 else 1,'theta':[seed]*16,
                    'identity':{'configuration':{'seed':seed}},'full_request_sha256':str(p)+str(seed)}
        m4={'D_selection':{'selected_configuration':{'p':.9,'ridge':.1}},'S_selection':{'selected_ridge':.1},
            'C_selection':{'selected_configuration':{'tau':[.1,.3],'ridge':1,'seed':23}}}
        p=root/'results/m4/preprocessing'/mouse/'C_tau0.1-0.3_seed23.json';p.parent.mkdir(parents=True,exist_ok=True)
        p.write_text(json.dumps({'Q':[[1,0]]*8}),encoding='utf8')
        families[(mouse,d.f.C_key([.1,.3],1,23))]={'theta':[23]*16,'identity':{'scaler_sha256':d.sha(p.read_bytes())},'full_request_sha256':'C23'}
        return root,mouse,qc,baselines,m3,families,m4

    def test_complete_bundle_uses_A_objective_and_global_C_seed(self):
        root,*args=self.fixture()
        with patch.object(d,'P',root):out=d.build(*args)
        self.assertEqual(out['Bstar'],'B2')
        self.assertEqual(set(out['source_fit_requests']),{'B0','B1','B2','B3','B4','D','S','C'})
        self.assertEqual(out['baseline_thetas']['B4'],[23])
        self.assertEqual(out['D']['A_selected_seed'],37)
        self.assertEqual(out['S']['p'],.5)
        self.assertEqual(out['C']['seed'],23)
        self.assertEqual(out['training_state_sha256'],'A-state')

    def test_final_role_or_wrong_partition_denied(self):
        root,mouse,qc,*rest=self.fixture()
        with patch.object(d,'P',root):
            for override in [{'role':'final'},{'partition':'C'},{'mouse_id':'wrong'}]:
                with self.assertRaises(PermissionError):d.build(mouse,{**qc,**override},*rest)

    def test_corrupt_selected_scaler_fails_before_evaluation(self):
        root,*args=self.fixture()
        p=root/'results/m3_A/preprocessing/synthetic_B4.json';p.write_text('{}',encoding='utf8')
        with patch.object(d,'P',root):
            with self.assertRaises(d.ScientificStop):d.build(*args)

    def test_incomplete_family_gate_denied(self):
        with patch.object(d.f,'approved',return_value='frozen'),patch.object(d.f,'prior_gates',return_value=({}, {}, {}, {})):
            with patch.object(d.b,'read',side_effect=[{'M4_A_NUMERICS':'PASS','required':540,'completed':539,'fits':[]},{'M4':'PASS'}]):
                with self.assertRaises(d.ScientificStop):d.gates()
