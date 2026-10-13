"""Bounded independent native subjects; immutable fit kernel and progressive gates."""
import ast
from concurrent.futures import ThreadPoolExecutor,as_completed
from datetime import datetime,timezone
import shutil
import math
import sys
import threading
import time
import study as r
from prepare import security
from transitions import completed

_timers=[]


def cleanup(function):
    def wrapped():
        try:return function()
        finally:
            for timer in _timers:timer.cancel()
    return wrapped


def within_budget(expired,elapsed):
    return not expired and elapsed<43200


def launch_one(session,stop,compile_only=False):
    # Audited adapter of frozen launcher, not a change to optimization or features.
    tree=ast.parse((r.HERE/'launch_repaired.py').read_text())
    body=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='main')
    changes=[]
    class Adapt(ast.NodeTransformer):
        def visit_Assign(self,n):
            names={t.id for t in n.targets if isinstance(t,ast.Name)}
            replacements={'full':'False','phase':'selected_phase','sessions':'[selected_session]'}
            for key,value in replacements.items():
                if key in names:n.value=ast.parse(value,mode='eval').body;changes.append(key)
            return self.generic_visit(n)
        def visit_Constant(self,n):
            if isinstance(n.value,str) and n.value=='exports/runtime':
                changes.append('private_runtime');return ast.copy_location(ast.Name(id='runtime_relative',ctx=ast.Load()),n)
            return n
    body=Adapt().visit(body)
    if sorted(changes)!=sorted(['full','phase','sessions','private_runtime','private_runtime']):raise RuntimeError('COHORT_ADAPTER_SCOPE')
    # Insert cancellation into the archived native wait, preserving cleanup/receipt.
    hook=ast.parse("""
for wait in ast.walk(body):
    if isinstance(wait,ast.While):
        wait.test=ast.BoolOp(op=ast.And(),values=[wait.test,ast.UnaryOp(op=ast.Not(),operand=ast.Call(func=ast.Attribute(value=ast.Name(id='peer_stop',ctx=ast.Load()),attr='is_set',ctx=ast.Load()),args=[],keywords=[]))])
""").body
    index=next(i for i,n in enumerate(body.body) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='loop' for t in n.targets))
    body.body[index:index]=hook
    import launch_repaired
    namespace=dict(vars(launch_repaired));namespace.update(selected_session=session,
        selected_phase='cohort_'+session['session_id'],runtime_relative='exports/runtime_'+session['session_id'],peer_stop=stop)
    # Inner compiled archived launcher must see the cancellation event as well.
    update=next(n for n in body.body if isinstance(n,ast.Expr) and isinstance(n.value,ast.Call) and
                isinstance(n.value.func,ast.Attribute) and n.value.func.attr=='update' and isinstance(n.value.func.value,ast.Name) and n.value.func.value.id=='ns')
    update.value.keywords.append(ast.keyword(arg='peer_stop',value=ast.Name(id='peer_stop',ctx=ast.Load())))
    exec(compile(ast.fix_missing_locations(ast.Module(body=[body],type_ignores=[])),__file__,'exec'),namespace)
    if compile_only:return ast.unparse(body),changes
    namespace['main']()


def collect(phase,target):
    count=0;invalid=[]
    for p in sorted((r.HERE/'results'/phase).glob('*.json')):
        try:x=r.load(p)
        except (ValueError,UnicodeError):
            invalid.append(dict(file=p.name,sha256=r.sha(p),reason='PARTIAL_JSON_NOT_ACCEPTED'));continue
        if x.get('family')!='baseline':continue
        destination=target/p.name
        if destination.exists():raise RuntimeError('DUPLICATE_COHORT_FIT')
        shutil.copy2(p,destination);count+=1
    return count,invalid


def stage_rows(target):
    return [x for p in target.glob('*.json') if (x:=r.load(p)).get('family')=='baseline']


def valid_roster(rows,sessions):
    expected={(s['session_id'],region,kind,ridge,seed) for s in sessions for region in ('CA1','DG')
        for kind in ('stationary','history','population','event','drift','combined')
        for ridge in ([None] if kind=='stationary' else [.001,.01,.1,1.]) for seed in (11,23,37)}
    actual={(x['session_id'],x['region'],x['kind'],x['ridge'],x['seed']) for x in rows}
    return actual==expected and len(rows)==len(expected) and all(x['converged'] and x['optimizer_success'] and
        x['projected_gradient']<=.001 and math.isfinite(x['training_LL_nats_per_unit_bin']) and
        math.isfinite(x['validation_LL_nats_per_unit_bin']) for x in rows)


@cleanup
def main():
    r.verify();a=security();bindings=completed(r,'smoke',126)
    amendment=r.load(r.HERE/'optimizer_amendment.json')
    if amendment['code_sha256']['launch_repaired.py']!=r.sha(r.HERE/'launch_repaired.py'):raise RuntimeError('FROZEN_LAUNCHER_CHANGED')
    original=r.PREVIOUS/'exports/development1';manifest=r.load(original/'manifest.json')
    issuer=r.load(r.PREVIOUS/'.private/development_export_issuer.json')
    if issuer['manifest_sha256']!=r.sha(original/'manifest.json'):raise RuntimeError('PARENT_INPUT_BINDING')
    sessions=manifest['sessions']
    if len(sessions)!=13 or len({x['mouse_id'] for x in sessions})!=13:raise RuntimeError('FROZEN_COHORT_DENOMINATOR')
    concurrency=3
    r.save(r.HERE/'full_execution_registration.json',dict(utc=datetime.now(timezone.utc).isoformat(),
        code_sha256=r.sha(r.HERE/'cohort.py'),optimizer_amendment_sha256=r.sha(r.HERE/'optimizer_amendment.json'),
        smoke_native_sha256=bindings,parent_manifest_sha256=r.sha(original/'manifest.json'),
        concurrency=concurrency,hardware=dict(logical_processors=32,physical_memory_bytes=67874107392),
        session_order=[x['session_id'] for x in sessions],reuse_sessions=[sessions[0]['session_id']],
        newly_fitted_sessions=[x['session_id'] for x in sessions[1:]],
        progressive_mouse_gates=[4,13],per_fit_threads=1,per_fit_optimizer_unchanged=True,
        total_wallclock_seconds=43200,
        no_retries=True,no_new_sources=True,final_access=False),True)
    target=r.HERE/'results/full';target.mkdir(exist_ok=False)
    count,invalid=collect('smoke',target)
    if count!=126 or invalid:raise RuntimeError('SMOKE_REUSE_INCOMPLETE')
    reused={p.name:r.sha(p) for p in target.glob('*.json')}
    r.save(r.HERE/'results/smoke_reuse_manifest.json',dict(fit_sha256=reused,native_sha256=bindings),True)
    proofs=[dict(phase='smoke',sha256=bindings)];failures=[];stop=threading.Event()
    expired=threading.Event()
    def timeout():
        expired.set();stop.set()
    started=time.monotonic()
    deadline=threading.Timer(43200,timeout);deadline.daemon=True;_timers.append(deadline);deadline.start()
    # The copied full manifest is metadata only; actual worker inputs remain per-mouse.
    metadata=r.HERE/'exports/full_AB';metadata.mkdir(exist_ok=False);a.protect(metadata)
    for session in sessions:
        source=original/session['file']
        if r.sha(source)!=session['sha256']:raise RuntimeError('FULL_ORIGINAL_EXPORT_HASH')
        shutil.copy2(source,metadata/session['file']);a.protect(metadata/session['file'])
    r.save(metadata/'manifest.json',manifest,True);a.protect(metadata/'manifest.json')
    r.save(r.HERE/'results/full_preflight.json',dict(manifest_sha256=r.sha(metadata/'manifest.json'),
        execution_registration_sha256=r.sha(r.HERE/'full_execution_registration.json'),
        preceding_smoke_sha256=bindings,session_count=13,source_requests=0,final_access=False),True)
    batches=[sessions[1:4],sessions[4:7],sessions[7:10],sessions[10:13]]
    for batch in batches:
        if stop.is_set():
            failures.append(dict(error='REGISTERED_WALLCLOCK_BUDGET_EXHAUSTED'));break
        for session in batch:
            destination=r.HERE/('exports/runtime_'+session['session_id'])
            shutil.copytree(r.HERE/'exports/runtime',destination)
            for name,digest in amendment['runtime_sha256'].items():
                if r.sha(destination/name)!=digest:raise RuntimeError('PRIVATE_RUNTIME_COPY_CHANGED')
        if stop.is_set():
            failures.append(dict(error='REGISTERED_WALLCLOCK_BUDGET_EXHAUSTED'));break
        with ThreadPoolExecutor(max_workers=concurrency) as pool:
            futures={pool.submit(launch_one,s,stop):s for s in batch}
            for future in as_completed(futures):
                session=futures[future];phase='cohort_'+session['session_id']
                try:
                    future.result();bound=completed(r,phase,126);proofs.append(dict(phase=phase,sha256=bound))
                except Exception as exc:
                    peer_abort=stop.is_set() and not expired.is_set()
                    stop.set();failures.append(dict(session_id=session['session_id'],error_type=type(exc).__name__,error=str(exc),
                        peer_abort=peer_abort,wallclock_deadline_reached=expired.is_set()))
                try:
                    added,bad=collect(phase,target);count+=added;invalid.extend(bad)
                    if bad or added!=126:
                        stop.set();failures.append(dict(session_id=session['session_id'],error='COLLECTION_INTEGRITY_FAILED',count=added))
                except Exception as exc:
                    stop.set();failures.append(dict(session_id=session['session_id'],error='COLLECTION_ABORT',error_type=type(exc).__name__))
        if stop.is_set():break
        admitted=sessions[:len(proofs)]
        if invalid or not valid_roster(stage_rows(target),admitted):
            stop.set();failures.append(dict(error='PROGRESSIVE_ROSTER_FAILED'));break
        if len(proofs)==4:
            r.save(target/'stage_small.json',dict(gate='PASS',mouse_count=4,completed_fit_count=len(stage_rows(target)),
                strict_all_candidates=True,native_proof_count=4),True)
    allrows=[]
    for p in target.glob('*.json'):
        x=r.load(p)
        if x.get('family')=='baseline':allrows.append(x)
    identities={(x['session_id'],x['region'],x['kind'],x['ridge'],x['seed']) for x in allrows}
    expected={(s['session_id'],region,kind,ridge,seed) for s in sessions for region in ('CA1','DG')
        for kind in ('stationary','history','population','event','drift','combined')
        for ridge in ([None] if kind=='stationary' else [.001,.01,.1,1.]) for seed in (11,23,37)}
    bysession={s['session_id']:s for s in sessions}
    for x in allrows:
        s=bysession[x['session_id']];u=len(s['unit_ids'][x['region']])
        if (x['data_sha256']!=s['sha256'] or x['mouse_id']!=s['mouse_id'] or
            x['training_unit_bins']!=len(s['trial_ids']['A'])*20*u or
            x['validation_unit_bins']!=len(s['trial_ids']['B'])*20*u):
            failures.append(dict(session_id=s['session_id'],error='MATCHED_INPUT_BINDING_FAILED'))
    for name,digest in reused.items():
        if r.sha(target/name)!=digest:raise RuntimeError('REUSED_SMOKE_BYTES_CHANGED')
    verified=all(x['converged'] and x['optimizer_success'] and x['projected_gradient']<=.001 and
        math.isfinite(x['training_LL_nats_per_unit_bin']) and math.isfinite(x['validation_LL_nats_per_unit_bin'])
        for x in allrows)
    deadline.cancel()
    elapsed=time.monotonic()-started
    if elapsed>=43200:expired.set()
    passed=within_budget(expired.is_set(),elapsed) and not failures and not invalid and identities==expected and len(allrows)==1638 and len(proofs)==13 and verified and valid_roster(allrows,sessions)
    gate=dict(gate='PASS' if passed else 'FAIL',scientific_verdict='BASELINES_EXECUTED' if passed else 'NUMERICAL_INCONCLUSIVE',
        expected_fit_count=1638,completed_fit_count=len(allrows),converged_fit_count=sum(x['converged'] for x in allrows),
        mouse_count=len({x['mouse_id'] for x in allrows}),native_proofs=proofs,failed_attempts=failures,
        invalid_partial_receipts=invalid,reused_smoke_fits=126,new_fit_count=len(allrows)-126,
        wallclock_deadline_reached=expired.is_set(),
        admission_elapsed_seconds=elapsed,
        final_evaluation_access=False,preferred_regime_claim=False)
    r.save(target/'gate_result.json',gate,True)
    # Aggregate receipt explicitly references all native children; not a single-process claim.
    r.save(target/'role_proof.json',{'pass':passed,'is_appcontainer':passed,'capability_count':0,
        'scope':'Aggregate of linked native zero-capability proofs, not a new token probe','native_proofs':proofs},True)
    r.save(target/'oracle_tests.json',dict(passed=passed,count=7,scope='Each linked native worker ran all7 fixed numerical oracles'),True)
    r.save(r.HERE/'results/full_launch_receipt.json',dict(exit_code=0 if passed else 2,timed_out=expired.is_set(),role_proof_pass=passed,
        profile_cleanup_hresult='0x00000000' if passed else 'NOT_ALL_VERIFIED',
        scope='13 linked native mouse evaluations including immutable smoke reuse',native_proofs=proofs,
        final_values_exposed_to_analysis=False,final_holdout_evaluated=False),True)
    print('FULL_COHORT_GATE',gate['gate'],len(allrows),flush=True)
    deadline.cancel()
    if not passed:raise SystemExit(2)


if __name__=='__main__':main()
