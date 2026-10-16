import copy
import json
import uuid
import unittest
from unittest.mock import patch
import numpy as np
from . import final_D as d
from . import test_calibration_state as states


class PriorTests(unittest.TestCase):
    def fixture(self):
        root=d.P/'work'/('D_prior_tests_'+uuid.uuid4().hex);root.mkdir(parents=True)
        def save(path,value):
            path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(d.b.canonical(value)+b'\n');return d.sha(path.read_bytes())
        mice=['synthetic'+str(j) for j in range(9)];allocation=[{'mouse_id':m,'role':'final','epochs':[]} for m in mice]
        m3={'selected_baselines':{name:{'selected_ridge':.1 if name=='B0' else 1.} for name in d.PARAMETERS},'strongest_baseline':{'B_star':'B2'}}
        m4={'D_selection':{'selected_configuration':{'p':.9,'ridge':.1}},'S_selection':{'selected_ridge':.1},
            'C_selection':{'selected_configuration':{'tau':[.3,1.],'seed':11,'ridge':1.}}}
        configurations=[{'baseline':name,'ridge':m3['selected_baselines'][name]['selected_ridge'],'seed':seed} for name in d.PARAMETERS for seed in [11,23,37]]
        configurations += [{'family':name,'p':p,'ridge':.1,'seed':seed} for name,p in [('D',.9),('S',.5)] for seed in [11,23,37]]
        configurations += [{'family':'C',**m4['C_selection']['selected_configuration']}]
        gate={'FINAL_C_NUMERICS':'PASS','source_freeze':'C-source','required':198,'completed':198,'mouse_order':mice,'fits':[],'models':{}}
        for mouse in mice:
            bundle=states.StateTests().fixture();bundle['mouse_id']=mouse;bundle['all_C_fit_requests']={};bundle['source_fit_requests']={}
            bundle['D']['ridge']=.1;bundle['S']['ridge']=.1;bundle['C']['ridge']=1.
            for j,configuration in enumerate(configurations):
                name=configuration.get('baseline',configuration.get('family'));theta=bundle['baseline_thetas'][name] if name in d.PARAMETERS else bundle[name]['theta']
                zero=np.zeros(len(theta));error=d.m.gradient_errors(zero,zero)
                cert={'pass':True,'numerical_gate_step':1e-4,'theta':theta,'analytical_gradient':zero.tolist(),
                    'independent_AD_gradient':zero.tolist(),'fixed_FD_gradient':zero.tolist(),'AD_error':error,'fixed_FD_error':error}
                request=mouse+'_'+str(j);path=root/'fits'/(request+'.json')
                result={'status':'PASS','real_data':True,'source_hash':'C-source','identity':{'mouse_id':mouse,'partition':'C','configuration':configuration},
                    'PG':0.,'objective':1.,'iterations':1,'calls':1,'theta':theta,'full_request_sha256':request,
                    'derivatives':{point:copy.deepcopy(cert) for point in ['initial','intermediate_first_callback','endpoint']}}
                digest=save(path,result);gate['fits'].append({'path':str(path.relative_to(root)).replace('\\','/'),'sha256':digest,'mouse_id':mouse})
                bundle['all_C_fit_requests'][str(j)]=request
                if name not in bundle['source_fit_requests']:bundle['source_fit_requests'][name]=request
            path=root/'models'/(mouse+'.json');digest=save(path,bundle)
            gate['models'][mouse]={'path':str(path.relative_to(root)).replace('\\','/'),'sha256':digest}
        sealed={'COMPLETE_C_STATE':'PASS','mouse_order':mice,'models':copy.deepcopy(gate['models'])}
        save(root/'results/FINAL_C_GATE.json',gate);save(root/'results/FINAL_C_FULL_STATE_MANIFEST.json',sealed)
        save(root/'results/M6_E_CONTROLS_GATE.json',{'M6_E_CONTROLS':'PASS'})
        save(root/'results/M3_BASELINE_SELECTION.json',m3);save(root/'results/M4_MODEL_SELECTION.json',m4)
        save(root/'PRE_D_STOPPING_RULE_AMENDMENT.json',{'known_failed_gate':{'immutable_associated_claim_verdict':'INCONCLUSIVE'},'final_D_outcome_access_before_amendment':False})
        return root,allocation,gate,sealed,save

    def test_full_synthetic198_roster_certificates_and_model_states(self):
        root,allocation,*_=self.fixture()
        with patch.object(d,'P',root),patch.object(d,'ROOT',root),patch.object(d,'ALLOCATION',allocation),patch.object(d,'SourceReader',side_effect=AssertionError('Daccessduringprerelease')):
            gate,sealed,models=d.prior_gates()
        self.assertEqual(len(models),9);self.assertEqual(len(gate['fits']),198)

    def test_duplicate_fit_or_incomplete_all_coordinate_certificate_denied(self):
        root,allocation,gate,sealed,save=self.fixture();original=copy.deepcopy(gate)
        gate['fits'][1]=copy.deepcopy(gate['fits'][0]);save(root/'results/FINAL_C_GATE.json',gate)
        with patch.object(d,'P',root),patch.object(d,'ROOT',root),patch.object(d,'ALLOCATION',allocation):
            with self.assertRaises(d.ScientificStop):d.prior_gates()
            gate=original;item=gate['fits'][0];path=root/item['path'];r=d.b.read(path);r['derivatives']['endpoint']['fixed_FD_gradient']=[]
            item['sha256']=save(path,r);save(root/'results/FINAL_C_GATE.json',gate)
            with self.assertRaises(d.ScientificStop):d.prior_gates()

    def test_incomplete_C_model_vector_denied_even_with_updated_outer_hashes(self):
        root,allocation,gate,sealed,save=self.fixture();mouse=gate['mouse_order'][0];path=root/gate['models'][mouse]['path'];model=d.b.read(path)
        model['baseline_thetas']['B4']=[0.];digest=save(path,model);gate['models'][mouse]['sha256']=digest;sealed['models'][mouse]['sha256']=digest
        save(root/'results/FINAL_C_GATE.json',gate);save(root/'results/FINAL_C_FULL_STATE_MANIFEST.json',sealed)
        with patch.object(d,'P',root),patch.object(d,'ROOT',root),patch.object(d,'ALLOCATION',allocation):
            with self.assertRaises(ValueError):d.prior_gates()
