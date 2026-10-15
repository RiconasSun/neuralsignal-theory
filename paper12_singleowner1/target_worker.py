"""Actual scientific evaluator process: no keys, issuer or ledger capability."""
import json
from pathlib import Path
import sys
import time

def main():
    deps,data,output,source,key,pid,sddl=sys.argv[1:];code=Path(__file__).parent
    sys.path.insert(0,str(code))
    from worker_bootstrap import bootstrap,runtime_check
    boot=bootstrap(deps,code);data=Path(data);out=Path(output)
    from common import new,read_json,sha,verify_approval
    from native_analysis_check import check
    proof=check(source,key,pid,sddl);new(out/'role_proof.json',proof)
    if not proof['pass']:raise PermissionError('PRODUCTION_EVALUATOR_ACTUAL_ROLE')
    runtime=runtime_check(data,deps);config=read_json(data/'target_config.json')
    from access_check import denied_open
    denials={name:denied_open(path) for name,path in config['protected_probes'].items()};new(out/'pregrant_denials.json',denials)
    if not all(denials.values()):raise PermissionError('TARGET_PROTECTED_SOURCE_KEY_ISSUER_LEDGER_ACCESS')
    # Actual target read proof before any consumption or capability signal.
    read_json(Path(config['binding_root'])/'C_state_manifest.json');read_json(config['anchor_path']);read_json(config['approval_path'])
    new(out/'ready.json',dict(boot,runtime=runtime,pid=__import__('os').getpid(),readonly_binding_and_approval_readable=True))
    end=time.monotonic()+43200
    while not (data/'start_evaluation.json').exists():
        if (data/'stop.json').exists():return
        if time.monotonic()>end:raise TimeoutError('NO_AUTHORIZED_CAPABILITY')
        time.sleep(.1)
    start=read_json(data/'start_evaluation.json');approval=read_json(config['approval_path']);anchor=read_json(config['anchor_path']);body=verify_approval(approval,anchor,config['binding_root'])
    from release_control import package_sid
    if body['principal']['pid']!=__import__('os').getpid() or body['principal']['package_sid']!=package_sid() or start['principal']!=body['principal'] or start['binding']!=__import__('hashlib').sha256(__import__('common').canonical(body)).hexdigest():raise PermissionError('TARGET_SIGNATURE_PRINCIPAL_BINDING')
    delivery=Path(config['delivery_root'])
    if sha(delivery/'delivery_manifest.json')!=start['delivery_manifest_sha256']:raise PermissionError('TARGET_CAPABILITY_MANIFEST_HASH')
    post={name:denied_open(path) for name,path in config['protected_probes'].items()};new(out/'postgrant_denials.json',post)
    if not all(post.values()):raise PermissionError('POSTGRANT_PROTECTED_ACCESS')
    new(out/'assessment_started.json',{'realm':body['realm'],'authorization_id':body['authorization_id'],'D_EVALUATION_EXECUTED':body['realm']=='REAL_D','one_shot_no_retry':True})
    from scientific_evaluator import evaluate
    result=evaluate(config['binding_root'],delivery,out,start['expected'])
    new(out/'gate_result.json',dict(result,role_proof=True,pregrant_denials=True,postgrant_denials=True,code_bootstrap=boot,runtime=runtime))

if __name__=='__main__':
    try:main()
    except BaseException as exc:
        try:
            from common import new
            started=Path(sys.argv[3])/'assessment_started.json'
            new(Path(sys.argv[3])/'failure.json',{'type':type(exc).__name__,'message':str(exc),'traceback':__import__('traceback').format_exc(),'assessment_started':started.exists(),'realm':__import__('json').loads(started.read_text())['realm'] if started.exists() else 'UNRELEASED'})
        finally:raise
