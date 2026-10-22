"""Offline saved-only R5 verification. No scientific package/model imports."""
import argparse,collections,datetime,hashlib,json,math,socket,sys
from pathlib import Path
import numpy as np

R=Path(__file__).resolve().parents[4];P=R/'paper16_development_r5';E=Path(__file__).resolve().parent

def load(path):return json.loads(Path(path).read_bytes())
def sha(path):
    with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def need(value,message):
    if not value:raise AssertionError(message)
def lines(path):return [json.loads(x) for x in Path(path).read_text(encoding='utf8').splitlines()] if Path(path).exists() else []
def identity(a):return {'shape':list(a.shape),'dtype':a.dtype.str,'sha256':hashlib.sha256(a.tobytes()).hexdigest()}
def receipt(row):
    path=R/row['path'];need(sha(path)==row['sha256'],'Saved state file hash: '+row['path'])
    with np.load(path,allow_pickle=False) as z:values={k:z[k].copy() for k in z.files}
    need({k:identity(v) for k,v in values.items()}==row['arrays'],'Saved state member hashes')
    return values

def coordinates(folder,result):
    d=load(folder/'DIAGNOSTICS.json');need(sha(folder/'DIAGNOSTICS.json')==result['diagnostic_state_sha256'],'Diagnostics hash')
    c=receipt(d['coordinate_state']);initial=receipt(load(folder/'ATTEMPT.json')['bounds']);end=receipt(result['endpoint_state'])
    p=len(initial['x0']);need(d['free_coordinates']==p and len(d['checkpoints'])==3,'Three complete checkpoints')
    need((d['FD_objective_calls'],d['AD_calls'],d['analytic_checkpoint_calls'])==(24*p,3,3),'Original diagnostic budgets')
    for name,row in zip(['initial','halfway','endpoint'],d['checkpoints']):
        x,g,ad=[c[name+k] for k in ['_x','_analytic','_AD']]
        need(all(a.shape==(p,) and np.isfinite(a).all() for a in [x,g,ad]),'Finite full coordinates')
        need(np.all(x>=initial['lo']-1e-12) and np.all(x<=initial['hi']+1e-12),'Original bounds')
        error=np.abs(g-ad)/np.maximum(1,np.maximum(np.abs(g),np.abs(ad)))
        need(np.array_equal(error,c[name+'_AD_error']) and float(error.max())==row['AD_scaled_coordinate_error_max']<=1e-8,'Saved AD coordinate arithmetic')
        for h in [.001,.0001,.00001,.000001]:
            fd=c[name+'_FD_'+str(h)];error=np.abs(fd-g)/np.maximum(1,np.maximum(np.abs(fd),np.abs(g)))
            need(fd.shape==(p,) and np.isfinite(fd).all() and np.array_equal(error,c[name+'_FD_error_'+str(h)]) and float(error.max())==row['FD_scaled_coordinate_errors'][str(h)],'Saved four-scale FD arithmetic')
        need(row['checkpoint']==name and row['pass'] is True and row['frozen_FD_scaled_error']==row['FD_scaled_coordinate_errors']['1e-05']<=2e-5,'Original fixed FD acceptance, no favorable-scale selection')
        need(math.isfinite(row['objective']) and math.isfinite(row['AD_objective']) and np.isclose(row['objective'],row['AD_objective'],atol=1e-10,rtol=1e-12),'Saved objective/AD equality')
    need(np.array_equal(c['initial_x'],initial['x0']) and np.array_equal(c['endpoint_x'],end['x']) and np.array_equal(c['endpoint_analytic'],end['gradient']),'Original initial and endpoint vectors')
    x,g=end['x'],end['gradient'];pg=float(np.abs(np.where(((x<=initial['lo']+1e-12)&(g>0))|((x>=initial['hi']-1e-12)&(g<0)),0,g)).max())
    need(pg==result['projected_gradient_inf']<=1e-5 and result['numerical_pass'] is True and d['all_checkpoints_pass'] is True,'Full original PG/AD/FD pass')
    need(result['nfev']==result['external_value_gradient_pairs']<=6000 and result['nit']==result['external_accepted_iterations']<=1500,'Original external counters')
    return p,pg

def run(manifest):
    archive=load(manifest);all_files=archive['files'];need(len({r['path'] for r in all_files})==len(all_files),'Unique archive inventory')
    for row in all_files:need(sha(R/row['path'])==row['sha256'],'Archive bytes changed: '+row['path'])
    plan=[r['task'] for r in load(R/'paper16_shutdown_recovery_r5_protocol/RECOVERY_TASK_PLAN.json')['tasks']]
    journal=lines(P/'results/FIT_JOURNAL.jsonl');attempted=[r['task'] for r in journal if r['event']=='ATTEMPTED'];completed=[r for r in journal if r['event']=='COMPLETED'];failed=[r for r in journal if r['event']=='FAILED']
    need(len(plan)==2479 and attempted==plan[:len(attempted)] and len(attempted)<=2479,'Exact ordered single attempts')
    need(len({t['id'] for t in attempted})==len(attempted),'No retries')
    need([r['task'] for r in completed]==attempted[:len(completed)] and len(failed)<=1,'Ordered completions and stop')
    totals=collections.Counter();max_pg=0.;passed=0
    for task in attempted:
        folder=P/'work/fits'/hashlib.sha256(task['id'].encode()).hexdigest()
        calls=lines(folder/'CALLS.jsonl');reserved=[r for r in calls if r['event']=='RESERVED_BEFORE_EVALUATION'];done=[r for r in calls if r['event']=='COMPLETED'];accepted=lines(folder/'ACCEPTED.jsonl')
        need(len(done)<=len(reserved)<=6000 and len(accepted)<=1500,'Actual reserved/completed counter bounds')
        totals['FG_reserved']+=len(reserved);totals['FG_completed']+=len(done);totals['accepted_iterations']+=len(accepted)
        for row in lines(folder/'DIAGNOSTIC_CALLS.jsonl'):totals[row['kind']]+=1
        matches=[r for r in completed if r['task']['id']==task['id']]
        if not matches:continue
        terminal=matches[0];need(len(matches)==1 and terminal['result_path']==(folder/'RESULT.json').relative_to(R).as_posix() and terminal['result_sha256']==sha(folder/'RESULT.json'),'Exact result/terminal join')
        result=load(folder/'RESULT.json');need(result['task']==task,'Exact completed task')
        _,pg=coordinates(folder,result);need(len(done)==len(reserved)==result['nfev'] and len(accepted)==result['nit'],'Saved FG/accepted counters')
        totals['complete_diagnostic_reports']+=1;max_pg=max(max_pg,pg);passed+=1
    caps={'FG_reserved':14874000,'accepted_iterations':3718500,'FD_RESERVED':21894528,'AD_RESERVED':7437,'ANALYTIC_RESERVED':7437}
    for key,cap in caps.items():need(totals[key]<=cap,'Original global resource cap '+key)
    phase=load(P/'results/STAGE_CLAIM.json') if (P/'results/STAGE_CLAIM.json').exists() else None
    if phase:
        delta=(datetime.datetime.fromisoformat(phase['deadline_UTC'])-datetime.datetime.fromisoformat(phase['start_UTC'])).total_seconds()
        need(delta==172800 and 0<phase['deadline_monotonic']-phase['start_monotonic']<=172800 and phase['no_reset'] is True,'One unchanged 48-hour stage')
    if (P/'results/SCIENTIFIC_STOP.json').exists():verdict=load(P/'results/SCIENTIFIC_STOP.json')['scientific_status']
    elif (P/'results/WORKER_COMPLETE.json').exists():
        outcome=load(P/'results/WORKER_COMPLETE.json');need(outcome['M4'] is True and outcome['E'] is False and outcome['Final_C_D_access'] is False,'M4-only completion')
        need(passed==2479 and (E/'M4_APPROVAL.json').exists(),'Complete independently reviewed M4 required')
        verdict='M4_COMPLETE_INDEPENDENTLY_ACCEPTED'
    else:
        need((E/'PREFLIGHT_SCIENTIFIC_STOP.json').exists(),'No terminal scientific evidence; active work is not a saved PASS')
        verdict=load(E/'PREFLIGHT_SCIENTIFIC_STOP.json')['scientific_status']
    need(not (P/'results/E_BATCH_CLAIM.json').exists() and not (P/'work/E').exists(),'E never authorized/executed')
    out={'mission':'P16-M3-M5-SHUTDOWN-RECOVERY-R5','saved_only_verification':'PASS','scientific_verdict':verdict,'new_attempted':len(attempted),'new_numerical_passes':passed,'new_failed_journal_entries':len(failed),'unattempted':2479-len(attempted),'max_completed_PG':max_pg if passed else None,'resources':dict(totals),'partial_diagnostic_completed_counts':'Unknown beyond complete saved reports; reservations are not completions','archive_manifest_sha256':sha(manifest),'reproducer_sha256':sha(__file__),'scientific_model_imports':0,'new_fits_derivatives_scores':0,'E_access':False,'Final_C_D_access':False}
    return out

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--manifest',default=str(P/'LOCAL_ARCHIVE_MANIFEST.json'));args=parser.parse_args()
    def denied(*a,**k):raise RuntimeError('Saved-only reproduction forbids network')
    socket.socket.connect=denied;socket.socket.connect_ex=denied;socket.create_connection=denied
    print(json.dumps(run(Path(args.manifest)),indent=2,allow_nan=False))
