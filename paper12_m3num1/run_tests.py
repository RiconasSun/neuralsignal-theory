"""Fresh regressions; capture only into this study, never invoke old result writers."""
import os
import subprocess
import sys
from datetime import datetime,timezone
import study as r


def main():
    rows=[]
    for folder,pattern in (('paper12_custody1','test_*.py'),('paper12_transport1','test_*.py'),
                           ('paper12_checkpoint1','test_*.py'),('paper12_resume1','test_*.py'),
                           ('paper12_m3num1','test_*.py')):
        env=dict(os.environ);env['PYTHONPATH']=str(r.OLD)
        command=[sys.executable,'-m','unittest','discover','-s',folder,'-p',pattern,'-v']
        run=subprocess.run(command,cwd=r.ROOT,env=env,capture_output=True,text=True)
        log=r.HERE/'results/tests'/(folder+'.log');log.parent.mkdir(parents=True,exist_ok=True)
        log.write_text(run.stdout+run.stderr,encoding='utf-8')
        rows.append(dict(folder=folder,exit_code=run.returncode,log_sha256=r.sha(log)))
        print(folder,run.returncode,flush=True)
    r.save(r.HERE/'results/tests/receipt.json',dict(utc=datetime.now(timezone.utc).isoformat(),rows=rows,
        code_sha256={p.name:r.sha(p) for p in r.HERE.glob('*.py')},
        passed=all(x['exit_code']==0 for x in rows),source_requests=0,final_access=False))
    if not all(x['exit_code']==0 for x in rows):raise SystemExit(1)


if __name__=='__main__':main()
