"""Conditional unchanged M4 sources and numerical gate; never executed before M3."""
import os
import json
import shutil
import subprocess
import sys
from datetime import datetime,timezone
import study as r
from transitions import completed
from prepare import security


def main():
    r.verify();bindings=completed(r,'full',1638);a=security()
    rows=[]
    for p in sorted((r.HERE/'results/full').glob('*.json')):
        value=r.load(p)
        if value.get('family')=='baseline':
            rows.append({k:v for k,v in value.items() if k not in ('objective_history','accepted_iteration_history','conditioning')})
    if len(rows)!=1638:raise RuntimeError('M3_FULL_ROSTER_REQUIRED')
    code=r.HERE/'exports/m4code';code.mkdir(exist_ok=False);a.protect(code)
    sources={name:r.PREVIOUS/name for name in ('model_math.py','task_offset.py','competition.py','model_worker.py','m4_numerical_tests.py')}
    sources.update({name:r.OLD/name for name in ('baseline_features.py','baseline_fit.py','native_analysis_check.py')})
    sources.update({name:r.ROOT/'paper11_v2/scripts'/name for name in ('predictive_models.py','predictive_models_code1.py','r2_models.py')})
    for name,path in sources.items():shutil.copy2(path,code/name)
    r.save(code/'baseline_metrics.json',dict(rows=rows,M3_gate_sha256=bindings['gate']),True)
    r.save(r.HERE/'M4_registration.json',dict(utc=datetime.now(timezone.utc).isoformat(),
        preceding_M3_sha256=bindings,source_sha256={p.relative_to(r.ROOT).as_posix():r.sha(p) for p in sources.values()},
        native_code_sha256={p.name:r.sha(p) for p in code.iterdir() if p.is_file()},
        launcher_sha256=r.sha(r.HERE/'launch_m4.py'),policy_sha256=r.sha(r.PREVIOUS/'M4_implementation_policy.json'),
        input_manifest_sha256=r.load(r.HERE/'results/full_preflight.json')['manifest_sha256'],
        full_preflight_sha256=r.sha(r.HERE/'results/full_preflight.json'),
        runtime_provenance_sha256=r.sha(r.HERE/'results/runtime_provenance.json'),
        runtime_sha256=r.load(r.HERE/'optimizer_amendment.json')['runtime_sha256'],
        original_M4_optimizer_and_offset_unchanged=True,before_numerical_tests=True,before_real_fits=True),True)
    runner="import sys,unittest,json;sys.path.insert(0,sys.argv[1]);s=unittest.defaultTestLoader.discover(sys.argv[1],pattern='m4_numerical_tests.py');r=unittest.TextTestRunner(verbosity=2).run(s);print(json.dumps(dict(count=r.testsRun,passed=r.wasSuccessful())));sys.exit(0 if r.wasSuccessful() else 1)"
    command=[sys.executable,'-c',runner,str(code)]
    env=dict(os.environ);env.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
    test=subprocess.run(command,cwd=r.ROOT,capture_output=True,text=True,env=env)
    report=json.loads(test.stdout)
    passed=test.returncode==0 and report['passed'] is True and report['count']==5
    log=r.HERE/'results/M4/numerical_tests.log';log.parent.mkdir(parents=True,exist_ok=True);log.write_text(test.stdout+test.stderr,encoding='utf-8')
    r.save(log.parent/'numerical_gate.json',dict(gate='PASS' if passed else 'FAIL',exit_code=test.returncode,tests_run=report['count'],
        registration_sha256=r.sha(r.HERE/'M4_registration.json'),log_sha256=r.sha(log),synthetic_only=True),True)
    print(test.stdout+test.stderr)
    if not passed:raise SystemExit(1)


if __name__=='__main__':main()
