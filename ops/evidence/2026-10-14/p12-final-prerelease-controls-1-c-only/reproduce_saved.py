"""Saved C-only evidence verification. No fitter, neural-input loader or release call."""
import hashlib
import json
from pathlib import Path
import sys
import zipfile

FOLDER=Path(__file__).resolve().parent
ROOT=FOLDER.parents[3]
HERE=ROOT/'paper12_controls1'

def load(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for block in iter(lambda:f.read(1048576),b''):h.update(block)
    return h.hexdigest()

def main():
    seal=load(FOLDER/'final_manifest.json')
    for name,h in seal['sha256'].items():
        if sha(ROOT/name)!=h:raise RuntimeError('FINAL_ARTIFACT_DRIFT:'+name)
    snapshot=HERE/'implementation_snapshot_v2.json'
    if sha(snapshot)!='dc48694e8c42843bc8923660d38dc5cc816eff9b2ebefe9bd2f6b36c33ef13d7':raise RuntimeError('FROZEN_SNAPSHOT')
    for name,h in load(snapshot)['sha256'].items():
        if sha(ROOT/name)!=h:raise RuntimeError('FROZEN_SOURCE_DRIFT:'+name)
    prior=load(FOLDER/'prior_committed_evidence_preservation.json');baseline=FOLDER/'daily_at_continuation_start.bin'
    for name,h in prior['working_bytes_sha256'].items():
        if name=='ops/daily-operations.md':
            if sha(baseline)!=h or not (ROOT/name).read_bytes().endswith(baseline.read_bytes()):raise RuntimeError('DAILY_HISTORY_DRIFT')
        elif sha(ROOT/name)!=h:raise RuntimeError('PRIOR_EVIDENCE_DRIFT:'+name)
    archives=members=0
    for p in FOLDER.glob('*_archive.json'):
        manifest=load(p);archive=FOLDER/manifest['archive']
        if sha(archive)!=manifest['archive_sha256']:raise RuntimeError('ARCHIVE_DRIFT')
        with zipfile.ZipFile(archive) as z:
            if len(z.namelist())!=len(manifest['member_sha256']) or set(z.namelist())!=set(manifest['member_sha256']):raise RuntimeError('ARCHIVE_ROSTER')
            for name,h in manifest['member_sha256'].items():
                if hashlib.sha256(z.read(name)).hexdigest()!=h:raise RuntimeError('ARCHIVE_MEMBER_DRIFT')
                members+=1
        archives+=1
    handoff=load(FOLDER/'HANDOFF.json')
    if handoff['D_RELEASE_CONSUMED'] or handoff['D_EVALUATION_EXECUTED'] or handoff.get('D_AUTHORIZED',False):raise RuntimeError('FORBIDDEN_D_ACTION')
    # This closeout reproduces the saved required-gate failure. It never retries sealing.
    if handoff['COMPLETE_C_SEAL_PASS'] or handoff['REAL_C_CALIBRATION_PASS'] or handoff['ENGINEERING_CONTROL_PASS']:raise RuntimeError('FALSE_COMPLETE_CONTROL_PASS')
    failure=load(FOLDER/'required_gate_failure.json')
    if failure['error_type']!='ModuleNotFoundError' or failure['message']!="No module named 'selection'" or failure['fit_retries'] or failure['seal_retries']:raise RuntimeError('FAILURE_RECORD_DRIFT')
    print(json.dumps({'saved_C_only_reproduction':'PASS','historical_files_preserved':prior['tracked_files'],
        'source_files_verified':92,'new_numerical_fits':0,'C_D_neural_input_partitions_opened':0,
        'new_archive_files':archives,'exact_archive_members':members,'complete_private_model_seal_verified':False,'required_seal_failure_preserved':True,
        'ENGINEERING_CONTROL_PASS':handoff['ENGINEERING_CONTROL_PASS'],'REAL_C_CALIBRATION_PASS':handoff['REAL_C_CALIBRATION_PASS'],
        'D_RELEASE_CONSUMED':False,'D_EVALUATION_EXECUTED':False}))
if __name__=='__main__':main()
