"""Metadata-only gate assembly after complete independent saved-state acceptance."""
import datetime,importlib.metadata,platform,sys
from pathlib import Path
from .core import *

def run():
    guard(load(P/'PHASE_A_CLAIM.json'));verify_pins()
    primary=load(P/'PRIMARY_AUDIT_V2_RESULT.json')
    independent=load(E/'INDEPENDENT_R5_REUSE_RESULT.json')
    review=load(E/'INDEPENDENT_R5_REUSE_MATRIX_ACCEPTANCE.json')
    if (primary['optimizer_passed'],primary['B0_passed'])!=(3992,216) or not independent['independent_qualification_complete'] or (independent['optimizer_states_qualified'],independent['B0_certificates_qualified'])!=(3992,216):raise AccessStop('Complete primary and independent audits required')
    if review['decision']!='ACCEPTED_COMPLETE_3992_216_REUSE_MATRIX' or review['open_P0'] or review['open_P1']:raise AccessStop('Independent exact matrix acceptance required')
    for name,key in [('PRIMARY_OPTIMIZER_V2_MATRIX.json','primary_optimizer_matrix_sha256'),('PRIMARY_B0_V2_MATRIX.json','primary_B0_matrix_sha256')]:
        if sha(P/name)!=review[key]:raise AccessStop('Reviewed primary matrix changed')
    if sha(E/'INDEPENDENT_R5_REUSE_RESULT.json')!=review['independent_result_sha256'] or sha(R/review['review_path'])!=review['review_sha256']:raise AccessStop('Independent review binding')
    certification=load(P/'CERTIFICATION_3_ACCEPTANCE.json')
    if not certification['mandatory_tests_pass'] or certification['real_fits_executed']!=0:raise AccessStop('Production synthetic certification required')
    result=load(R/certification['test_result_path'])
    for row in result['source_files']:
        if sha(R/row['path'])!=row['sha256']:raise AccessStop('Certified source changed')
    runtime=load(R/'paper16_development_r4/RUNTIME_IDENTITY.json')
    if Path(sys.executable).resolve()!= (R/runtime['runtime_executable']).resolve() or sha(sys.executable)!=runtime['python_launcher_sha256']:raise AccessStop('Actual registered Python launcher required')
    versions={'Python':platform.python_version(),**{name:importlib.metadata.version(name) for name in ['numpy','scipy','h5py','requests']}}
    if versions!=runtime['versions']:raise AccessStop('Actual numeric runtime version mismatch')
    for path,digest in runtime['files'].items():
        if sha(R/path)!=digest:raise AccessStop('Numeric runtime binary changed')
    once(P/'PRODUCTION_CERTIFICATION_FINAL.json',certification)
    once(P/'REUSE_ADMISSION.json',{'mission':MISSION,'required_gate_pass':True,'optimizer_states_admitted':3992,'B0_certificates_admitted':216,'R3':952,'R4':3040,'primary_result_sha256':sha(P/'PRIMARY_AUDIT_V2_RESULT.json'),'independent_result_sha256':sha(E/'INDEPENDENT_R5_REUSE_RESULT.json'),'independent_matrix_acceptance_sha256':sha(E/'INDEPENDENT_R5_REUSE_MATRIX_ACCEPTANCE.json'),'historical_ftol_origins_preserved':True,'phase_A_claim_sha256':sha(P/'PHASE_A_CLAIM.json'),'new_evaluations':0,'not_yet_production_admission':True})
    once(P/'RUNTIME_IDENTITY.json',{'runtime_executable':runtime['runtime_executable'],'python_launcher_sha256':sha(sys.executable),'versions':versions,'files':runtime['files'],'synthetic_command':'paper16_m1/work/runtime/Scripts/python.exe -B -m paper16_development_r5.certify supervise','scientific_command':'paper16_m1/work/runtime/Scripts/python.exe -B -m paper16_development_r5.controller supervise'})
    paths=set(P.glob('*.py'))|set(P.glob('*.json'))
    paths.update(Q/name for name in ['PROSPECTIVE_MISSION.md','PROPOSED_EXECUTION_POLICY.json','REUSE_TARGETS.json','RECOVERY_TASK_PLAN.json','ROSTER_IDENTITIES.json','SOURCE_PINS.json'])
    paths.update(E/name for name in ['OWNER_REQUEST.txt','REQUIREMENT_BASELINE.json','goldenstandards.md','INDEPENDENT_R5_REUSE_RESULT.json','INDEPENDENT_R5_REUSE_MATRIX_ACCEPTANCE.json'])
    paths.add(R/review['review_path'])
    paths.update(R/row['path'] for row in result['source_files'])
    paths.update(R/path for path in runtime['files']);paths.add(R/runtime['runtime_executable'])
    paths.update(R/path for path in [certification['registration_path'],certification['test_result_path']])
    for root in [R/'paper16_development_r3',R/'paper16_development_r4']:
        paths.update(root/name for name in ['SOURCE_PINS.json','PREFIT_FREEZE_MANIFEST.json','PROTECTED_STATE_MANIFEST.json'])
    paths.add(R/'paper16_development_r4/PROTECTED_STATE_MANIFEST_SUPPLEMENT_1.json')
    guard(load(P/'PHASE_A_CLAIM.json'))
    once(P/'PREFIT_FREEZE_MANIFEST.json',{'mission':MISSION,'frozen_UTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'phase_A_claim_sha256':sha(P/'PHASE_A_CLAIM.json'),'before_new_real_fits':True,'E_authorized':False,'files':[{'path':f.relative_to(R).as_posix(),'sha256':sha(f)} for f in sorted(paths)]})
    print('Complete metadata gate assembled; independent exact-production acceptance still required.',flush=True)

if __name__=='__main__':
    run()
