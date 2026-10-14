"""Fresh native saved-evidence certification. No model/AD/fit execution."""
import csv
import hashlib
import json
from pathlib import Path
import sys

def main():
    deps,data,output,source,key,pid,sddl=sys.argv[1:];sys.path[:0]=[deps,str(Path(__file__).parent)];out=Path(output);code=Path(__file__).parent
    def load(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
    def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
    def save(n,v):
        with (out/n).open('x',encoding='utf-8') as f:json.dump(v,f,indent=2,allow_nan=False)
    from native_analysis_check import check
    proof=check(source,key,pid,sddl);save('role_proof.json',proof)
    if not proof['pass']:raise PermissionError('FRESH_NATIVE_ROLE_PROOF')
    binding=load(code/'recovery_binding.json')
    for name,digest in binding['sha256'].items():
        if sha(code/name)!=digest:raise RuntimeError('RECOVERY_PAYLOAD_CHANGED:'+name)
    gate=load(code/'primary_gate.json');reproduction=load(code/'primary_reproduction.json');decision=load(code/'primary_decision.json');tests=load(code/'primary_tests.json')
    if not reproduction['all_exact'] or not tests['passed'] or tests['count']!=13 or tests['skips'] or gate['gate']!='PASS' or gate['real_fits']!=1:raise RuntimeError('PRIMARY_NUMERICAL_PROOF_REQUIRED')
    with (code/'gradient_scan.csv').open(encoding='utf-8',newline='') as f:rows=list(csv.DictReader(f))
    expected={(stage,i,s) for stage in ('initial','intermediate','endpoint') for i in range(384) for s in (1e-2,1e-3,1e-4,1e-5,1e-6,1e-7,1e-8)}
    if {(r['stage'],int(r['coordinate']),float(r['scale'])) for r in rows}!=expected or len(rows)!=8064 or sha(code/'gradient_scan.csv')!=gate['CSV_sha256']:raise RuntimeError('EXACT_SAVED_COORDINATE_PROOF')
    from reproduce_saved import validate_row
    from audit_statistics import reconstruct
    for row in rows:validate_row(row)
    verdict=reconstruct(rows,gate['stages'],decision)
    if verdict!=gate['verdict']:raise RuntimeError('ROOT_CAUSE_CHANGED')
    manifest=load(Path(data)/'manifest.json')
    if manifest['group']!='development' or manifest['compartments']!=['A'] or sha(Path(data)/'manifest.json')!=binding['A_manifest_sha256']:raise PermissionError('SAME_A_METADATA_REQUIRED')
    save('gate_result.json',dict(gate='PASS',scope='Saved-only primary evidence certification; not a second fit or derivative experiment',verdict=verdict,coordinate_rows=len(rows),primary_binding_sha256=sha(code/'recovery_binding.json'),primary_numerical_gate_sha256=sha(code/'primary_gate.json'),new_fits=0,new_derivative_evaluations=0,original_fit_count=1,validation_access=False,final_access=False,primary_process_exit_code='NOT_PUBLISHED_DUE_TO_CONTROLLER_SERIALIZATION_ERROR',primary_cleanup_hresult='NOT_PUBLISHED',fresh_saved_certification=True))

if __name__=='__main__':main()
