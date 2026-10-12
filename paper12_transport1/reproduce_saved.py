"""Public saved evidence only; cannot retrieve/decrypt data or run models."""
import subprocess
import sys
from datetime import datetime,timezone
import common as r


def verify_manifest(expected=None):
    path=r.HERE/'final_manifest.json';digest=r.sha(path)
    if expected is not None and digest!=expected:raise RuntimeError('REPLAY_MANIFEST_CHANGED')
    for name,value in r.load(path)['sha256'].items():
        if r.sha(r.HERE/name)!=value:raise RuntimeError('REPLAY_INPUT_CHANGED:'+name)
    if r.sha(path)!=digest:raise RuntimeError('REPLAY_MANIFEST_CHANGED')
    return digest


def main():
    before=verify_manifest();r.verify()
    out=r.HERE/'replay/saved';out.mkdir(parents=True,exist_ok=True)
    commands=[['powershell','-NoProfile','-ExecutionPolicy','Bypass','-File',str(r.OLD/'reproduce2.ps1'),'-Python',sys.executable],
        [sys.executable,'-m','unittest','discover','-s',str(r.HERE),'-p','test_*.py','-v'],
        [sys.executable,str(r.HERE/'summarize.py')]]
    checks=[]
    for number,command in enumerate(commands):
        result=subprocess.run(command,cwd=r.ROOT,capture_output=True,text=True)
        log=out/('check_%02d.log'%number);log.write_text(result.stdout+result.stderr,encoding='utf-8')
        checks.append(dict(command=command,exit_code=result.returncode,log=log.name,sha256=r.sha(log)))
        if result.returncode:break
    after=verify_manifest(before)
    receipt=dict(utc=datetime.now(timezone.utc).isoformat(),checks=checks,start_manifest_sha256=before,end_manifest_sha256=after,
        saved_checks_pass=len(checks)==3 and all(x['exit_code']==0 for x in checks),
        saved_M2_gate=r.load(r.HERE/'results/M2/gate_result.json')['gate'],
        scope='Saved public evidence/tests; no extraction,live isolation,private QC,models or final evaluation rerun',
        source_requests_executed=0,experiments_reproduced=False,final_holdout_accessed=False)
    r.save(out/'receipt.json',receipt);print(receipt)
    if not receipt['saved_checks_pass']:raise SystemExit(1)


if __name__=='__main__':main()
