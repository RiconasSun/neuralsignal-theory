"""Registered host activation; no issuer. Pending REAL authority stops before resume.

Processes are prepared suspended so the owner can bind an exact live identity in
a future separate authorization. This mission exercises only SYNTHETIC_D.
"""
from pathlib import Path
from .common import *
from .production_broker import preflight,deliver,RegisteredDeployment

def activate_registered(path,pinned_sha256,target,controller,verify_target,protect,grant):
    deployment=RegisteredDeployment(path,pinned_sha256)
    body,anchor=preflight(deployment,verify_target)
    if target.pi.pid!=body['principal']['pid'] or target.package!=body['principal']['package_sid'] or controller.package!=anchor['controller_sid']:raise PermissionError('PREPARED_PRODUCTION_ROLE_IDENTITY')
    binding=Path(deployment['binding_root']);identity=read_json(binding/'code_identity.json')
    check_hashes(controller.code,identity['controller_code_sha256'])
    if str(target.code)!=deployment['target_code_root'] or str(target.runtime)!=deployment['runtime_root'] or target.runtime!=controller.runtime:raise PermissionError('PREPARED_CODE_RUNTIME_PATH')
    plan=read_json(controller.data/'production_plan.json')
    if plan!={k:deployment[k] for k in ('ledger','anchor_path','binding_root','approval_path')}:raise PermissionError('PREPARED_CONTROLLER_INPUTS')
    config=read_json(target.data/'target_config.json')
    if any(config[k]!=deployment[k] for k in ('anchor_path','binding_root','approval_path','delivery_root')) or str(target.data)!=deployment['target_data_root']:raise PermissionError('PREPARED_TARGET_INPUTS')
    import time
    target.realm=body['realm'];controller.realm=body['realm'];target.resume()
    end=time.monotonic()+300
    while not (target.output/'ready.json').exists():
        if target.poll() is not None or time.monotonic()>end:raise RuntimeError('TARGET_PRECONSUMPTION_READ_PROOF_REQUIRED')
        time.sleep(.1)
    ready=read_json(target.output/'ready.json')
    if ready['pid']!=body['principal']['pid'] or not ready['readonly_binding_and_approval_readable']:raise PermissionError('TARGET_PRECONSUMPTION_PROOF_IDENTITY')
    preflight(deployment,verify_target)
    new(controller.data/'activation_start.json',{'binding':digest(canonical(body)),'authorization_id':body['authorization_id'],'realm':body['realm']});controller.resume()
    if controller.wait()!=0:raise RuntimeError('PRODUCTION_CONSUMPTION_STOP_NO_RETRY')
    receipt=read_json(controller.output/'consumed_success.json');completion=deliver(deployment,receipt,verify_target,protect,grant)
    if target.wait()!=0:raise RuntimeError('PRODUCTION_ASSESSMENT_INTERRUPTED_NO_RETRY')
    return completion,read_json(target.output/'gate_result.json')
