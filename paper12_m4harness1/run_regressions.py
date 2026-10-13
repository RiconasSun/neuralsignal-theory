"""Synthetic/local regressions only; record into this mission, never old outputs."""
import os
import subprocess
import sys
import re
import study as r

FOLDERS=('paper12_custody1','paper12_transport1','paper12_checkpoint1','paper12_resume1','paper12_m3num1','paper12_m4harness1')


def run(output):
    output.mkdir(parents=True,exist_ok=True);rows=[]
    for folder in FOLDERS:
        env=dict(os.environ);env['PYTHONPATH']=str(r.OLD)
        command=[sys.executable,'-m','unittest','discover','-s',folder,'-p','test_*.py','-v']
        result=subprocess.run(command,cwd=r.ROOT,env=env,capture_output=True,text=True)
        text=result.stdout+result.stderr;log=output/(folder+'.log');log.write_text(text,encoding='utf-8')
        match=re.search(r'^Ran (\d+) tests? in ',text,re.M)
        rows.append(dict(folder=folder,exit_code=result.returncode,test_count=int(match[1]) if match else 0,log_sha256=r.sha(log)))
        print(folder,result.returncode,flush=True)
    return rows


def main():
    rows=run(r.HERE/'results/regressions')
    passed=all(x['exit_code']==0 for x in rows) and sum(x['test_count'] for x in rows)==193
    r.save(r.HERE/'results/regressions/receipt.json',dict(passed=passed,checks=rows,total_tests=sum(x['test_count'] for x in rows),
        source_requests=0,final_access=False,neural_fits=False))
    if not passed:raise SystemExit(1)


if __name__=='__main__':main()
