"""Source-only R4 phases; no model/optimizer/B/E-scoring/Final execution path."""
import datetime
import json
import os
import sys
import time
import h5py
from .core import (R,P,E,S,load,sha,once,registration,verify_history,verify_saved_A,source_inputs,
    save_arrays,select_common,validate_item,SourceStop,ResourceStop,CommonSupportStop,
    guard,make_stage,verify_stage_environment,require_job,supervise_child,private_file)
from .transport import Journal,Transport,RangeReader
from .neural_reader import read_a_source

MISSION='P16-M2-BOUNDED-NEURAL-SOURCE-RECOVERY-R4'


def phase_name(phase):
    if phase not in ['fourth','remaining']:raise SourceStop('Unknown R4 phase denied before any source claim')
    return phase


def verify_preaccess():
    a=load(E/'PREACCESS_APPROVAL.json')
    if a.get('decision')!='ACCEPTED_R4_SOURCE_ONLY_PREACCESS' or any(type(a.get(k)) is not int or a[k]!=0 for k in ['open_P0','open_P1']):
        raise SourceStop('Exact independent R4 preaccess acceptance required')
    if sha(E/'PREACCESS_REVIEW.md')!=a['report_sha256']:raise SourceStop('R4 independent report identity mismatch')
    manifest=load(P/'PREACCESS_FREEZE_MANIFEST.json')
    if sha(P/'PREACCESS_FREEZE_MANIFEST.json')!=a['manifest_sha256']:raise SourceStop('R4 preaccess freeze mismatch')
    required={r['path'] for r in manifest['files']}|{'paper16_source_r4/PREACCESS_FREEZE_MANIFEST.json'}
    if not required<=set(a['reviewed_hashes']):raise SourceStop('Incomplete independently reviewed R4 payload set')
    for name,digest in a['reviewed_hashes'].items():
        path=(R/name).resolve();path.relative_to(R)
        if sha(path)!=digest:raise SourceStop('Reviewed R4 source/evidence changed: '+name)
    for row in manifest['files']:
        if (R/row['path']).stat().st_size!=row['bytes'] or sha(R/row['path'])!=row['sha256']:raise SourceStop('R4 frozen source identity')
    verify_history()
    return registration()


def fourth_approval():
    a=load(E/'FOURTH_SOURCE_APPROVAL.json')
    if a.get('decision')!='ACCEPTED_R4_COMPLETE_FOURTH_SOURCE' or any(type(a.get(k)) is not int or a[k]!=0 for k in ['open_P0','open_P1']):
        raise SourceStop('Independent complete fourth-source acceptance required before other24')
    if sha(E/'FOURTH_SOURCE_REVIEW.md')!=a['report_sha256']:raise SourceStop('Fourth review report identity')
    required={'paper16_source_r4/results/'+n for n in ['STAGE_CLAIM.json','WORKER_fourth.json','SUPERVISION_fourth.json','BUDGET_FOURTH.jsonl','RECOVERED_RANGE.json']}
    required|={'paper16_source_r4/results/sources/763673393/'+n for n in ['ATTEMPT.json','RESULT.json','UNIT_QC.jsonl','VALUE_READS.json','NATIVE_LINK_AUDIT.json']}
    if not required<=set(a['reviewed_hashes']):raise SourceStop('Incomplete fourth-source reviewed artifacts')
    for name,digest in a['reviewed_hashes'].items():
        path=(R/name).resolve();path.relative_to(R)
        if sha(path)!=digest:raise SourceStop('Fourth source reviewed evidence changed')
    if not load(P/'results/SUPERVISION_fourth.json')['valid_completed_worker']:raise SourceStop('Fourth worker did not complete')
    if not load(P/'results/sources/763673393/RESULT.json')['source_pass']:raise SourceStop('Fourth source did not pass integrity')
    if not (P/'results/TRANSPORT.jsonl').read_bytes().startswith((P/'results/BUDGET_FOURTH.jsonl').read_bytes()):raise SourceStop('Fourth journal prefix changed')


def process_source(item,reg,stage,journal,fourth=False):
    validate_item(item,reg);guard(stage)
    folder=P/'results/sources'/str(item['session_id']);folder.mkdir(parents=True,exist_ok=True)
    once(folder/'ATTEMPT.json',{'mission':MISSION,'source':item,'phase':'fourth' if fourth else 'remaining',
        'time_UTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'registration_sha256':sha(P/'ACCESS_REGISTRATION.json'),
        'preaccess_approval_sha256':sha(E/'PREACCESS_APPROVAL.json'),'R3_new_attempt_reclassification':False})
    audit,reads=[],[];new_captures=[];reused=[];metrics=None;t=None
    try:
        header,flashes,running,pins=source_inputs(item)
        raw=b''
        if fourth:raw,reused=verify_saved_A(item,reg['recovery']['historical_completed_candidates'])
        private_file(folder/'UNIT_QC.jsonl',raw)
        metrics=(folder/'UNIT_QC.jsonl').open('a',encoding='utf8',newline='\n')
        once(folder/'REUSED_A_PREFIX.json',{'count':len(reused),'original_R3_QC_sha256':sha(S/'results/sources/763673393/UNIT_QC.jsonl') if fourth else None,
            'exact_prefix_bytes':len(raw),'new_neural_payload_reads_for_reused_units':0})
        candidates={(int(x['session_id']),int(x['unit_id'])):x for x in load(S/'SOURCE_CANDIDATE_CERTIFICATES.json')['candidates']}
        def persist(uid,arrays,record):
            guard(stage);path=P/'work/private/A'/str(item['session_id'])/(str(uid)+'.npz');path.parent.mkdir(parents=True,exist_ok=True)
            result={'private_path':path.relative_to(R).as_posix(),**save_arrays(path,arrays)}
            once(folder/f'A_CAPTURE_{uid}.json',{'unit_id':uid,'A_only':True,**result})
            new_captures.append(result);row={**record,'private_A_capture':result}
            metrics.write(json.dumps(row,allow_nan=False)+'\n');metrics.flush();os.fsync(metrics.fileno())
            return result
        t=Transport(item,reg,stage,journal)
        if fourth:
            once(P/'results/NON_NEURAL_PREFLIGHT.json',{'source':item,'HEAD':t.head(),'body_bytes':0})
            recovery=t.recover_historical();once(P/'results/RECOVERED_RANGE.json',recovery)
        guard(stage)
        with RangeReader(t) as reader:
            with h5py.File(reader,'r') as file:
                result=read_a_source(file,item,reg,header,flashes,candidates,persist,audit,reads,reused_records=reused)
        guard(stage);selection=select_common(result['units'],flashes['color'],running['missing'],reg);guard(stage)
        once(folder/'VALUE_READS.json',reads);once(folder/'NATIVE_LINK_AUDIT.json',audit)
        final={'mission':MISSION,'source':item,'source_pass':True,'A_QC_complete':True,'candidate_units_examined_total':len(result['units']),
            'historical_R3_candidate_states_reused':len(reused),'new_R4_candidate_states':len(new_captures),'selection':selection,
            'native_objects':result['native_objects'],'probe_metadata':result['probe_metadata'],'source_metadata_pins':pins,
            'UNIT_QC_sha256':sha(folder/'UNIT_QC.jsonl'),'A_only_export':True,'B_E_arrays_exported':False,
            'Final_C_access':False,'Final_D_access':False,'model_fits':0,'running_acquisition_calls':0}
        once(folder/'RESULT.json',final)
        print(json.dumps({'session':item['session_id'],'source_pass':True,'admitted':selection['admitted'],
                          'new_A_states':len(new_captures),'R3_A_reused':len(reused)}),flush=True)
        return final
    except BaseException as exc:
        for name,value in [('VALUE_READS.json',reads),('NATIVE_LINK_AUDIT.json',audit)]:
            if not (folder/name).exists():once(folder/name,value)
        verdict='RESOURCE_LIMIT' if isinstance(exc,ResourceStop) else 'SCIENTIFIC_PROTOCOL_INCONCLUSIVE' if isinstance(exc,CommonSupportStop) else 'STOP_SOURCE'
        once(folder/'FAILURE.json',{'verdict':verdict,'error_type':type(exc).__name__,'message':str(exc),
             'historical_A_prefix_reused':len(reused),'new_A_captures_preserved':len(new_captures),
             'no_later_source_or_fit_authorized':True,'attempt_has_ended_no_phase_restart':True})
        raise
    finally:
        if metrics is not None:metrics.close()
        if t is not None:t.close()


def cohort():
    reg=registration();results=[]
    for i,item in enumerate(reg['objects']):
        folder=(S if i<3 else P)/'results/sources'/str(item['session_id'])
        result=load(folder/'RESULT.json')
        if not result['source_pass'] or not result['A_QC_complete']:raise SourceStop('Incomplete original source cannot receive terminal/cohort credit')
        results.append(result)
    admitted=[x for x in results if x['selection']['admitted']]
    bo=sum(x['source']['protocol']=='brain_observatory_1.1' for x in admitted);fc=len(admitted)-bo
    passed=len(admitted)>=14 and bo>=3 and fc>=10
    decision={'mission':MISSION,'verdict':'M2_SOURCE_AND_PHYSIOLOGY_PASS' if passed else 'DATA_INSUFFICIENT',
        'sources_completed':28,'R3_complete_sources_reused':3,'new_R4_complete_sources':25,
        'admitted_mice':len(admitted),'admitted_BO':bo,'admitted_FC':fc,'A_only_physiology_pass':passed,
        'source_only_M3_readiness':passed,'model_fits_authorized':False,'model_fits':0,'B_E_neural_scientific_access':False,
        'Final_C_access':False,'Final_D_access':False,
        'sources':[{'source':x['source'],'selection':x['selection']} for x in results]}
    once(P/'results/M2_DECISION.json',decision);return decision


def worker(phase):
    phase_name(phase);reg=verify_preaccess();stage=load(P/'results/STAGE_CLAIM.json');verify_stage_environment(stage)
    supervisor=load(P/'results'/f'SUPERVISOR_{phase}.claim.json');require_job(supervisor['job_name'])
    once(P/'results'/f'WORKER_{phase}.claim.json',{'worker_pid':os.getpid(),'parent_pid':os.getppid(),'job_name':supervisor['job_name'],'phase':phase})
    if phase=='remaining':fourth_approval()
    journal=Journal(P/'results/TRANSPORT.jsonl',reg,append=phase=='remaining')
    try:
        objects=reg['objects'][3:4] if phase=='fourth' else reg['objects'][4:]
        for item in objects:process_source(item,reg,stage,journal,fourth=phase=='fourth')
        guard(stage)
        decision=cohort() if phase=='remaining' else None
        once(P/'results'/f'WORKER_{phase}.json',{'phase':phase,'completed_sources':len(objects),'all_sources_integrity_pass':True,
            'new_payload_cumulative':journal.payload,'reserved_cumulative':journal.reserved,
            'timeout_recovery_slots_cumulative':journal.recovery_slots,'per_source':journal.by_source,'decision':None if decision is None else decision['verdict'],
            'deadline_monotonic':stage['deadline_monotonic'],'elapsed_seconds':time.monotonic()-stage['start_monotonic'],'model_fits':0})
    finally:journal.close()


def supervise(phase):
    phase_name(phase);reg=verify_preaccess()
    if phase=='fourth':
        once(P/'results/STAGE_CLAIM.json',{'mission':MISSION,**make_stage(reg['resources']['development_wall_seconds_max']),
            'registration_sha256':sha(P/'ACCESS_REGISTRATION.json'),'R3_stage_reset':False,'new_R4_authorized_clock':True})
    else:fourth_approval()
    stage=load(P/'results/STAGE_CLAIM.json');verify_stage_environment(stage)
    job=f'Local\\P16_R4_{phase}_{os.getpid()}_{time.time_ns()}'
    once(P/'results'/f'SUPERVISOR_{phase}.claim.json',{'phase':phase,'supervisor_pid':os.getpid(),'job_name':job,'original_R4_deadline_monotonic':stage['deadline_monotonic']})
    outcome=supervise_child([sys.executable,'-m','paper16_source_r4.run_sources','worker',phase],
        stage['deadline_monotonic'],E/f'EXECUTION_{phase.upper()}.log',job,stage)
    outcome.update({'phase':phase,'valid_completed_worker':bool(outcome['returncode']==0 and not outcome['killed_at_deadline']
        and outcome['completed_before_deadline'] and (P/'results'/f'WORKER_{phase}.json').exists()),'log_sha256':sha(E/f'EXECUTION_{phase.upper()}.log')})
    once(P/'results'/f'SUPERVISION_{phase}.json',outcome)
    if phase=='fourth':
        path=P/'results/TRANSPORT.jsonl';private_file(P/'results/BUDGET_FOURTH.jsonl',path.read_bytes() if path.exists() else b'')
    if not outcome['valid_completed_worker']:raise SourceStop('Required R4 source phase ended; no later source or phase restart')
    print(json.dumps(outcome),flush=True)


if __name__=='__main__':
    if len(sys.argv)!=3 or sys.argv[1] not in ['supervise','worker']:raise SourceStop('Only exact registered R4 source commands')
    phase_name(sys.argv[2]);{'supervise':supervise,'worker':worker}[sys.argv[1]](sys.argv[2])
