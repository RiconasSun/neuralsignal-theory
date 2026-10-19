import unittest
import numpy as np
from .analysis_oracles import *
from .spec import glm,scored_log_rate,histories
class AnalysisTests(unittest.TestCase):
 def test_selection_rejects_every_invalid_row_and_protocol_switch(self):
  records=[{'lambda':lam,'mouse_id':i,'protocol':'BO' if i<5 else 'FC','logscore':-1.} for lam in [.01,.1,1.] for i in range(28)]
  badsets=[records+[{'lambda':99,'mouse_id':999,'protocol':'UNKNOWN','logscore':float('nan')}],
   [{**x,'protocol':'UNKNOWN' if x['mouse_id']==27 else x['protocol']} for x in records],
   [{**x,'protocol':'FC' if x['mouse_id']==0 and x['lambda']==.1 else x['protocol']} for x in records],
   records+[records[0]],records[:-1]]
  badsets.append([{'lambda':lam,'mouse_id':i,'protocol':'BO' if i<3 else ('FC' if i<13 else 'UNKNOWN'),'logscore':-1.} for lam in [.01,.1,1.] for i in range(14)])
  for field,value in [('lambda',99),('logscore',float('nan')),('mouse_id',''),('mouse_id',True),('protocol','UNKNOWN')]:
   badsets.append([{**records[0],field:value}]+records[1:])
  for rows in badsets:
   with self.subTest(rows=rows[:1]),self.assertRaises(ValueError):select_lambda(rows)
 def test_controls_secondary_family_consistency(self):
  from pathlib import Path
  import json
  root=Path(__file__).resolve().parents[1]
  cfg=json.loads((root/'protocol.json').read_text(encoding='utf8'));controls=json.loads((root/'controls.json').read_text(encoding='utf8'))
  self.assertEqual(cfg['secondary_contrasts'],['B4-B2','B4-B3','D-B4','C-B4','D-S'])
  self.assertEqual(next(x for x in controls['sensitivities'] if x['id']=='S08')['RNG_replicates'],'MainHolm5/pairedsignflips')
  self.assertNotIn('Holm3',json.dumps(controls))
 def test_saved_reproduction_denies_network_neural_files(self):
  from .verify import saved_scope
  import requests,urllib.request,h5py
  with saved_scope():
   for fn in [lambda:requests.get('https://example.invalid'),lambda:urllib.request.urlopen('https://example.invalid'),lambda:h5py.File('never_open_real.nwb','r'),lambda:np.load('never_open_spikes.npy')]:
    with self.assertRaises(RuntimeError):fn()
 def test_B0_B4_all_nested_identities_and_positive_PSTH_curvature(self):
  rng=np.random.Generator(np.random.PCG64(16063));X=np.c_[np.tile(np.eye(12),(3,1)),rng.uniform(-.2,.2,(36,12))];y=rng.poisson(.5,36).astype(float);dt=np.full(36,.02)
  rate=scored_log_rate(y,dt);b=np.r_[np.full(12,rate),np.zeros(12)]
  base=glm([rate],np.ones((36,1)),y,dt,.1,1)[0];self.assertAlmostEqual(glm(b,X,y,dt,.1)[0],base,places=12)
  for extra in [3,6,10]:
   value,grad=glm(np.r_[b,np.zeros(extra)],np.c_[X,rng.uniform(0,1,(36,extra))],y,dt,.1)
   self.assertAlmostEqual(value,base,places=12);np.testing.assert_allclose(grad[:24],glm(b,X,y,dt,.1)[1],atol=1e-14)
  H=X.T@(np.exp(X@b)[:,None]*dt[:,None]*X)/36+np.diag(np.r_[np.zeros(12),np.full(12,.1)])
  self.assertGreater(np.linalg.eigvalsh(H).min(),0)
  spikes=[np.array([0,.025,.075]),np.array([.03,.09])];np.testing.assert_array_equal(histories(spikes,0,5),histories(spikes,0,10,.01))
 def test_training_QC_occupancy_ISI_gaps_future_and_role(self):
  windows=[(i*2,i*2+.22) for i in range(30)];spikes=np.array([x for a,b in windows for x in [a+.01,a+.03]])
  result=physiological_summary(spikes,windows,'A');self.assertTrue(result['pass']);self.assertEqual(result['occupied'],30);self.assertEqual(result['ISI_pairs'],30)
  self.assertEqual(result,physiological_summary(np.r_[spikes,999.],windows,'A'))
  for role in ['B','E','D']:
   with self.assertRaises(ValueError):physiological_summary(spikes,windows,role)
  self.assertFalse(physiological_summary(spikes[:20],windows,'C')['pass'])
 def test_balanced_B_selection_and_seed_policy(self):
  records=[]
  for lam,bo,fc in [(.01,-.1,-2),(.1,-2,-.5),(1.,-3,-3)]:
   records.extend({'lambda':lam,'mouse_id':i,'protocol':'BO' if i<5 else 'FC','logscore':bo if i<5 else fc} for i in range(28))
  self.assertEqual(select_lambda(records),.01)
  self.assertEqual(select_lambda([{**x,'logscore':-1} for x in records]),1.)
  rs=[{'seed':s,'objective':1.,'numerical_pass':True} for s in [11,23,37]];self.assertEqual(select_seed(rs),11)
  rs[-1]['numerical_pass']=False
  with self.assertRaises(ValueError):select_seed(rs)
 def test_exact_mouse_signs_Holm5_bootstrap_and_no_pseudoreplication(self):
  x=np.ones((4,6));result=statistics(x);self.assertEqual(result['sign_patterns'],16);np.testing.assert_array_equal(result['p'],np.full(6,.125));np.testing.assert_array_equal(result['secondary_Holm5'],np.full(5,.625))
  self.assertEqual(result['CI'].shape,(2,6));np.testing.assert_array_equal(statistics(np.zeros((4,6)))['p'],np.ones(6))
  again=statistics(x);np.testing.assert_array_equal(result['CI'],again['CI'])
 def test_claim_classification_primary_gate_interval_and_fallback(self):
  r={'mean':np.full(6,.01),'CI':np.array([np.full(6,.005),np.full(6,.015)]),'p':np.full(6,.001),'secondary_Holm5':np.full(5,.005),'LOMO':np.full((12,6),.009)}
  self.assertEqual(set(classify(r,12,True,True,[True]*3,True).values()),{'HELDOUT_DESCRIPTIVE_POSITIVE'})
  self.assertEqual(set(classify(r,11,True,True,[True]*3,True).values()),{'FALLBACK_DESCRIPTIVE_COVERAGE_FAIL'})
  self.assertEqual(set(classify(r,12,False,True,[True]*3,True).values()),{'INCONCLUSIVE_REQUIRED_GATE'})
  r['CI'][0,0]=.001;self.assertEqual(set(classify(r,12,True,True,[True]*3,True).values()),{'MIXED_UNSUPPORTED'})
 def test_circular_shift_count_and_support(self):
  x=np.array([0,.02,.2,np.nextafter(.25,0)]);a=circular_shift(x,0,.25,np.random.Generator(np.random.PCG64(16053)))
  self.assertEqual(len(a),len(x));self.assertTrue(np.all((0<=a)&(a<.25)))
if __name__=='__main__':unittest.main()
