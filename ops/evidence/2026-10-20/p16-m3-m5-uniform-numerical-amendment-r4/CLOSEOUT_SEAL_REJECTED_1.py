"""Create-only external-interruption archive; no neural sources or model calls."""
import argparse
import datetime
import hashlib
import json
import socket
from pathlib import Path
from unittest.mock import patch

R=Path(__file__).resolve().parents[1]
P=R/'paper16_development_r4'
E=R/'ops/evidence/2026-10-20/p16-m3-m5-uniform-numerical-amendment-r4'

def load(p):return json.loads(p.read_bytes())
def sha(p):
    with p.open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def ref(p):return {'path':p.relative_to(R).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)}
def once(p,value):
    with p.open('x',encoding='utf8',newline='\n') as stream:
        json.dump(value,stream,indent=2,allow_nan=False);stream.write('\n')

def register_interruption():
    from .reproduce_saved import strict_journal
    journal=P/'results/FIT_JOURNAL.jsonl'
    raw=journal.read_bytes()
    assert raw.endswith(b'\n'),'Preserve and explicitly audit a torn journal; never silently truncate'
    attempts,terminals,active=strict_journal([json.loads(r) for r in raw.splitlines()])
    assert len(attempts)==3041 and len(terminals)==3040 and active is not None
    assert all(r['event']=='COMPLETED' for r in terminals.values())
    folder=P/'work/fits'/hashlib.sha256(active['id'].encode()).hexdigest()
    once(P/'PARTIAL_ATTEMPT_MANIFEST.json',{
        'mission':'P16-M3-M5-UNIFORM-NUMERICAL-AMENDMENT-R4','task':active,
        'endpoint_unavailable':True,'numerical_verdict':None,
        'files':[ref(p) for p in sorted(folder.iterdir()) if p.is_file()]})
    once(P/'results/EXTERNAL_INTERRUPTION_CLOSEOUT.json',{
        'schema':'R4_EXTERNAL_INTERRUPTION_V1',
        'mission':'P16-M3-M5-UNIFORM-NUMERICAL-AMENDMENT-R4',
        'registered_closeout_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'scientific_verdict':'STOP_EXECUTION_INTERRUPTED_REQUIRED_GATE',
        'native_supervision_available':False,'native_returncode':None,'termination_time':None,'cause':None,
        'scientific_resumption_authorized':False,'no_retry':True,
        'stage_claim_sha256':sha(P/'results/STAGE_CLAIM.json'),
        'supervisor_sha256':sha(P/'results/SUPERVISOR.json'),
        'fit_journal_sha256':sha(journal),'attempts':len(attempts),'completed':len(terminals),
        'independent_native_probe':ref(E/'INDEPENDENT_INTERRUPTION_NATIVE_PROBE_1.json'),
        'owner_reported_cause':'COMPUTER_SHUTDOWN',
        'owner_cause_evidence':ref(E/'OWNER_INTERRUPTION_CAUSE.json'),
        'partial_manifest_sha256':sha(P/'PARTIAL_ATTEMPT_MANIFEST.json'),
        'interpretation':'Owner confirms computer shutdown; native final process status and exact shutdown time are unavailable. No scientific restart.'})
    print(json.dumps({'interruption_receipt':ref(P/'results/EXTERNAL_INTERRUPTION_CLOSEOUT.json'),
                      'partial_manifest':ref(P/'PARTIAL_ATTEMPT_MANIFEST.json')}))

def seal():
    files=[]
    for root in [P/'work',P/'results']:
        for path in sorted(root.rglob('*')):
            if path.is_file():files.append(ref(path))
    once(P/'PROTECTED_STATE_MANIFEST.json',{
        'mission':'P16-M3-M5-UNIFORM-NUMERICAL-AMENDMENT-R4',
        'scope':'ALL_EXISTING_R4_WORK_AND_RESULTS_INCLUDING_INCOMPLETE_STATE',
        'recorded_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'files':files,'file_count':len(files),'total_bytes':sum(r['bytes'] for r in files),
        'protected_arrays_publication_authorized':False,'no_new_scientific_calls':True})
    print(json.dumps({'protected_manifest':ref(P/'PROTECTED_STATE_MANIFEST.json'),'files':len(files)},flush=True))

def facts():
    from .reproduce_saved import facts as observed_facts
    observed,attempted=observed_facts()
    plan=load(P/'NEW_TASK_PLAN_CANDIDATE.json')['tasks']
    by={r['task']['id']:r for r in attempted}
    states=[]
    for task in plan:
        state=by.get(task['id'])
        states.append({'task':task,'status':'UNATTEMPTED'} if state is None else {
            **state,'status':'NUMERICAL_PASS' if state.get('numerical_pass') is True else
            'NUMERICAL_FAIL' if state.get('numerical_pass') is False else 'INTERRUPTED_INCOMPLETE'})
    once(P/'EXECUTION_FACTS.json',observed)
    once(P/'TASK_OUTCOMES.json',{'tasks':states,'planned':len(plan),'facts_sha256':sha(P/'EXECUTION_FACTS.json')})
    print(json.dumps(observed,indent=2))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('operation',choices=['register','seal','facts'])
    arguments=parser.parse_args()
    with patch.object(socket.socket,'connect',side_effect=RuntimeError('Saved-only closeout denies network')):
        {'register':register_interruption,'seal':seal,'facts':facts}[arguments.operation]()
