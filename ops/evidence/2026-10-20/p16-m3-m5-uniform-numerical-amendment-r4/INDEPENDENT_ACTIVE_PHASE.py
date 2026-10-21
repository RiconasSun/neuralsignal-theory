"""Observe complete journal lines only; never evaluates a scientific function."""
from pathlib import Path
import datetime,hashlib,json,os
P=Path('paper16_development_r4')
E=Path('ops/evidence/2026-10-20/p16-m3-m5-uniform-numerical-amendment-r4')
def rows(path):
    if not path.exists():return []
    raw=path.read_bytes()
    if not raw.endswith(b'\n'):raw=raw.rsplit(b'\n',1)[0]
    return [json.loads(x) for x in raw.splitlines()]
def snapshot():
    journal=rows(P/'results/FIT_JOURNAL.jsonl')
    attempts=[r for r in journal if r['event']=='ATTEMPTED']
    terminal={r['task']['id'] for r in journal if r['event'] in ['COMPLETED','FAILED']}
    active=next((r['task'] for r in reversed(attempts) if r['task']['id'] not in terminal),None)
    out=dict(recorded_UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),event='INDEPENDENT_ACTIVE_PHASE_SNAPSHOT',attempts=len(attempts),completed=sum(r['event']=='COMPLETED' for r in journal),failures=sum(r['event']=='FAILED' for r in journal),active_task=active['id'] if active else None,new_scientific_calls=0)
    if active:
        folder=P/'work/fits'/hashlib.sha256(active['id'].encode()).hexdigest()
        diagnostic=rows(folder/'DIAGNOSTIC_CALLS.jsonl');calls=rows(folder/'CALLS.jsonl')
        out.update(phase='SAVED_STATE_WRITE' if (folder/'DIAGNOSTICS.json').exists() else 'DERIVATIVE_CERTIFICATE' if diagnostic else 'OPTIMIZER' if calls else 'INITIALIZATION',FG_completed=sum(r['event']=='COMPLETED' for r in calls),accepted_iterations=len(rows(folder/'ACCEPTED.jsonl')),diagnostic_reservations=len(diagnostic),last_checkpoint=diagnostic[-1].get('checkpoint') if diagnostic else None,last_diagnostic_kind=diagnostic[-1]['kind'] if diagnostic else None)
    with (E/'INDEPENDENT_ACTIVE_PHASE_PROGRESS.jsonl').open('a',encoding='utf8',newline='\n') as f:
        f.write(json.dumps(out)+'\n');f.flush();os.fsync(f.fileno())
    print(json.dumps(out),flush=True)
if __name__=='__main__':snapshot()
