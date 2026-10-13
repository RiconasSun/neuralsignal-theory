import subprocess
import sys
from datetime import datetime,timezone
import study as r


def main():
    rows=[]
    for folder in ('paper12_custody1','paper12_transport1','paper12_checkpoint1','paper12_resume1'):
        command=[sys.executable,'-m','unittest','discover','-s',folder,'-p','test_*.py','-v']
        run=subprocess.run(command,cwd=r.ROOT,capture_output=True,text=True)
        text=run.stdout+run.stderr
        path=r.HERE/'results/tests'/(folder+'.log');path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(text,encoding='utf-8')
        rows.append(dict(folder=folder,command=command,exit_code=run.returncode,log_sha256=r.sha(path)))
        print(text)
        if run.returncode:break
    r.save(r.HERE/'results/tests/receipt.json',dict(utc=datetime.now(timezone.utc).isoformat(),
        rows=rows,passed=len(rows)==4 and all(x['exit_code']==0 for x in rows),
        source_requests=0,code_sha256={p.name:r.sha(p) for p in r.HERE.glob('*.py')}))
    if len(rows)!=4 or any(x['exit_code'] for x in rows):raise SystemExit(1)


if __name__=='__main__':main()
