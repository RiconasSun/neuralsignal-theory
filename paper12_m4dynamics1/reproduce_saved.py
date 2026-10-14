"""Saved public evidence and synthetic/regression tests only; no neural access."""
import importlib.util
import os
import re
import subprocess
import sys
import study as r
from table import render
from controls import completed

def manifest():
    path=r.HERE/'final_manifest.json'
    for name,digest in r.load(path)['sha256'].items():
        if r.sha(r.HERE/name)!=digest:raise RuntimeError('PUBLIC_ARCHIVE_CHANGED:'+name)
    return r.sha(path)

def main():
    before=manifest();out=r.HERE/'replay';out.mkdir(exist_ok=True)
    gate=r.load(r.HERE/'gate_result.json')
    for phase,bindings in gate['native_bindings'].items():
        if completed(phase,False)!=bindings:raise RuntimeError('NATIVE_COMPLETION_BINDINGS_CHANGED')
        rows=r.load(r.HERE/f'results/{phase}/native/summary.json')['rows'];data=render(rows)
        target=r.HERE/f'{phase}_216_fit_table.csv'
        if data!=target.read_bytes():raise RuntimeError('TABLE_REPLAY_MISMATCH')
        (out/target.name).write_bytes(data)
    env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
    checks=[]
    folders=('paper12_custody1','paper12_transport1','paper12_checkpoint1','paper12_resume1','paper12_m3num1','paper12_m4harness1','paper12_m4offset1')
    for folder in folders:
        e=dict(env,PYTHONPATH=str(r.OLD)+os.pathsep+str(r.ROOT/'paper12_m3num1'))
        result=subprocess.run([sys.executable,'-m','unittest','discover','-s',folder,'-p','test_*.py','-v'],cwd=r.ROOT,env=e,capture_output=True,text=True)
        text=result.stdout+result.stderr;log=out/(folder+'.log');log.write_text(text,encoding='utf-8');match=re.search(r'^Ran (\d+) tests? in ',text,re.M)
        checks.append(dict(folder=folder,exit_code=result.returncode,count=int(match[1]) if match else 0,log_sha256=r.sha(log)))
    runner="import sys,unittest,importlib.util,pathlib;sys.path[:0]=sys.argv[1:4];a=unittest.TestLoader().discover(sys.argv[1],pattern='test_*.py');b=unittest.TestLoader().discover(sys.argv[1],pattern='guard_tests.py');s=importlib.util.spec_from_file_location('frozen_m4_checks',pathlib.Path(sys.argv[4])/'m4_numerical_tests.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);c=unittest.TestLoader().loadTestsFromModule(m);d=unittest.TestLoader().discover(sys.argv[3],pattern='m4_control_tests.py');e=unittest.TestLoader().discover(sys.argv[1],pattern='cache_tests.py');r=unittest.TextTestRunner(verbosity=2).run(unittest.TestSuite([a,b,c,d,e]));print('COUNT',r.testsRun);sys.exit(not(r.wasSuccessful() and r.testsRun==22 and not r.skipped))"
    e=dict(env,PYTHONPATH=str(r.OLD))
    result=subprocess.run([sys.executable,'-c',runner,str(r.HERE),str(r.PREVIOUS),str(r.OFFSET),str(r.ROOT/'paper12_m4harness1/patched')],cwd=r.ROOT,env=e,capture_output=True,text=True)
    log=out/'numerical_and_guards.log';log.write_text(result.stdout+result.stderr,encoding='utf-8')
    after=manifest();passed=before==after and result.returncode==0 and all(z['exit_code']==0 for z in checks) and sum(z['count'] for z in checks)==204
    r.save(out/'receipt.json',dict(utc=r.datetime.now(r.timezone.utc).isoformat(),passed=passed,regression_checks=checks,regression_count=sum(z['count'] for z in checks),
        numerical_and_guard_tests=22 if result.returncode==0 else None,numerical_log_sha256=r.sha(log),manifest_before=before,manifest_after=after,
        tables_reproduced=True,source_requests=0,neural_access=False,real_fits_repeated=False,live_isolation_repeated=False,unexecuted_science_reproduced=False,final_access=False),False)
    print('SAVED_ONLY_REPRODUCTION',passed,'REGRESSIONS',sum(z['count'] for z in checks),'NEW_NUMERICAL_GUARDS',22 if result.returncode==0 else 'FAILED')
    if not passed:raise SystemExit(1)

if __name__=='__main__':main()
