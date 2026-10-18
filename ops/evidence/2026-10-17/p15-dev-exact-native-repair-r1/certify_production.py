"""Synthetic certification and preparation source-continuity receipt; no real fits."""
import ast,hashlib,datetime,unittest,shutil
from paper15_r1.source import P,R,dump,load_json
from paper15_r1.training import sha

E=R/'ops/evidence/2026-10-17/p15-dev-exact-native-repair-r1'
snapshot=(R/'paper15_dev/training.py').read_text().replace('paper15_dev','paper15_r1').replace('json.loads(','load_json(')
lines=snapshot.splitlines();lines.insert(1,'from .source import load_json');snapshot='\n'.join(lines)+'\n'
states=[load_json(p.read_text()) for p in (P/'states').glob('*_A_PREPROCESSING.json')]
assert len(states)==10
snapshot_bytes=snapshot.replace('\n','\r\n').encode()  # Original Windows Path.write_text bytes.
h=hashlib.sha256(snapshot_bytes).hexdigest();assert all(s['preparation_implementation_sha256']==h for s in states)
dst=P/'source_snapshots/training_A_preparation.py';dst.parent.mkdir(parents=True,exist_ok=True)
if dst.exists():assert dst.read_bytes()==snapshot_bytes
else:dst.write_bytes(snapshot_bytes)
def prepare_ast(text):return ast.dump(next(x for x in ast.parse(text).body if isinstance(x,ast.FunctionDef) and x.name=='prepare'),include_attributes=False)
assert prepare_ast(snapshot)==prepare_ast((P/'training.py').read_text())
continuity=dict(preparation_source_snapshot_sha256=h,
    current_training_sha256=sha(P/'training.py'),prepare_AST_sha256=hashlib.sha256(prepare_ast(snapshot).encode()).hexdigest(),
    prepare_function_unchanged=True,states=10,reason='Subsequent edits only register corrective budget metadata and enforce production admission; no preparation equation or output changed')
if (P/'results/A_PREPARATION_SOURCE_CONTINUITY.json').exists():assert load_json((P/'results/A_PREPARATION_SOURCE_CONTINUITY.json').read_text())==continuity
else:dump(P/'results/A_PREPARATION_SOURCE_CONTINUITY.json',continuity)
names=['source','reader','integrity','models','features','worker','selection','controls','sensitivities','statistics','evaluation','saved_audit','anatomy','native_table','production_admission']
suite=unittest.TestSuite(unittest.defaultTestLoader.loadTestsFromName('paper15_r1.test_'+n) for n in names)
result=unittest.TextTestRunner(verbosity=1).run(suite);assert result.wasSuccessful()
grad=load_json((P/'work/PRODUCTION_GRADIENT_SYNTHETIC.json').read_text());assert len(grad)==24
target=P/'results/PRODUCTION_GRADIENT_SYNTHETIC.json'
if target.exists():assert sha(target)==sha(P/'work/PRODUCTION_GRADIENT_SYNTHETIC.json')
else:shutil.copyfile(P/'work/PRODUCTION_GRADIENT_SYNTHETIC.json',target)
dump(P/'results/PRODUCTION_SYNTHETIC_CERTIFICATE.json',dict(time=datetime.datetime.now(datetime.timezone.utc).isoformat(),
    tests=result.testsRun,failures=0,errors=0,gradient_points=24,analytic_AD_max=max(x['check']['AD_max_scaled'] for x in grad),
    all_fixed_FD_max=max(f['max_scaled'] for x in grad for f in x['check']['FD']),
    original_math_byte_hashes={name:sha(P/name) for name in ['models.py','features.py','independent_ad.py','physiology.py']},
    mathematical_sources_equal_original=all(sha(P/name)==sha(R/'paper15_dev'/name) for name in ['models.py','features.py','independent_ad.py','physiology.py']),
    current_sources={path.name:sha(path) for path in P.glob('*.py')},real_fits=0,Final_access=False))
print('Synthetic production certificate',result.testsRun,'tests/24points; preparation AST unchanged')
