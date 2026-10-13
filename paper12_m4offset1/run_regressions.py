import os
import re
import subprocess
import sys
import study as r

FOLDERS=('paper12_custody1','paper12_transport1','paper12_checkpoint1','paper12_resume1','paper12_m3num1','paper12_m4harness1','paper12_m4offset1')


def run(output):
    output.mkdir(parents=True,exist_ok=True);checks=[]
    for folder in FOLDERS:
        env=dict(os.environ);env['PYTHONPATH']=str(r.OLD)+os.pathsep+str(r.M3)
        result=subprocess.run([sys.executable,'-m','unittest','discover','-s',folder,'-p','test_*.py','-v'],cwd=r.ROOT,env=env,capture_output=True,text=True)
        text=result.stdout+result.stderr;log=output/(folder+'.log');log.write_text(text,encoding='utf-8');match=re.search(r'^Ran (\d+) tests? in ',text,re.M)
        checks.append(dict(folder=folder,exit_code=result.returncode,count=int(match[1]) if match else 0,log_sha256=r.sha(log)));print(folder,result.returncode,flush=True)
    return checks


def main():
    checks=run(r.HERE/'results/regressions');passed=all(x['exit_code']==0 for x in checks) and sum(x['count'] for x in checks)==204
    r.save(r.HERE/'results/regressions/receipt.json',dict(passed=passed,checks=checks,total_tests=sum(x['count'] for x in checks),source_requests=0,neural_fits=False,final_access=False))
    if not passed:raise SystemExit(1)


if __name__=='__main__':main()
