"""Additional synthetic, metadata-only guards. Never opens a neural container."""
import ast,unittest
from pathlib import Path
import numpy as np
from .spec import *

def supported(a,b,valid,invalid):
 return any(l<=a and b<=r for l,r in valid) and not any(l<b and a<r for l,r in invalid)

class AdditionalTests(unittest.TestCase):
 def test_normative_bounds_and_initializer_match(self):
  import json
  root=Path(__file__).resolve().parents[1];num=json.loads((root/'NUMERICAL_POLICY.json').read_text(encoding='utf8'));cfg=json.loads((root/'protocol.json').read_text(encoding='utf8'))
  self.assertEqual(num['bounds']['PSTH_and_B0'],[-10,10])
  for text in [num['initialization'],num['B0_rate_domain'],cfg['features']['B0_and_initialization_rate_domain']]:
   self.assertIn('clip(log R_u,-10,10)',text)
  from .dynamics import constraints
  lo,hi=constraints(8,30);self.assertEqual(lo[0],-10);self.assertEqual(hi[0],10)
 def test_current_documents_UTF8_not_double_encoded(self):
  root=Path(__file__).resolve().parents[1]
  for p in root.glob('*.md'):
   s=p.read_text(encoding='utf8')
   for broken in ['âˆ','â‰','â€“','Ã—']:
    self.assertNotIn(broken,s,str(p))
 def test_complete_presentation_late_invalid_does_not_count(self):
  source=[[(0.,.25)],[(0.,.25)]]
  self.assertTrue(complete_presentation(0,.25,source))
  self.assertFalse(complete_presentation(0,.25,source,[(.215,.22)]))
  self.assertFalse(complete_presentation(0,.25,[[(0,.15)],[(0,.25)]]))
  self.assertFalse(complete_presentation(0,.25,[[(0,.1),(.11,.25)]]))
  self.assertFalse(complete_presentation(0,.21,source))
  self.assertTrue(complete_presentation(0,.25,[[(0,.1),(.1,.25)]]))
  self.assertEqual(sum(complete_presentation(0,.25,source,[(.215,.22)]) for _ in range(30)),0)
 def test_B0_init_scored_rows_not_early_QC(self):
  late_counts=np.array([10.]+[0.]*59);exposure=np.full(60,.02)
  value=scored_log_rate(late_counts,exposure)
  self.assertAlmostEqual(math.exp(value),10/1.2)
  self.assertNotAlmostEqual(math.exp(value),100/2.2)
  self.assertEqual(scored_log_rate(np.zeros(60),exposure),-10.)
  self.assertEqual(scored_log_rate(np.full(60,10000),exposure),10.)
  _,g=glm([value],np.ones((60,1)),late_counts,exposure,0,1);self.assertLess(abs(g[0]),1e-14)
 def test_secondary_classification_frozen_per_contrast(self):
  import json
  cfg=json.loads((Path(__file__).resolve().parents[1]/'protocol.json').read_text(encoding='utf8'))['statistics']
  for row in cfg['contrast_rules']:
   target=.002 if row['contrast']=='B4-B1' else .001
   self.assertEqual(row['own_mean_min'],target);self.assertEqual(row['own_CI_lower_exclusive_min'],target)
   self.assertEqual(row['own_p_max'],.05);self.assertEqual(row['n_Final_min'],12)
   self.assertIn('N1>=12',row['joint_prerequisites'])
  self.assertEqual([x['contrast'] for x in cfg['contrast_rules']],['B4-B1','B4-B2','B4-B3','D-B4','C-B4','D-S'])
 def test_documented_PowerShell_literal(self):
  raw=(Path(__file__).resolve().parents[1]/'README.md').read_bytes()
  self.assertIn(b'& .\\paper16_m1\\reproduce.ps1\n',raw)
  self.assertNotIn(b'paper16_m1\reproduce',raw)
 def test_hypothetical_power_integral(self):
  from .planning import hypothetical_power,hypothetical_interval_resolution
  from scipy.stats import nct,t
  for n,sd,d in [(6,.002,.01),(27,.005,.002),(27,.002,.01)]:
   p=hypothetical_power(n,sd,d,.05);self.assertTrue(0<=p<=1+1e-12)
  self.assertAlmostEqual(hypothetical_power(12,.005,0,.05),.05,places=10)
  self.assertAlmostEqual(hypothetical_interval_resolution(12,.005,.002,.002),.025,places=10)
  c=t.ppf(.975,26);nc=.002*27**.5/.005
  self.assertAlmostEqual(hypothetical_power(27,.005,.002,.05),1-nct.cdf(c,26,nc)+nct.cdf(-c,26,nc),places=10)
 def test_saved_manifest_tamper_missing_denied(self):
  import tempfile,hashlib
  from .verify import validate_manifest
  work=Path(__file__).resolve().parents[1]/'work';work.mkdir(exist_ok=True)
  with tempfile.TemporaryDirectory(dir=work) as d:
   root=Path(d);p=root/'fixture';p.write_bytes(b'original')
   rows=[{'path':'fixture','sha256':hashlib.sha256(b'original').hexdigest(),'bytes':8}]
   validate_manifest(root,rows,{'fixture'});p.write_bytes(b'changed')
   with self.assertRaises(AssertionError):validate_manifest(root,rows,{'fixture'})
   p.unlink()
   with self.assertRaises(AssertionError):validate_manifest(root,rows,{'fixture'})
 def test_manifest_expected_set_cannot_be_redefined(self):
  import tempfile,hashlib
  from .verify import validate_manifest
  work=Path(__file__).resolve().parents[1]/'work';work.mkdir(exist_ok=True)
  with tempfile.TemporaryDirectory(dir=work) as d:
   root=Path(d);(root/'fixture').write_bytes(b'x')
   row={'path':'fixture','sha256':hashlib.sha256(b'x').hexdigest(),'bytes':1}
   bad=[[],[row,row],[{**row,'path':'../fixture'}],[{**row,'path':'C:/fixture'}],[{**row,'path':'other'}],[{**row,'bytes':0}],[{**row,'sha256':'z'*64}]]
   for rows in bad:
    with self.subTest(rows=rows),self.assertRaises(AssertionError):validate_manifest(root,rows,{'fixture'})
   with self.assertRaises(AssertionError):validate_manifest(root,[row],{'fixture','missing'})
   with self.assertRaises(AssertionError):validate_manifest(root,[row])
 def test_observation_invalid_gaps_zero_offset(self):
  self.assertTrue(supported(0,.22,[(0,.25)],[]))
  self.assertFalse(supported(0,.22,[(0,.1),(.12,.25)],[]))
  self.assertFalse(supported(0,.22,[(0,.25)],[(.05,.06)]))
  self.assertTrue(supported(0,.22,[(0,.25)],[(.22,.25)]))
  self.assertFalse(event_available(.25,.22));self.assertFalse(event_available(.25,.25));self.assertTrue(event_available(.25,np.nextafter(.25,1)))
  self.assertEqual(count_bins([],np.array([0,.02,.04]),[True,False]),[0,None])
 def test_scalar_metadata_decoder_regression_and_allowlist(self):
  tree=ast.parse((Path(__file__).with_name('stimulus_metadata.py')).read_text())
  fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='decoded')
  ns={'np':np};exec(compile(ast.Module(body=[fn],type_ignores=[]),'<isolated metadata decoder>','exec'),ns)
  self.assertEqual(ns['decoded'](np.array(b'760345702')),'760345702')
  self.assertEqual(ns['decoded'](np.array([b'a',b'b'])),['a','b'])
  source=ast.unparse(tree)
  self.assertIn('if name not in ALLOWED:',source)
  fields=next(n.value for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(x,ast.Name) and x.id=='FIELDS' for x in n.targets))
  self.assertEqual(set(ast.literal_eval(fields)),{'id','start_time','stop_time','color','contrast','phase','spatial_frequency','size','opacity','mask'})
  self.assertNotIn('spike_times',source)
 def test_no_future_scaler_refit_or_neural_count_use(self):
  A=np.arange(48,dtype=float).reshape(2,24)/100;mu,sd,active=scaler(A)
  frozen=[v.copy() for v in (mu,sd,active)]
  E=np.full((3,24),999.);_=((E-mu)/sd)[:,active]
  for a,b in zip(frozen,(mu,sd,active)):np.testing.assert_array_equal(a,b)
 def test_eta_finiteness_and_bounded_feature_domain(self):
  self.assertLess(218,np.log(np.finfo(float).max));self.assertTrue(np.isfinite(np.exp(218)))
  with self.assertRaises(ValueError):nuisance(1,5,None,0,0,999,1.,1.,0,1)
 def test_bounds_gradient_never_blanket_zero(self):
  np.testing.assert_array_equal(projected_gradient(np.array([-1.,1.]),np.array([-2.,3.]),-1,1),[-2,3])
 def test_source_nonfinite_denied(self):
  with self.assertRaises(ValueError):histories([[float('nan')],[]],0,5)
  with self.assertRaises(ValueError):gain(np.array([float('inf')]),np.array([0.]),np.array([True]))

if __name__=='__main__':unittest.main()
