"""Native isolated controller verifier; synthetic integration, never real D."""
import json
from pathlib import Path
import sys

def main():
    deps,data,output,source,key,pid,sddl=sys.argv[1:8];sys.path[:0]=[deps,str(Path(__file__).parent)]
    from release_control import Controller,package_sid
    data=Path(data);out=Path(output)
    if len(sys.argv)>8:
        point,name=sys.argv[8:];fixture=data/name
        def crash(stage):
            if stage==point:__import__('os')._exit(73)
        Controller(fixture/'ledger',fixture/'anchor.json',data/'binding').consume(fixture/'approval.json',crash)
        raise RuntimeError('CRASH_POINT_NOT_REACHED')
    def save(name,value):
        with (out/(name+'.json')).open('x') as f:json.dump(value,f,indent=2)
    from native_analysis_check import check
    proof=check(source,key,pid,sddl);save('role_proof',proof)
    if not proof['pass']:raise PermissionError('ACTUAL_CONTROLLER_ROLE')
    probes=json.loads((data/'probes.json').read_text());denials={}
    for name,path in probes.items():
        try:
            with open(path,'rb') as f:f.read(1)
            denials[name]=False
        except PermissionError:denials[name]=True
    save('issuer_source_key_denials',denials)
    if not all(denials.values()):raise PermissionError('CONTROLLER_ISSUER_OR_SOURCE_ACCESS')
    from access_check import denied_open
    checks={name:denied_open(path) for name,path in probes.items()};save('no_read_open_denials',checks)
    if not all(checks.values()):raise PermissionError('NATIVE_NO_READ_ACCESS_CHECK')
    import unittest
    import test_controller as tests
    tests.DATA=data;tests.OUT=out;tests.ARGS=[deps,str(data),str(out),source,key,pid,sddl];tests.WORKER=str(Path(__file__).resolve())
    result=unittest.TestResult();unittest.defaultTestLoader.loadTestsFromModule(tests).run(result)
    save('oracle_tests',{'count':result.testsRun,'passed':result.wasSuccessful(),'skipped':len(result.skipped),'errors':[str(x) for x in result.errors],'failures':[str(x) for x in result.failures]})
    if not result.wasSuccessful() or result.skipped:raise RuntimeError('CONTROLLER_INTEGRATION_GATE')
    receipt=Controller(data/'success/ledger',data/'success/anchor.json',data/'binding').consume(data/'success/approval.json')
    save('consumed_synthetic_receipt',receipt)
    save('gate_result',{'gate':'PASS','actual_controller_sid':package_sid(),'synthetic_only':True,'synthetic_capability_pending_broker':True,
        'D_RELEASE_CONSUMED':False,'D_EVALUATION_EXECUTED':False,'tests':result.testsRun})
if __name__=='__main__':main()
