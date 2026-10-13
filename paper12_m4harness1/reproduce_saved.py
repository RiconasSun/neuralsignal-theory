"""Saved-only integrity/tables plus original synthetic checks; never real fits."""
import os
import re
import subprocess
import sys
import study as r
from closure_verify import verify
from run_regressions import run
from summarize import table,offset_table


def check_manifest():
    manifest=r.load(r.HERE/'final_manifest.json')
    for name,digest in manifest['sha256'].items():
        if r.sha(r.HERE/name)!=digest:raise RuntimeError('SAVED_RESULT_CHANGED:'+name)
    return r.sha(r.HERE/'final_manifest.json')


def main():
    verify(archive_required=True);before=check_manifest();output=r.HERE/'replay';output.mkdir(exist_ok=True)
    checks=run(output)
    for name,render in (('numerical_error_table.csv',table),('offset_diagnostics.csv',offset_table)):
        text=render();(output/name).write_text(text,encoding='utf-8',newline='')
        if text!=(r.HERE/'results'/name).read_text(encoding='utf-8'):raise RuntimeError('PUBLIC_TABLE_MISMATCH:'+name)
    env=dict(os.environ);env.update(PYTHONPATH=str(r.PREVIOUS),OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
    cmd=[sys.executable,'-m','unittest','discover','-s',str(r.HERE/'patched'),'-p','m4_numerical_tests.py','-v']
    result=subprocess.run(cmd,cwd=r.ROOT,env=env,capture_output=True,text=True)
    text=result.stdout+result.stderr;log=output/'frozen_five_checks.log';log.write_text(text,encoding='utf-8')
    count=re.search(r'^Ran (\d+) tests? in ',text,re.M)
    numeric_ok=result.returncode==0 and count and int(count[1])==5 and 'skipped' not in text.lower()
    verify(archive_required=True);after=check_manifest()
    passed=before==after and all(x['exit_code']==0 for x in checks) and sum(x['test_count'] for x in checks)==193 and bool(numeric_ok)
    r.save(output/'receipt.json',dict(passed=passed,regressions=checks,regression_count=sum(x['test_count'] for x in checks),
        original_numerical_categories_repeated=5 if numeric_ok else 0,numerical_exit_code=result.returncode,numerical_log_sha256=r.sha(log),
        start_manifest_sha256=before,end_manifest_sha256=after,public_tables_reproduced=True,
        source_requests=0,neural_access=False,M3_fits_repeated=False,M4_fits_repeated=False,live_isolation_repeated=False,
        unexecuted_M5_reproduced=False,final_access=False))
    print('SAVED_RESULTS_AND_SYNTHETIC_ONLY_REPRODUCTION',passed)
    if not passed:raise SystemExit(1)


if __name__=='__main__':main()
