"""Unchanged ledger controller + native negative tests, synthetic rehearsal only."""
from pathlib import Path
import sys

def main():
    deps,data,output,source,key,pid,sddl=sys.argv[1:8];code=Path(__file__).parent;sys.path.insert(0,str(code))
    from worker_bootstrap import bootstrap,runtime_check
    bootstrap(deps,code)
    from release_control import Controller,read_json
    data=Path(data);out=Path(output)
    if len(sys.argv)>8:
        point,name=sys.argv[8:]
        def crash(stage):
            if stage==point:__import__('os')._exit(73)
        Controller(data/name/'ledger',data/name/'anchor.json',data/'binding').consume(data/name/'approval.json',crash)
        raise RuntimeError('REGISTERED_CRASH_POINT_NOT_REACHED')
    from common import new
    from native_analysis_check import check
    proof=check(source,key,pid,sddl);new(out/'role_proof.json',proof)
    if not proof['pass']:raise PermissionError('PRODUCTION_CONTROLLER_ACTUAL_ROLE')
    runtime=runtime_check(data,deps)
    from access_check import denied_open
    probes=read_json(data/'controller_probes.json');denials={name:denied_open(path) for name,path in probes.items()};new(out/'protected_denials.json',denials)
    if not all(denials.values()):raise PermissionError('CONTROLLER_SOURCE_KEY_ISSUER_ACCESS')
    if not (data/'synthetic_oracles.json').exists():
        consume_production(data,out,runtime)
        return
    if read_json(data/'synthetic_oracles.json')!={'realm':'SYNTHETIC_D'} or read_json(data/'success/anchor.json')['realm']!='SYNTHETIC_D':raise PermissionError('SYNTHETIC_ORACLES_REALM')
    import unittest,test_controller as tests
    tests.DATA=data;tests.OUT=out;tests.ARGS=[deps,str(data),str(out),source,key,pid,sddl];tests.WORKER=str(Path(__file__).resolve())
    result=unittest.TestResult();unittest.defaultTestLoader.loadTestsFromModule(tests).run(result)
    new(out/'oracle_tests.json',{'count':result.testsRun,'passed':result.wasSuccessful(),'skipped':len(result.skipped),'errors':[str(x) for x in result.errors],'failures':[str(x) for x in result.failures]})
    if not result.wasSuccessful() or result.skipped:raise RuntimeError('ACTUAL_CONTROLLER_ORACLES')
    # Extra signed production-failure fixtures consume only synthetic entitlements.
    extra=read_json(data/'extra_consumptions.json')
    for name in extra:
        receipt=Controller(data/name/'ledger',data/name/'anchor.json',data/'binding').consume(data/name/'approval.json');new(out/('consumed_'+name+'.json'),receipt)
    new(out/'oracles_done.json',{'passed':True,'controller_oracles':result.testsRun,'synthetic_extra_consumptions':len(extra)})
    consume_production(data,out,runtime)

def consume_production(data,out,runtime):
    from release_control import Controller,read_json,verify_approval,canonical,digest
    from common import new
    import time
    end=time.monotonic()+43200
    while not (data/'activation_start.json').exists():
        if time.monotonic()>end:raise TimeoutError('NO_VERIFIED_HOST_ACTIVATION')
        time.sleep(.1)
    plan=read_json(data/'production_plan.json');approval=read_json(plan['approval_path']);anchor=read_json(plan['anchor_path']);body=verify_approval(approval,anchor,plan['binding_root']);cue=read_json(data/'activation_start.json')
    if cue!={'binding':digest(canonical(body)),'authorization_id':body['authorization_id'],'realm':body['realm']}:raise PermissionError('HOST_ACTIVATION_CUE_BINDING')
    receipt=Controller(plan['ledger'],plan['anchor_path'],plan['binding_root']).consume(plan['approval_path'])
    new(out/'consumed_success.json',receipt);new(out/'gate_result.json',{'gate':'PASS','realm':receipt['realm'],'runtime':runtime,'consumption_completed':True,'production_plan_executed':True})

if __name__=='__main__':
    try:main()
    except BaseException as exc:
        try:
            from common import new
            new(Path(sys.argv[3])/'failure.json',{'type':type(exc).__name__,'message':str(exc),'traceback':__import__('traceback').format_exc(),'consumption_status':'Inspect durable ledger/fence; failure does not restore entitlement'})
        finally:raise
