import hashlib
import subprocess
import sys
import uuid
from pathlib import Path
import study as r
from custody_security import prepare,require_custodian
from history_guard import verify
from atomic_checkpoint import commit,read


def cases(root,context):
    rows=[]
    for size in (1,4194303,4194304,4194305):
        trial=prepare(root/('size_'+str(size)));body=b'x'*size;source=dict(dataset='synthetic-boundary',bytes=size)
        try:
            receipt=commit(trial,'block',body,source)
            passed=size<=4194304 and read(trial/'block.checkpoint',source,hashlib.sha256(body).hexdigest())==body
            rows.append(dict(context=context,size=size,passed=passed,successful_commit=True,receipt=receipt))
        except ValueError as exc:
            rows.append(dict(context=context,size=size,passed=size==4194305 and str(exc)=='BODY_SIZE_INVALID' and not (trial/'block.checkpoint').exists(),
                successful_commit=False,expected_safe_stop=True,error_code=str(exc)))
        except Exception as exc:
            rows.append(dict(context=context,size=size,passed=False,successful_commit=False,error_type=type(exc).__name__))
    return rows


def main():
    require_custodian()
    if '--child' in sys.argv:
        r.save(Path(sys.argv[3]),cases(prepare(Path(sys.argv[2])),'fresh_trusted_host_child'));return
    verify();root=prepare(r.HERE/'.private'/('boundary_'+uuid.uuid4().hex))
    rows=cases(prepare(root/'main'),'trusted_host_main');output=root/'child.json'
    process=subprocess.run([sys.executable,str(Path(__file__).resolve()),'--child',str(root/'child'),str(output)],capture_output=True,text=True)
    if process.returncode:raise RuntimeError('BOUNDARY_CHILD_FAILED')
    rows+=r.load(output)
    r.save(r.HERE/'results/boundaries.json',dict(rows=rows,passed=len(rows)==8 and all(x['passed'] for x in rows),
        source_requests=0,protected_neural_contents_read=False,code_sha256=r.sha(r.HERE/'boundary_cases.py'),
        registration_sha256=r.sha(r.HERE/'BOUNDARY_REGISTRATION.json')),True)
    print(dict(boundary_cases=len(rows),passed=sum(x['passed'] for x in rows),successful_commits=sum(x['successful_commit'] for x in rows)))


if __name__=='__main__':main()
