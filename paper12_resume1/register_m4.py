"""Register sources and frozen tests before numerical verification and real fitting."""
import subprocess
import sys
from datetime import datetime,timezone
import study as r
from register_m3 import guard_adapter


def main():
    guard_adapter()
    gate=r.HERE/'results/M3/progressive1/gate_result.json'
    if r.load(gate)['gate']!='PASS':raise RuntimeError('M3_PASS_REQUIRED')
    rows=[]
    for path in sorted((gate.parent).glob('*.json')):
        value=r.load(path)
        if value.get('family')=='baseline':rows.append(value)
    r.save(r.HERE/'baseline_metrics.json',dict(rows=rows,M3_gate_sha256=r.sha(gate)),True)
    names=['model_math.py','task_offset.py','competition.py','model_worker.py','launch_m4.py','register_m4.py',
           'M4_implementation_policy.json','m4_numerical_tests.py','baseline_metrics.json']
    files=[r.HERE/x for x in names]+[r.ROOT/'paper11_v2/scripts'/x for x in ('predictive_models.py','predictive_models_code1.py','r2_models.py')]
    r.save(r.HERE/'M4_implementation_registration.json',dict(utc=datetime.now(timezone.utc).isoformat(),
        before_numerical_verification=True,before_real_dynamics_fits=True,
        M3_gate_sha256=r.sha(gate),sha256={p.relative_to(r.ROOT).as_posix():r.sha(p) for p in files}),True)
    command=[sys.executable,'-m','unittest','discover','-s','paper12_resume1','-p','m4_numerical_tests.py','-v']
    run=subprocess.run(command,cwd=r.ROOT,capture_output=True,text=True)
    log=r.HERE/'results/M4/numerical_tests.log';log.parent.mkdir(parents=True,exist_ok=True);log.write_text(run.stdout+run.stderr,encoding='utf-8')
    r.save(log.parent/'numerical_gate.json',dict(gate='PASS' if run.returncode==0 else 'FAIL',command=command,
        exit_code=run.returncode,log_sha256=r.sha(log),registered_sources_sha256=r.sha(r.HERE/'M4_implementation_registration.json'),
        fixture_scope_only=True,real_model_fits=False,final_evaluation_accessed=False),True)
    print(run.stdout+run.stderr)
    if run.returncode:raise SystemExit(run.returncode)


if __name__=='__main__':main()
