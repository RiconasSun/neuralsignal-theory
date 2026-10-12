"""Bound saved replay; optional fresh synthetic native suite, never real data."""
import subprocess
import sys
import uuid
from datetime import datetime,timezone
import study as r
from history_guard import verify
from gate import assess


def verify_manifest(expected=None):
    path=r.HERE/'final_manifest2.json';digest=r.sha(path)
    if expected is not None and digest!=expected:raise RuntimeError('REPLAY_MANIFEST_CHANGED')
    for name,value in r.load(path)['sha256'].items():
        if r.sha(r.HERE/name)!=value:raise RuntimeError('REPLAY_INPUT_CHANGED:'+name)
    if r.sha(path)!=digest:raise RuntimeError('REPLAY_MANIFEST_CHANGED')
    return digest


def main():
    start=verify_manifest();verify()
    out=r.HERE/'replay'/('run_'+uuid.uuid4().hex);out.mkdir(parents=True)
    commands=[['powershell','-NoProfile','-ExecutionPolicy','Bypass','-File',str(r.ROOT/'paper12_transport1/reproduce.ps1'),'-Python',sys.executable],
        [sys.executable,'-m','unittest','discover','-s',str(r.HERE),'-p','test_*.py','-v'],[sys.executable,str(r.HERE/'gate.py')],
        [sys.executable,str(r.HERE/'tables.py')]]
    if '--native' in sys.argv:
        commands += [[sys.executable,str(r.HERE/'native_tests.py'),'--replay',str(out/'native.json')],
            [sys.executable,str(r.HERE/'isolation_replay2.py'),'--native',str(out/'native.json'),'--output',str(out/'isolation.json'),'--runtime','--quote-retry'],
            [sys.executable,str(r.HERE/'replay_boundaries.py'),str(out/'boundaries.json')]]
    checks=[]
    for number,command in enumerate(commands):
        result=subprocess.run(command,cwd=r.ROOT,capture_output=True,text=True)
        log=out/('check_%02d.log'%number);log.write_text(result.stdout+result.stderr,encoding='utf-8')
        checks.append(dict(command=command,exit_code=result.returncode,log=log.name,sha256=r.sha(log)))
        if result.returncode:break
    fresh=None
    if '--native' in sys.argv and (out/'isolation.json').exists():
        fresh=assess(r.load(out/'native.json'),r.load(out/'isolation.json'),dict(saved_checks_pass=all(x['exit_code']==0 for x in checks)))
        if not (out/'boundaries.json').exists() or r.load(out/'boundaries.json')['passed'] is not True:
            fresh.update(gate='FAIL',verdict='CHECKPOINT_REPAIR_UNVERIFIED')
        r.save(out/'native_gate.json',fresh)
    end=verify_manifest(start)
    passed=all(x['exit_code']==0 for x in checks) and len(checks)==len(commands)
    if '--native' in sys.argv:passed=passed and fresh is not None and fresh['gate']=='PASS'
    receipt=dict(utc=datetime.now(timezone.utc).isoformat(),checks=checks,start_manifest_sha256=start,end_manifest_sha256=end,
        passed=passed,native_synthetic_replayed='--native' in sys.argv,fresh_synthetic_gate=fresh,
        original_scientific_M2_gate='FAIL/INCONCLUSIVE',neural_source_requests=0,protected_neural_contents_read=False,
        real_transport_or_scientific_experiments_reproduced=False,output_namespace=str(out.relative_to(r.HERE)))
    r.save(out/'receipt.json',receipt);print(receipt)
    if not passed:raise SystemExit(1)


if __name__=='__main__':main()
