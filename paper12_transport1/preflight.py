"""Saved-output regression evidence; no source requests or neural decoding."""
import subprocess
import sys
from datetime import datetime,timezone
import common as r


def main():
    r.verify()
    command=[sys.executable,'-m','unittest','discover','-s','paper12_transport1','-p','test_*.py','-v']
    result=subprocess.run(command,cwd=r.ROOT,capture_output=True,text=True)
    output=r.HERE/'results/preflight_tests.log';output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(result.stdout+result.stderr,encoding='utf-8')
    old=r.OLD/'replay/revision2'
    receipt=r.load(old/'reproduction_receipt.json')
    target=r.HERE/'results/prior_reproduce2';target.mkdir(parents=True,exist_ok=True)
    for path in old.iterdir():
        if path.is_file():(target/path.name).write_bytes(path.read_bytes())
    r.save(r.HERE/'results/preflight_tests.json',dict(utc=datetime.now(timezone.utc).isoformat(),
        command=command,exit_code=result.returncode,passed=result.returncode==0,
        test_code_sha256={p.name:r.sha(p) for p in r.HERE.glob('test_*.py')},
        log_sha256=r.sha(output),prior_reproduce2_receipt_sha256=r.sha(target/'reproduction_receipt.json'),
        prior_reproduce2=receipt,source_requests_executed=0))
    print(result.stdout+result.stderr)
    if result.returncode:raise SystemExit(result.returncode)


if __name__=='__main__':main()
