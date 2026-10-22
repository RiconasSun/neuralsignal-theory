"""Read-only live journal metadata; incomplete last write is not a receipt."""
import collections,datetime,hashlib,json,time
from pathlib import Path
R=Path(__file__).resolve().parents[4];P=R/'paper16_development_r5'
def load(p):return json.loads(p.read_bytes())
def rows(p):
    if not p.exists():return []
    raw=p.read_text(encoding='utf8');items=raw.splitlines()
    if raw and not raw.endswith('\n'):items=items[:-1]
    return [json.loads(x) for x in items]
stage=load(P/'results/STAGE_CLAIM.json');journal=rows(P/'results/FIT_JOURNAL.jsonl');counts=collections.Counter(r['event'] for r in journal)
complete=[r for r in journal if r['event']=='COMPLETED'];totals=collections.Counter();max_pg=None
for row in complete:
    result=load(R/row['result_path']);totals['FG']+=result['external_value_gradient_pairs'];totals['accepted']+=result['external_accepted_iterations'];max_pg=max(max_pg or 0.,result['projected_gradient_inf'])
terminal={r['task']['id'] for r in journal if r['event'] in ['COMPLETED','FAILED']};active=[r['task']['id'] for r in journal if r['event']=='ATTEMPTED' and r['task']['id'] not in terminal]
out={'attempted':counts['ATTEMPTED'],'completed':counts['COMPLETED'],'failed_journal_entries':counts['FAILED'],'unattempted':2479-counts['ATTEMPTED'],'active_task':active[-1] if active else None,'completed_FG':totals['FG'],'completed_accepted':totals['accepted'],'max_completed_PG':max_pg,'elapsed_seconds':time.monotonic()-stage['start_monotonic'],'unchanged_deadline_UTC':stage['deadline_UTC'],'scientific_stop':load(P/'results/SCIENTIFIC_STOP.json') if (P/'results/SCIENTIFIC_STOP.json').exists() else None,'M4_ready':(P/'results/M4_READY_FOR_INDEPENDENT_REVIEW.json').exists(),'worker_complete':(P/'results/WORKER_COMPLETE.json').exists(),'E_executed':False,'Final_access':False}
if active:
    folder=P/'work/fits'/hashlib.sha256(active[-1].encode()).hexdigest()
    calls=rows(folder/'CALLS.jsonl')
    out['active_FG_reserved']=sum(r['event']=='RESERVED_BEFORE_EVALUATION' for r in calls)
    out['active_FG_completed']=sum(r['event']=='COMPLETED' for r in calls)
    out['active_accepted_iterations']=len(rows(folder/'ACCEPTED.jsonl'))
print(json.dumps(out,indent=2,allow_nan=False))
