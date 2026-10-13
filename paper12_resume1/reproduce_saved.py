"""Public saved-results replay only; never calls real extraction or private QC."""
import subprocess
import sys
from datetime import datetime,timezone
import study as r


def verify_manifest():
    manifest=r.load(r.HERE/'final_manifest.json')
    for name,digest in manifest['sha256'].items():
        if r.sha(r.HERE/name)!=digest:raise RuntimeError('SAVED_INPUT_CHANGED:'+name)
    return r.sha(r.HERE/'final_manifest.json')


def main():
    r.verify();before=verify_manifest();rows=[]
    commands=[['powershell','-NoProfile','-ExecutionPolicy','Bypass','-File',str(r.OLD/'reproduce2.ps1')],
              [sys.executable,str(r.HERE/'run_tests.py')],
              [sys.executable,str(r.HERE/'saved_table_replay.py')],
              [sys.executable,str(r.HERE/'public_tables.py')],
              [sys.executable,str(r.HERE/'failed_m3_report.py')]]
    for i,command in enumerate(commands):
        run=subprocess.run(command,cwd=r.ROOT,capture_output=True,text=True)
        path=r.HERE/'replay'/('check_'+str(i)+'.log');path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(run.stdout+run.stderr,encoding='utf-8')
        rows.append(dict(command=command,exit_code=run.returncode,log=path.relative_to(r.HERE).as_posix(),sha256=r.sha(path)))
        if run.returncode:break
    r.verify();after=verify_manifest()
    passed=len(rows)==5 and all(x['exit_code']==0 for x in rows) and before==after
    receipt=dict(utc=datetime.now(timezone.utc).isoformat(),checks=rows,passed=passed,
        start_manifest_sha256=before,end_manifest_sha256=after,source_requests=0,
        private_contents_read=False,live_isolation_repeated=False,real_extraction_repeated=False,
        unexecuted_models_reproduced=False,final_evaluation_accessed=False,
        scope='Saved public hashes/tables and synthetic regression tests only')
    r.save(r.HERE/'replay/reproduction_receipt.json',receipt)
    print(receipt)
    if not passed:raise SystemExit(1)


if __name__=='__main__':main()
