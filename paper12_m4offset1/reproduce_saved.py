import os
import subprocess
import sys
import re
import study as r
from closure_verify import verify
from run_regressions import run
from summarize import offsets,models


def manifest():
    for name,digest in r.load(r.HERE/'final_manifest.json')['sha256'].items():
        if r.sha(r.HERE/name)!=digest:raise RuntimeError('SAVED_PUBLIC_FILE_CHANGED:'+name)
    return r.sha(r.HERE/'final_manifest.json')


def main():
    verify();before=manifest();output=r.HERE/'replay';output.mkdir(exist_ok=True);checks=run(output)
    for name,render in (('offset_diagnostics.csv',offsets),('model_comparison.csv',models)):
        text=render();(output/name).write_text(text,encoding='utf-8',newline='')
        if text!=(r.HERE/'results'/name).read_text(encoding='utf-8'):raise RuntimeError('PUBLIC_TABLE_REPLAY_MISMATCH')
    env=dict(os.environ);env['PYTHONPATH']=str(r.PREVIOUS)+os.pathsep+str(r.OLD)+os.pathsep+str(r.HERE)
    runner="import sys,unittest,json;sys.path.insert(0,sys.argv[1]);a=unittest.TestLoader().discover(sys.argv[1],pattern='m4_numerical_tests.py');b=unittest.TestLoader().discover(sys.argv[2],pattern='m4_control_tests.py');s=unittest.TestSuite([a,b]);r=unittest.TextTestRunner(verbosity=2).run(s);print(json.dumps(dict(count=r.testsRun,passed=r.wasSuccessful(),skipped=len(r.skipped))));sys.exit(0 if r.wasSuccessful() else 1)"
    result=subprocess.run([sys.executable,'-c',runner,str(r.HARNESS/'patched'),str(r.HERE)],cwd=r.ROOT,env=env,capture_output=True,text=True)
    log=output/'eight_fixed_checks.log';log.write_text(result.stdout+result.stderr,encoding='utf-8');report=r.json.loads(result.stdout)
    numeric=result.returncode==0 and report['count']==8 and report['passed'] and report['skipped']==0
    verify();after=manifest();passed=before==after and numeric and all(x['exit_code']==0 for x in checks) and sum(x['count'] for x in checks)==204
    r.save(output/'receipt.json',dict(passed=passed,regressions=checks,regression_count=sum(x['count'] for x in checks),synthetic_checks_repeated=8 if numeric else 0,
        numeric_log_sha256=r.sha(log),start_manifest_sha256=before,end_manifest_sha256=after,public_tables_reproduced=True,
        neural_access=False,source_requests=0,real_fits_repeated=False,live_isolation_repeated=False,unexecuted_science_reproduced=False,final_access=False))
    print('SAVED_PUBLIC_RESULTS_AND_SYNTHETIC_ONLY',passed)
    if not passed:raise SystemExit(1)


if __name__=='__main__':main()
