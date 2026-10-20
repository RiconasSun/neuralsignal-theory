"""One fresh A diagnostic or synthetic suite; no evaluation/selection entry point."""
import os,sys
from .common import *

def run(mode):
    require(mode in ['synthetic','real'],'Mode');folder=Path(os.environ['P16_TF1_FOLDER']);stage=load(folder/'STAGE.json')
    require_job(os.environ['P16_TF1_JOB']);verify_stage_environment(stage);guard(stage);verify_code()
    if mode=='synthetic':
        from .tests import run as tests
        tests(folder);return
    verify_prefit();claim=load(P/'REAL_CLAIM.json');require(claim['stage']==stage and claim['no_retry'],'One original stage claim')
    from . import access,broker
    access.install_guard()
    try:
        objective=access.load_A(folder,stage)
        task={'id':load(P/'INPUT_IDENTITY.json')['new_task_id'],'mouse_id':'733457989','panel':'S02','model':'C','unit_id':951800892,'lambda':1.0,'new_mission':MISSION}
        result=broker.fit(objective,folder/'fit',stage,task)[1]
        guard(stage);require(result['success'] and result['message'].startswith('CONVERGENCE:'),'Correct numerical termination required')
        once(folder/'WORKER_COMPLETE.json',{'numerical_pass':True,'real_A_attempts':1,'B_E_scientific_access':False,'Final_C_access':False,'Final_D_access':False})
    except BaseException as exc:
        once(folder/'STOP.json',{'type':type(exc).__name__,'message':str(exc),'no_retry':True,'stage_unchanged':True});raise

if __name__=='__main__':run(sys.argv[1])
