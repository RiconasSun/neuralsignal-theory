"""Independent saved-only audit after externally observed host/process loss.

Does not restart a scientific stage or produce a native SUPERVISION receipt.
"""
import datetime
import hashlib
import json
import socket
from pathlib import Path
from unittest.mock import patch
import numpy as np

R=Path.cwd();P=R/'paper16_development_r4';O=R/'paper16_development_r3'
E=R/'ops/evidence/2026-10-20/p16-m3-m5-uniform-numerical-amendment-r4'

def J(p):return json.loads(Path(p).read_bytes())
def H(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def C(ok,why):
    if not ok:raise AssertionError(why)
def rows(p):
    if not p.exists():return []
    b=p.read_bytes();C(not b or b.endswith(b'\n'),'Torn journal must not be silently truncated')
    return [json.loads(s) for s in b.splitlines()]
def once(path,value):
    with path.open('x',encoding='utf8',newline='\n') as f:
        json.dump(value,f,indent=2,allow_nan=False);f.write('\n')
def denied(*a,**k):raise AssertionError('No objective/AD/scoring/optimizer/network calls in independent saved-only audit')

def run():
    from paper16_development_r4 import reproduce_saved as saved,models,features
    from paper16_development_r4.core import spec,dynamics
    from paper16_termination_feasibility1 import reproduce as prior
    from scipy import optimize
    native_path=E/'INDEPENDENT_INTERRUPTION_NATIVE_PROBE_1.json';native=J(native_path)
    claim_path=P/'results/STAGE_CLAIM.json';claim=J(claim_path);supervisor=J(P/'results/SUPERVISOR.json')
    C(native['supervisor_present'] is False and native['matching_processes']==[],'Original supervisor/workers absent')
    C(native['native_supervisor_pid']==supervisor['supervisor_pid']==36728,'Exact original supervisor PID')
    C(native['job_name']==supervisor['job_name'] and native['job_open_succeeded'] is False
      and native['job_last_error']==2,'Exact named Job absent, independently queried (not access denied)')
    C(H(claim_path)==supervisor['original_stage_sha256']=='f1ea1b38264f8e98bcafe5932420bfd921a823a1186b995600f7429b7b6c2a7c','Original claim unchanged')
    C(claim['no_reset'] is True and abs(claim['deadline_monotonic']-claim['start_monotonic']-172800)<1e-6,'Original unextended48h budget')
    for name in ['SUPERVISION.json','WORKER_COMPLETE.json','M4_READY_FOR_INDEPENDENT_REVIEW.json','M4_SELECTION_FREEZE.json','E_BATCH_CLAIM.json','E_DEVELOPMENT_RESULTS.json']:
        C(not (P/'results'/name).exists(),'Interrupted stage must not have terminal/completion/E entitlement '+name)
    C(not (E/'M4_APPROVAL.json').exists(),'No complete M4 approval')
    freeze_path=P/'PREFIT_FREEZE_MANIFEST.json'
    C(H(freeze_path)=='37b40a80af9eab485ea5817b92fb77e4b3cf64e1245a6e79b9183904278183b0','Original production freeze identity')
    for item in J(freeze_path)['files']:C(H(R/item['path'])==item['sha256'],'Frozen63 file unchanged: '+item['path'])
    pins=J(P/'SOURCE_PINS.json')['files']
    for path,digest in pins.items():C(H(R/path)==digest,'Historical source/evidence pin: '+path)
    old=J(O/'PROTECTED_STATE_MANIFEST.json')['files']
    for item in old:
        path=R/item['path'];C(H(path)==item['sha256'],'Historical protected saved-state hash')
        if 'bytes' in item:C(path.stat().st_size==item['bytes'],'Historical protected saved-state size')
    journal_path=P/'results/FIT_JOURNAL.jsonl';journal=rows(journal_path)
    attempts,terminals,active=saved.strict_journal(journal)
    C(len(attempts)==3041 and len(terminals)==3040 and all(r['event']=='COMPLETED' for r in terminals.values()),'Actual interrupted 3041/3040/0 accounting')
    C(active is not None and active['id']=='763236014:S02:S:None:11:GLOBAL','Exact last partial attempt')
    plan=J(P/'NEW_TASK_PLAN_CANDIDATE.json')['tasks'];C(len(plan)==5519,'Registered task denominator')
    C([a['task'] for a in attempts]==plan[:len(attempts)],'Exact ordered prefix/no retry/no skipped task')
    ledger_path=E/'INDEPENDENT_NEW_STATE_AUDIT.jsonl';ledger=rows(ledger_path)
    accepted={r['task_id']:r for r in ledger if r['event']=='INDEPENDENT_COMPLETED_STATE_ACCEPTED'}
    C(len(ledger)==len(accepted) and 3039<=len(ledger)<=3040,'Actual prior reviewer receipt count; no impersonation')
    C(list(accepted)==[r['task']['id'] for r in journal if r['event']=='COMPLETED'][:len(ledger)],'Exact prior reviewed completion prefix')
    chain=hashlib.sha256();prefix_hashes={}
    for index,line in enumerate(ledger_path.read_bytes().splitlines(keepends=True)):
        C(json.loads(line)['previous_ledger_sha256']==(chain.hexdigest() if index else None),'Every historical reviewer ledger prefix chain')
        chain.update(line);prefix_hashes[index+1]=chain.hexdigest()
    progress=rows(E/'INDEPENDENT_NEW_REVIEW_PROGRESS.jsonl')[-1]
    C(prefix_hashes[progress['independent_completed_states_total']]==progress['ledger_sha256'],'Last persisted progress anchor; later completed receipt may precede progress flush')
    inventory={};preps={r['key']:r for r in J(O/'results/A_PREPROCESSING_STATES.json')}
    # Fresh every-byte rehash, not an mtime/size cache. Old ledger is never appended.
    for receipt in ledger:
        C(receipt['reviewer']=='/root/r4_reuse_review' and receipt['new_optimizer_calls']==receipt['new_likelihood_derivative_score_calls']==0,'Historical reviewer/proof class')
        C(receipt['prefit_manifest_sha256']==H(freeze_path) and receipt['scientific_stage_sha256']==H(claim_path),'Historical receipt stage/freeze')
        for item in receipt['files']:
            path=R/item['path'];C(path.stat().st_size==item['bytes'] and H(path)==item['sha256'],'Fresh every-byte audit of prior state: '+item['path'])
            inventory[item['path']]=item
        C(H(R/receipt['prepared_A_path'])==receipt['prepared_A_sha256'],'Historical A preparation identity')
    totals={'FG_pairs':0,'accepted_iterations':0,'fixed_FD_error_max':0.,'AD_error_max':0.,'PG_max':0.}
    new_reviews=[]
    with patch.object(models.Objective,'analytic',side_effect=denied),patch.object(models.Objective,'AD',side_effect=denied),patch.object(models.Objective,'score',side_effect=denied),patch.object(spec,'glm',side_effect=denied),patch.object(spec,'independent_AD',side_effect=denied),patch.object(dynamics,'objective',side_effect=denied),patch.object(dynamics,'independent_AD',side_effect=denied),patch.object(optimize,'minimize',side_effect=denied),patch.object(socket.socket,'connect',side_effect=denied):
        for index,attempt in enumerate(attempts):
            task=attempt['task'];tid=task['id'];folder=P/'work/fits'/hashlib.sha256(tid.encode()).hexdigest()
            C(attempt['ftol']==0. and J(folder/'ATTEMPT.json')['task']==task,'Exact amended new task')
            if tid==active['id']:continue
            terminal=terminals[tid];result,coords=prior.check_fit(folder)
            C(result['task']==task and result['numerical_pass'] is True and terminal['PG']==result['projected_gradient_inf']<=1e-5,'Every completed unchanged PG/AD/fixedFD gate')
            C(terminal['result_path']==(folder/'RESULT.json').relative_to(R).as_posix() and terminal['result_sha256']==H(folder/'RESULT.json'),'Exact completed journal/result join')
            C(result['external_value_gradient_pairs']==result['nfev']<=6000 and result['external_accepted_iterations']==result['nit']<=1500,'External frozen counters')
            C(not (folder/'FAILURE.json').exists() and (folder/'CLIENT_STDERR.log').stat().st_size==0,'No completed state failure/stderr')
            diagnostics=J(folder/'DIAGNOSTICS.json')
            totals['FG_pairs']+=result['nfev'];totals['accepted_iterations']+=result['nit']
            totals['PG_max']=max(totals['PG_max'],result['projected_gradient_inf'])
            totals['AD_error_max']=max(totals['AD_error_max'],max(c['AD_scaled_coordinate_error_max'] for c in diagnostics['checkpoints']))
            totals['fixed_FD_error_max']=max(totals['fixed_FD_error_max'],max(c['frozen_FD_scaled_error'] for c in diagnostics['checkpoints']))
            if tid not in accepted:
                prep=preps[task['mouse_id']+'/'+task['panel']]
                C(H(R/prep['path'])==prep['sha256'] and prep['role']=='A','Final previously unaudited completion original A identity')
                with np.load(R/prep['path'],allow_pickle=False) as a:z={k:a[k].copy() for k in a.files}
                C(np.all((z['ordinals']>=0)&(z['ordinals']<90)),'A-only saved derived preparation')
                batch=features.Batch(**{k:z[k] for k in ['raw','y','ordinals','unit_ids','colors','running_missing','score_mask']},dt=prep['dt'],psth=prep['psth'],b1=prep['b1'],role='A',panel=prep['panel'])
                scaler=features.Scaling(z['mean'],z['scale'],z['active'],prep['psth'])
                obj=models.Objective(batch,scaler,task['model'],1.,None,task['seed'])
                with np.load(folder/'initial.npz',allow_pickle=False) as a:initial={k:a[k].copy() for k in a.files}
                C(all(np.array_equal(initial[k],v) for k,v in [('x0',obj.x0),('lo',obj.lo),('hi',obj.hi)]),'Last completed original initializer/packing/bounds')
                files=[dict(path=x.relative_to(R).as_posix(),bytes=x.stat().st_size,sha256=H(x)) for x in sorted(folder.iterdir()) if x.is_file()]
                for item in files:inventory[item['path']]=item
                new_reviews.append(dict(task=task,reviewer='/root/r4_interruption_review',numerical_pass=True,PG=result['projected_gradient_inf'],files=files))
            if (index+1)%500==0:print(json.dumps({'fresh_completed_checked':index+1}),flush=True)
        folder=P/'work/fits'/hashlib.sha256(active['id'].encode()).hexdigest()
        C(all(not (folder/name).exists() for name in ['RESULT.json','FAILURE.json','endpoint.npz','DIAGNOSTICS.json','coordinate_certificates.npz']),'Incomplete attempt has no invented endpoint or completion')
        with np.load(folder/'initial.npz',allow_pickle=False) as a:initial={k:a[k].copy() for k in a.files}
        nr,nd=saved.accepted_prefix(rows(folder/'CALLS.jsonl'),rows(folder/'ACCEPTED.jsonl'),initial)
        diag=prior.diagnostic_prefix(rows(folder/'DIAGNOSTIC_CALLS.jsonl'),len(initial['x0']))
        partial=dict(task=active,FG_reserved=nr,FG_completed=nd,accepted_iterations=len(rows(folder/'ACCEPTED.jsonl')),diagnostic_reservations=diag,numerical_pass=None)
        for x in sorted(folder.iterdir()):
            if x.is_file():inventory[x.relative_to(R).as_posix()]=dict(path=x.relative_to(R).as_posix(),bytes=x.stat().st_size,sha256=H(x))
    access=rows(P/'results/ACCESS.jsonl');C(all(r['role']=='A' for r in access),'All actual source access records A-only')
    C(not list((P/'work').glob('roles/*/E.npz')) and not list((P/'results').glob('source_access/*/E.json')),'No E exports/source access artifacts')
    # No declaration that missing receipts prove an administrator-resistant access boundary.
    out=dict(reviewed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),reviewer='/root/r4_interruption_review',
             diagnosis='EXTERNAL_EXECUTION_INTERRUPTION_WITH_MISSING_NATIVE_FINAL_RECEIPT',original_stage_sha256=H(claim_path),
             original_supervisor_pid=36728,job_name=supervisor['job_name'],current_process_match_count=0,supervisor_absent=True,named_job_absent=True,
             native_probe_path=native_path.relative_to(R).as_posix(),native_probe_sha256=H(native_path),native_job_absence_win32_error=2,
             returncode=None,termination_time=None,cause=None,native_final_supervision_available=False,
             frozen_production_files_checked=len(J(freeze_path)['files']),historical_pins_checked=len(pins),historical_protected_files_checked=len(old),
             attempted=3041,completed=3040,numerical_failures=0,incomplete_attempted=1,unattempted=2478,
             fresh_completed_states_checked=3040,original_reviewer_receipts_preserved=len(ledger),new_independent_completion_reviews=new_reviews,
             partial_attempt=partial,completed_totals=totals,source_access_records=len(access),E_exports=0,M4_complete=False,E_executed=False,
             Final_C_access=False,Final_D_access=False,new_optimizer_calls=0,new_derivative_calls=0,new_score_calls=0,new_neural_source_access=0,
             original_ledger_sha256=H(ledger_path),journal_sha256=H(journal_path),scientific_reexecution_authorized=False,
             evidence_limitations=['Exact termination time/cause/returncode unavailable; do not classify as numerical failure or normal completion.',
                                   'Observed current process/Job absence and artifact/source-log boundary, not protection against a malicious administrator.'])
    files_path=P/'work/INDEPENDENT_INTERRUPTION_FILE_HASHES.json';once(files_path,{'files':list(inventory.values()),'fresh_every_byte':True})
    out['fresh_file_inventory']=dict(path=files_path.relative_to(R).as_posix(),sha256=H(files_path),files=len(inventory))
    once(E/'INDEPENDENT_INTERRUPTION_EVIDENCE.json',out)
    print(json.dumps({k:v for k,v in out.items() if k not in ['new_independent_completion_reviews']}),flush=True)

if __name__=='__main__':run()
