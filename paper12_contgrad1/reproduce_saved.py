"""Synthetic oracle tests plus public saved numerical evidence replay.

No neural input or protected vectors read; never launches another fit.
"""
import csv
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import study as r

def error(a,b):return abs(a-b)/max(1.,abs(a),abs(b))
def close(a,b):return math.isclose(a,b,rel_tol=1e-12,abs_tol=1e-12)

def validate_row(row):
    h=float(row['h']);a=float(row['analytical']);ad=float(row['AD'])
    fm2,fm,fmh,fph,fp,fp2=[float(row[k]) for k in ('f_minus2','f_minus1','f_minus_half','f_plus_half','f_plus1','f_plus2')]
    central=(fp-fm)/(2*h);fourth=(fm2-8*fm+8*fp-fp2)/(12*h);rich=(4*(fph-fmh)/h-central)/3
    for name,value in (('central',central),('fourth_order',fourth),('richardson',rich),('AD_abs_error',abs(a-ad)),('AD_scaled_error',error(a,ad)),('central_abs_error',abs(central-ad)),('central_scaled_error',error(central,ad)),('fourth_abs_error',abs(fourth-ad)),('fourth_scaled_error',error(fourth,ad)),('richardson_abs_error',abs(rich-ad)),('richardson_scaled_error',error(rich,ad))):
        if not close(float(row[name]),value):raise RuntimeError('SAVED_DERIVATIVE_ARITHMETIC:'+name)
    if not close(float(row['ridge_AD']),.001*float(row['theta'])) or not close(ad,float(row['likelihood_AD'])+float(row['ridge_AD'])):raise RuntimeError('RIDGE_DECOMPOSITION')
    if not close(h,float(row['scale'])*max(1.,abs(float(row['theta'])))):raise RuntimeError('REGISTERED_STEP')

def main():
    before=r.sha(r.HERE/'final_manifest.json')
    for name,digest in r.load(r.HERE/'final_manifest.json')['sha256'].items():
        if r.sha(r.ROOT/name)!=digest:raise RuntimeError('FINAL_CANDIDATE_CHANGED:'+name)
    public=r.HERE/'results/diagnostic/native';gate=r.load(public/'gate_result.json');proof=r.load(public/'role_proof.json');reproduction=r.load(public/'reproduction.json')
    certificate=r.HERE/'results/receipt_recovery/native';receipt=r.load(r.HERE/'results/receipt_recovery_launch_receipt.json');cert_gate=r.load(certificate/'gate_result.json');cert_proof=r.load(certificate/'role_proof.json')
    if gate['gate']!='PASS' or receipt['exit_code']!=0 or receipt['timed_out'] or receipt['profile_cleanup_hresult']!='0x00000000' or not receipt['role_proof_pass'] or not proof['pass'] or proof['capability_count']!=0 or not cert_proof['pass'] or cert_proof['capability_count']!=0 or not reproduction['all_exact']:raise RuntimeError('COMPLETE_NATIVE_DIAGNOSIS_AND_SAVED_CERTIFICATE_REQUIRED')
    if cert_gate['gate']!='PASS' or cert_gate['primary_numerical_gate_sha256']!=r.sha(public/'gate_result.json') or cert_gate['new_fits'] or cert_gate['new_derivative_evaluations']:raise RuntimeError('FRESH_SAVED_CERTIFICATE_BINDING')
    if gate['validation_access'] or gate['final_access'] or reproduction['real_fits']!=1 or reproduction['M3_refits'] or reproduction['offset_refits']:raise RuntimeError('SCOPE_VIOLATION')
    if gate['CSV_sha256']!=r.sha(public/'gradient_scan.csv'):raise RuntimeError('GRADIENT_CSV_CHANGED')
    with (public/'gradient_scan.csv').open(encoding='utf-8',newline='') as f:rows=list(csv.DictReader(f))
    scales=r.load(r.HERE/'protocol.json')['scales'];expected={(stage,i,scale) for stage in ('initial','intermediate','endpoint') for i in range(384) for scale in scales}
    keys={(row['stage'],int(row['coordinate']),float(row['scale'])) for row in rows}
    if keys!=expected or len(rows)!=len(expected) or len(rows)!=gate['coordinate_rows']:raise RuntimeError('EXACT_COORDINATE_COVERAGE')
    for row in rows:validate_row(row)
    from audit_statistics import reconstruct
    reconstructed=reconstruct(rows,gate['stages'],r.load(public/'decision.json'))
    if reconstructed!=gate['verdict']:raise RuntimeError('ROOT_CAUSE_RECONSTRUCTION')
    frozen=r.load(r.HERE/'frozen_sources/manifest.json')
    for name,digest in frozen['sha256'].items():
        if r.sha(r.HERE/'frozen_sources'/name)!=digest:raise RuntimeError('FROZEN_REPRODUCTION_SOURCE_CHANGED')
    env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',PYTHONPATH=str(r.HERE/'frozen_sources'))
    synthetic=subprocess.run([sys.executable,'-m','unittest','discover','-s',str(r.HERE),'-p','test_diagnostics.py','-v'],env=env,capture_output=True,text=True)
    saved=subprocess.run([sys.executable,'-m','unittest','discover','-s',str(r.HERE),'-p','test_saved_audit.py','-v'],env=env,capture_output=True,text=True)
    out=r.HERE/'replay'/r.datetime.now(r.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ');out.mkdir(parents=True,exist_ok=False)
    (out/'synthetic.log').write_text(synthetic.stdout+synthetic.stderr,encoding='utf-8');(out/'saved.log').write_text(saved.stdout+saved.stderr,encoding='utf-8')
    if synthetic.returncode or saved.returncode or r.sha(r.HERE/'final_manifest.json')!=before:raise RuntimeError('REPLAY_REGRESSION_OR_MANIFEST_FAILURE')
    import re
    counts=[int(re.search(r'Ran (\d+) tests?',x.stdout+x.stderr)[1]) for x in (synthetic,saved)]
    if any('skipped=' in x.stdout+x.stderr for x in (synthetic,saved)):raise RuntimeError('NO_SKIPPED_REQUIRED_TESTS')
    r.save(out/'receipt.json',dict(passed=True,utc=r.datetime.now(r.timezone.utc).isoformat(),manifest_sha256=before,coordinate_rows=len(rows),synthetic_tests=counts[0],saved_audit_tests=counts[1],new_real_fits=0,neural_access=False,protected_states_accessed=False,live_isolation_repeated=False,original_controller_exit=1,original_native_exit='UNPUBLISHED',original_cleanup_hresult='UNPUBLISHED',fresh_saved_certificate_exit=receipt['exit_code'],fresh_saved_certificate_cleanup=receipt['profile_cleanup_hresult'],original_scientific_failure_unchanged=True,verdict=gate['verdict']))
    print('REPRODUCTION_PASS',gate['verdict'],'coordinate_rows',len(rows),'synthetic_tests',counts[0],'saved_audit_tests',counts[1],'receipt',out/'receipt.json')

if __name__=='__main__':main()
