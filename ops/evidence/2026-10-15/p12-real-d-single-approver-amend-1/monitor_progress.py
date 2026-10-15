"""Counts only newly generated SYN progress receipts; never source/key/state access."""
from datetime import datetime,timezone
import json
from pathlib import Path
import time

ROOT=Path(__file__).resolve().parents[4]
job=ROOT/'paper12_singleowner1/jobs/synthetic_2'
for _ in range(960):
    outputs=list((job/'exports').glob('P12Production.*/output'))
    value={'utc':datetime.now(timezone.utc).isoformat(),'scope':'NEW_SYNTHETIC_2_ONLY','completed_mice':sum(len(list(p.glob('completed_*.json'))) for p in outputs),'null_cases':sum(len(list(p.glob('null_*.json'))) for p in outputs),'total_null_cases':104,'failed':(job/'attempt_failure.json').exists() or any((p/'failure.json').exists() for p in outputs),'finished':(job/'result.json').exists()}
    print(json.dumps(value),flush=True)
    if value['failed'] or value['finished']:break
    time.sleep(45)
