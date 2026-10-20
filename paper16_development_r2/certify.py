"""Native externally bounded synthetic production suite, not scientific fitting."""
import importlib.metadata,os,platform,sys,time,unittest
from unittest.mock import patch
from .core import *
from paper16_dev_r3.run_m2 import supervise_child

def worker():
    require_job(os.environ['P16_R2_JOB']);stage=load(os.environ['P16_R2_TEST_STAGE']);verify_stage_environment(stage)
    candidate=load(Path(os.environ['P16_R2_TEST_STAGE']).parent/'CODE_HASHES.json')
    for name,digest in candidate.items():
        if sha(R/name)!=digest:raise ImplementationStop('Synthetic candidate changed before test import')
    runtime={'Python':platform.python_version(),**{k:importlib.metadata.version(k) for k in ['numpy','scipy','h5py','requests']}}
    if runtime!=NUMERIC['software']:raise ImplementationStop('Pinned runtime mismatch')
    suite=unittest.defaultTestLoader.loadTestsFromName('paper16_development_r2.test_production')
    # Reuse only independent, non-optimizer M1 state/enumeration oracles here.
    for name in ['test_nested_B4_at_zero_latent_offsets_and_logits','test_D_forward_enumeration_S_presentation_static_and_IID','test_continuous_history_strict_future_reset_and_parameter_counts']:
        suite.addTest(unittest.defaultTestLoader.loadTestsFromName('paper16_m1.code.test_dynamics.DynamicsTests.'+name))
    with patch('socket.socket.connect',side_effect=RuntimeError('M3 synthetic suite forbids source network')):
        result=unittest.TextTestRunner(verbosity=2).run(suite)
    report={'scope':'SYNTHETIC_PRODUCTION_ONLY','runtime':runtime,'tests_run':result.testsRun,'failures':len(result.failures),
        'errors':len(result.errors),'skipped':len(result.skipped),'mandatory_tests_pass':result.wasSuccessful() and not result.skipped,
        'real_fits_executed':0,'Final_C_access':False,'Final_D_access':False}
    report['candidate_source_hashes']=candidate
    report['candidate_unchanged_during_tests']=all(sha(R/name)==digest for name,digest in candidate.items())
    report['mandatory_tests_pass']=report['mandatory_tests_pass'] and report['candidate_unchanged_during_tests']
    once(Path(os.environ['P16_R2_TEST_STAGE']).parent/'RESULT.json',report)
    if not report['mandatory_tests_pass']:raise ImplementationStop('Required synthetic production certification failed')

def supervise():
    root=P/'work'/('M3_'+str(time.time_ns()));root.mkdir(parents=True,exist_ok=False)
    stage=make_stage(900);once(root/'STAGE.json',stage);name=f'Local\\P16_R2_M3_{os.getpid()}_{time.time_ns()}'
    once(root/'CODE_HASHES.json',{path.relative_to(R).as_posix():sha(path) for path in sorted(P.glob('*.py'))})
    os.environ['P16_R2_JOB']=name;os.environ['P16_R2_TEST_STAGE']=str(root/'STAGE.json')
    result=supervise_child([sys.executable,'-B','-m','paper16_development_r2.certify','worker'],stage['deadline_monotonic'],root/'TESTS.log',name,stage)
    once(root/'SUPERVISION.json',result)
    print(json.dumps({'synthetic_run':root.relative_to(R).as_posix(),'supervision':result}),flush=True)
    if result['returncode']!=0 or result['killed_at_deadline']:raise ImplementationStop('Synthetic suite failed; preserve run/no real fitting')

if __name__=='__main__':{'worker':worker,'supervise':supervise}[sys.argv[1]]()
