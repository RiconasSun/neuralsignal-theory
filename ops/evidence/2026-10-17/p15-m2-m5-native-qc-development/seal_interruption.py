"""Seal the stopped execution; hash saved artifacts, never load neural arrays."""
import collections
import datetime
import json
from paper15_dev.source import P,R,dump
from paper15_dev.training import sha

E=R/'ops/evidence/2026-10-17/p15-m2-m5-native-qc-development'
plan=json.loads((P/'A_FIT_PLAN.json').read_text())
rows=[]
for subject in plan['subjects']:
    for config in plan['configurations']:
        path=P/'fits'/subject/(config['id']+'.json')
        if path.exists():
            doc=json.loads(path.read_text())
            rows.append(dict(subject=subject,configuration=config['id'],family=config['family'],
                status=doc['status'],sha256=sha(path),bytes=path.stat().st_size))
counts=collections.Counter(r['status'] for r in rows)
retained={}
for path in P.rglob('*'):
    if not path.is_file() or '__pycache__' in path.parts:continue
    rel=path.relative_to(P).as_posix()
    if rel.startswith('work/') and not (rel.endswith('.log') or rel.startswith(('work/A_features/','work/A_features_attempt1/','work/A_exports/','work/full_synthetic_reference_journals/'))):continue
    retained[rel]=dict(sha256=sha(path),bytes=path.stat().st_size,git_archive=not rel.startswith('work/'))
result=dict(mission='P15-M2-M5-NATIVE-QC-AND-DEVELOPMENT',time=datetime.datetime.now(datetime.timezone.utc).isoformat(),
    interruption=dict(session=42960,action='write_stdin Ctrl-C',exit_code=1,reason='Confirmed native-time serialization changes registered wheel nuisance inputs; critical source/causal-input gate stop',
        active_state_note='STARTED journal is original crash/interruption evidence; no endpoint or optimizer trace was fabricated. In-memory progress was not durably checkpointed.'),
    planned=plan['total_main'],attempted=len(rows),completed=sum(v for k,v in counts.items() if k!='STARTED'),
    numerical_pass=counts['NUMERICAL_PASS'],numerical_fail=counts['NUMERICAL_FAIL'],interrupted=counts['STARTED'],unattempted=plan['total_main']-len(rows),
    attempt_rows=rows,preserved_artifacts=retained,
    scientific_usability='Not accepted as frozen-native scientific fits; numerical PASS applies only to implemented rounded-input objectives',
    B_selection_executed=False,E_evaluation_executed=False,Final_neural_access=False,retries=0)
target=E/'INTERRUPTION_SEAL.json';assert not target.exists();dump(target,result)
print(json.dumps({k:result[k] for k in ('planned','attempted','completed','numerical_pass','numerical_fail','interrupted','unattempted')}))
