"""No neural access: revalidate frozen public results, tables and synthetic tests."""
import csv
import io
import os
import subprocess
import sys
from datetime import datetime,timezone
import study as r
from closure_verify import verify as verify_history


def verify_results():
    seal=r.load(r.HERE/'final_manifest.json')
    for name,digest in seal['sha256'].items():
        if r.sha(r.HERE/name)!=digest:raise RuntimeError('SAVED_RESULT_CHANGED:'+name)
    return r.sha(r.HERE/'final_manifest.json')


def table():
    stream=io.StringIO(newline='');writer=csv.writer(stream,lineterminator='\n')
    writer.writerow(['phase','session','region','kind','ridge','seed','converged','iterations','objective_calls','projected_gradient','training_LL_nats_per_unit_bin','validation_LL_nats_per_unit_bin'])
    for phase in ('diagnosis','smoke','full'):
        for path in sorted((r.HERE/'results'/phase).glob('*.json')):
            x=r.load(path)
            if 'kind' not in x:continue
            writer.writerow([phase,x['session_id'],x['region'],x['kind'],x['ridge'],x['seed'],x['converged'],x['iterations'],x['objective_calls'],x['projected_gradient'],x['training_LL_nats_per_unit_bin'],x.get('validation_LL_nats_per_unit_bin','NOT_ACCESSED')])
    return stream.getvalue()


def main():
    verify_history();before=verify_results();checks=[]
    from saved_links import verify
    native_link_count=verify()
    env=dict(os.environ);env['PYTHONPATH']=str(r.OLD)
    output=r.HERE/'replay';output.mkdir(exist_ok=True)
    for folder in ('paper12_custody1','paper12_transport1','paper12_checkpoint1','paper12_resume1','paper12_m3num1'):
        command=[sys.executable,'-m','unittest','discover','-s',folder,'-p','test_*.py','-v']
        result=subprocess.run(command,cwd=r.ROOT,env=env,capture_output=True,text=True)
        log=output/(folder+'.log');log.write_text(result.stdout+result.stderr,encoding='utf-8')
        checks.append(dict(folder=folder,exit_code=result.returncode,log_sha256=r.sha(log)))
    rendered=table();(output/'fit_diagnostics.csv').write_text(rendered,encoding='utf-8',newline='')
    if rendered!=(r.HERE/'results/fit_diagnostics.csv').read_text(encoding='utf-8'):raise RuntimeError('TABLE_REPLAY_MISMATCH')
    from public_tables import csv_text
    baseline=csv_text()
    (output/'baseline_comparison.csv').write_text(baseline,encoding='utf-8',newline='')
    if baseline!=(r.HERE/'results/baseline_comparison.csv').read_text(encoding='utf-8'):raise RuntimeError('BASELINE_TABLE_REPLAY_MISMATCH')
    verify_history();after=verify_results()
    passed=before==after and all(x['exit_code']==0 for x in checks)
    r.save(output/'receipt.json',dict(utc=datetime.now(timezone.utc).isoformat(),checks=checks,passed=passed,
        start_manifest_sha256=before,end_manifest_sha256=after,public_table_reproduced=True,
        baseline_table_reproduced=True,
        native_links_revalidated=native_link_count,
        neural_access=False,source_requests=0,live_isolation_repeated=False,fits_repeated=False,
        unexecuted_scientific_stages_reproduced=False,final_access=False))
    print('SAVED_PUBLIC_RESULTS_TABLES_SYNTHETIC_TESTS',passed)
    if not passed:raise SystemExit(1)


if __name__=='__main__':main()
