"""Offline saved-metadata reproduction; never re-download or fit models."""
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from audit import HERE
from register import verify, sha
from summarize import summarize
from ibl_replay import main as replay_ibl

def reproduce():
    prior = verify()
    manifest = json.loads((HERE/'manifest.json').read_text())
    for key in ('metadata_sha256','source_sha256','result_sha256'):
        for name,digest in manifest[key].items():
            if sha(HERE/name) != digest: raise RuntimeError('Candidate input changed: '+name)
    output = HERE/'replay'
    output.mkdir(exist_ok=True)
    summarize(output)
    replay_ibl(output)
    comparisons = {}
    names = ['allen_sessions.csv','allen_mice.csv','allen_probes.csv','allen_coverage.json',
             'allen_stimulus_intervals.csv','allen_support_qc.json','allen_gate_result.json',
             'ibl_sessions_code1.csv','ibl_coverage_code1.json']
    for name in names:
        comparisons[name] = sha(output/name) == sha(HERE/'results'/name)
    if not all(comparisons.values()): raise RuntimeError('Saved-metadata result parity failed')
    test = subprocess.run([sys.executable,'-m','unittest','discover','-s',str(HERE),'-p','test_m0.py','-v'],
                          capture_output=True,text=True)
    (output/'tests.log').write_text(test.stdout+test.stderr)
    if test.returncode: raise RuntimeError('Automated tests failed: see replay/tests.log')
    receipt = {'utc':datetime.now(timezone.utc).isoformat(), 'mode':'OFFLINE_SAVED_METADATA_ONLY',
               'exit_code':test.returncode, 'comparisons':comparisons,
               'prior_files_unchanged':len(prior['prior_hashes']),
               'network_requests':0, 'new_scientific_experiments':0,
               'scientific_validation_pass':False, 'python':sys.version}
    (output/'reproduction_result.json').write_text(json.dumps(receipt,indent=2,sort_keys=True))
    print(json.dumps(receipt,indent=2))

if __name__=='__main__': reproduce()
