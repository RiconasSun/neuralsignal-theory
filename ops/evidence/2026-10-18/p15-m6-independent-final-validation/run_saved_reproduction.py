"""Native PowerShell saved-only command plus an artifact-bound typed receipt."""
import argparse
import datetime
import json
from pathlib import Path
import subprocess
from paper15_final1.source import P,E,R,read,dump,sha


def run(attempt):
    assert attempt in (1,2,3)
    log=E/f'NATIVE_SAVED_REPRODUCTION_{attempt}.log';receipt=E/f'NATIVE_SAVED_REPRODUCTION_RECEIPT_{attempt}.json'
    assert not log.exists() and not receipt.exists()
    archive=sha(P/'ARCHIVE_FREEZE.json');claim=sha(P/'D_BATCH_CLAIM.json')
    command=['powershell','-NoProfile','-ExecutionPolicy','Bypass','-File',str(P/'reproduce.ps1')]
    with log.open('wb') as handle:
        completed=subprocess.run(command,cwd=R,stdout=handle,stderr=subprocess.STDOUT)
    text=log.read_text(encoding='utf-8-sig');results=[]
    for line in text.splitlines():
        if line.startswith('{'):
            try:results.append(json.loads(line))
            except ValueError:pass
    ok=completed.returncode==0 and len(results)==1
    result=results[0] if len(results)==1 else None
    if ok:
        ok=(result['saved_only'] is True and result['saved_statistics_exact'] is True and result['tests']==68
            and result['main_attempts']==72 and result['sensitivity_attempts']==320
            and result['passing_endpoint_certificates']==392 and result['source_arrays_loaded']==0
            and result['new_real_fits']==0 and result['D_reassessment'] is False)
    assert sha(P/'ARCHIVE_FREEZE.json')==archive and sha(P/'D_BATCH_CLAIM.json')==claim
    dump(receipt,dict(status='PASS_NATIVE_POWERSHELL_SAVED_ONLY' if ok else 'FAILED_SAVED_REPRODUCTION',
        time=datetime.datetime.now(datetime.timezone.utc).isoformat(),archive_sha256=archive,D_claim_sha256=claim,
        command=command,exit_code=completed.returncode,log_path=log.relative_to(R).as_posix(),log_sha256=sha(log),result=result))
    assert ok,'Saved reproduction failed; original log and receipt preserved'
    print('Actual native PowerShell saved-only PASS; receipt',receipt.name)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--attempt',type=int,required=True);run(p.parse_args().attempt)
