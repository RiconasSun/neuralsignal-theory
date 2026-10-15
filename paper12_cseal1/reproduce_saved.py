"""Verify archived public evidence and, by default, the existing protected seal."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
E = ROOT/'ops/evidence/2026-10-14/p12-c-seal-host-import-repair-1'

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--public-only',action='store_true');args=parser.parse_args()
    report=json.loads((E/'final_manifest.json').read_text(encoding='utf-8'))
    for name, expected in report['sha256'].items():
        if hashlib.sha256((ROOT/name).read_bytes()).hexdigest()!=expected:raise RuntimeError('SAVED_EVIDENCE_DRIFT:'+name)
    final=json.loads((E/'HANDOFF.json').read_text(encoding='utf-8'))
    assert final['ENGINEERING_CONTROL_PASS'] and final['REAL_C_NUMERICAL_FITS_PASS'] and final['COMPLETE_C_SEAL_PASS'] and final['REAL_C_CALIBRATION_PASS']
    assert final['D_RELEASE_CONSUMED'] is False and final['D_EVALUATION_EXECUTED'] is False and final['new_real_C_fits']==0
    if not args.public_only:
        checks=E/'reproduction_checks';checks.mkdir(exist_ok=True)
        receipt=checks/(str(time.time_ns())+'.json')
        subprocess.run([sys.executable,'-B','-m','paper12_cseal1.host','--check','--receipt',str(receipt)],cwd=ROOT,check=True)
        result=json.loads(receipt.read_text(encoding='utf-8'))
        assert result['COMPLETE_C_SEAL_PASS'] and result['verified_counts']==final['verified_counts']
    print(json.dumps({'saved_public_integrity':'PASS','protected_saved_state':'NOT_RUN_PUBLIC_ONLY' if args.public_only else 'PASS','new_fits':0,'raw_C_D_reads':0,'D_RELEASE_CONSUMED':False,'D_EVALUATION_EXECUTED':False}))

if __name__=='__main__':main()
