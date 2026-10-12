import subprocess
import sys
from datetime import datetime,timezone
import study as r


def main():
    command=[sys.executable,'-m','unittest','discover','-s',str(r.HERE),'-p','test_*.py','-v']
    result=subprocess.run(command,cwd=r.ROOT,capture_output=True,text=True)
    out=r.HERE/'results/focused_tests.log';out.parent.mkdir(exist_ok=True)
    out.write_text(result.stdout+result.stderr,encoding='utf-8')
    r.save(r.HERE/'results/focused_tests.json',dict(utc=datetime.now(timezone.utc).isoformat(),command=command,
        passed=result.returncode==0,exit_code=result.returncode,log_sha256=r.sha(out),
        test_sha256={path.name:r.sha(path) for path in r.HERE.glob('test_*.py')}))
    print(result.stdout+result.stderr)
    if result.returncode:raise SystemExit(result.returncode)


if __name__=='__main__':main()
