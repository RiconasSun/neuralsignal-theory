"""Path metadata classification only; no neural/state-value decoding or hashing."""
import collections,json
from pathlib import Path
R=Path(__file__).resolve().parents[4];E=Path(__file__).resolve().parent;old=R/'paper16_development_r3'
rows=json.loads((R/'paper16_development_r5/INDEPENDENT_R5_PROTECTED_HASH_READBACK.json').read_bytes())['files']
expected={row['path'] for row in rows if row['path'].startswith('paper16_development_r3/')}
actual={p.relative_to(R).as_posix() for d in [old/'work',old/'results'] for p in d.rglob('*') if p.is_file()}
pins=json.loads((R/'paper16_development_r4/SOURCE_PINS.json').read_bytes())['files']
out=[]
for name in sorted(actual-expected):
    category='historical_public_results' if name.startswith('paper16_development_r3/results/') else 'historical_synthetic_fixture' if '/work/synthetic/' in name or '/work/test_metadata_' in name else 'historical_tools_preflight_and_closeout'
    out.append({'path':name,'path_category':category,'frozen_public_source_pin_present':name in pins,'admitted_as_scientific_state':False})
value={'protected_scientific_inventory_count':len(expected),'whole_work_results_path_count':len(actual),'outside_protected_scientific_scope':len(out),'missing_registered_paths':sorted(expected-actual),'classification':'Path names/context only, not a new scientific identity or numerical audit','new_numerical_evaluations':0,'buckets':dict(collections.Counter(x['path_category'] for x in out)),'paths':out,'enforcement':'Canonical admitted R3 fits/B0 have exact registered folder members; only registered paths may enter the M4 seal; known old tools/fixtures are preserved without scientific admission.'}
with (E/'R3_INVENTORY_SCOPE_CLASSIFICATION.json').open('x',encoding='utf8') as f:json.dump(value,f,indent=2)
print(json.dumps({k:v for k,v in value.items() if k!='paths'},indent=2))
