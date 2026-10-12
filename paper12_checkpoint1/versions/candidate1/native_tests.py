"""Registered synthetic-only Windows diagnostic/evaluation harness."""
import ctypes
import hashlib
import os
import platform
import subprocess
import sys
import threading
import time
import uuid
from pathlib import Path
import numpy as np
import pywintypes
import win32con
import win32file
import win32security as ws
import ntsecuritycon as rights
import study as r
from history_guard import verify as verify_history
from custody_security import prepare,protect,check_acl,require_custodian
from atomic_checkpoint import commit,read,writer_lock


def error(exc):
    return dict(error_type=type(exc).__name__,winerror=getattr(exc,'winerror',None) or (exc.args[0] if isinstance(exc,pywintypes.error) else None),
        error_code=str(exc) if isinstance(exc,(RuntimeError,ValueError)) else 'NATIVE_WINDOWS_ERROR',events=getattr(exc,'events',[]))


def fixtures(root,count,label):
    rng=np.random.default_rng(2026101201);rows=[]
    for index in range(count):
        trial=prepare(root/('trial_'+str(index)))
        body=rng.bytes(1024+(index%8)*1024);source=dict(dataset='synthetic',version=1,block=index)
        try:
            receipt=commit(trial,'block',body,source)
            same=commit(trial,'block',body,source)
            if not receipt['committed'] or not same['idempotent'] or read(trial/'block.checkpoint',source,hashlib.sha256(body).hexdigest())!=body:
                raise RuntimeError('NONINJECTED_COMMIT_MISMATCH')
            check_acl(trial/'block.checkpoint')
            rows.append(dict(context=label,index=index,passed=True,receipt=receipt,idempotent_resume=True,
                source_verified=True,ACL_verified=True,payload_bytes=len(body)))
        except Exception as exc:rows.append(dict(context=label,index=index,passed=False,**error(exc)))
    return rows


def original(root):
    rng=np.random.default_rng(2026101201);rows=[]
    for index in range(200):
        trial=prepare(root/('trial_'+str(index)));pending=prepare(trial/'pending')
        for name in ('body.blob','marker.json'):
            path=pending/name
            with path.open('xb') as stream:stream.write(rng.bytes(256));stream.flush();os.fsync(stream.fileno())
            protect(path)
        try:
            pending.rename(trial/'committed');rows.append(dict(index=index,rename_pass=True))
        except Exception as exc:rows.append(dict(index=index,rename_pass=False,**error(exc)))
    return rows


def injections(root):
    results=[]
    def case(name,work):
        trial=prepare(root/name)
        try:
            detail=work(trial);results.append(dict(name=name,test_pass=True,successful_commit_count=0,**(detail or {})))
        except Exception as exc:results.append(dict(name=name,test_pass=False,successful_commit_count=0,**error(exc)))
    body=b'synthetic-old';new=b'synthetic-new';source=dict(dataset='synthetic',version=1)
    digest=hashlib.sha256(body).hexdigest()
    def locked(trial):
        commit(trial,'block',body,source);target=trial/'block.checkpoint'
        previous=r.sha(target)
        handle=win32file.CreateFile(str(target),win32con.GENERIC_READ,win32con.FILE_SHARE_READ,None,win32con.OPEN_EXISTING,0,None)
        try:
            try:
                forbidden=win32file.CreateFile(str(target),rights.DELETE,7,None,win32con.OPEN_EXISTING,0,None)
            except pywintypes.error as exc:
                native_code=exc.winerror
                if native_code!=32:raise
            else:
                forbidden.Close();raise RuntimeError('INJECTED_ACL_DELETE_NOT_DENIED')
            try:commit(trial,'block',new,source,previous)
            except RuntimeError as exc:
                events=exc.events
                if len(events)!=3 or any(x['winerror'] not in (5,32,33) for x in events):raise
                if r.sha(target)!=previous:raise RuntimeError('LOCKED_TARGET_MODIFIED')
                return dict(expected_safe_stop=True,native_events=events,old_artifact_preserved=True,native_delete_sharing_winerror=native_code)
            raise RuntimeError('LOCKED_DESTINATION_UNEXPECTED_SUCCESS')
        finally:handle.Close()
    case('locked_destination',locked)
    def readonly(trial):
        commit(trial,'block',body,source);target=trial/'block.checkpoint'
        win32file.SetFileAttributes(str(target),win32con.FILE_ATTRIBUTE_READONLY)
        try:
            try:commit(trial,'block',new,source,r.sha(target))
            except RuntimeError as exc:
                if str(exc)!='READONLY_CHECKPOINT_FORBIDDEN':raise
                return dict(expected_safe_stop=True,error_code=str(exc))
            raise RuntimeError('READONLY_NOT_REJECTED')
        finally:win32file.SetFileAttributes(str(target),win32con.FILE_ATTRIBUTE_NORMAL)
    case('readonly_destination',readonly)
    def acl_denied(trial):
        commit(trial,'block',body,source);target=trial/'block.checkpoint';previous=r.sha(target)
        sd=ws.GetNamedSecurityInfo(str(target),ws.SE_FILE_OBJECT,ws.DACL_SECURITY_INFORMATION)
        original_acl=sd.GetSecurityDescriptorDacl()
        user=ws.GetTokenInformation(ws.OpenProcessToken(-1,rights.TOKEN_QUERY),ws.TokenUser)[0]
        acl=ws.ACL();acl.AddAccessDeniedAce(ws.ACL_REVISION,rights.DELETE,user)
        for index in range(original_acl.GetAceCount()):acl.AddAce(ws.ACL_REVISION,index+1,original_acl.GetAce(index))
        ws.SetNamedSecurityInfo(str(target),ws.SE_FILE_OBJECT,ws.DACL_SECURITY_INFORMATION|ws.PROTECTED_DACL_SECURITY_INFORMATION,None,None,acl,None)
        try:
            try:
                forbidden=win32file.CreateFile(str(target),rights.DELETE,7,None,win32con.OPEN_EXISTING,0,None)
            except pywintypes.error as exc:
                native_code=exc.winerror
                if native_code!=5:raise
            else:
                forbidden.Close();raise RuntimeError('INJECTED_ACL_DELETE_NOT_DENIED')
            try:commit(trial,'block',new,source,previous)
            except RuntimeError as exc:
                if str(exc)!='CUSTODY_DACL_MISMATCH':raise
                return dict(expected_safe_stop=True,error_code=str(exc),native_delete_request_winerror=native_code,permission_repair_attempted=False)
            raise RuntimeError('ACL_DENIAL_NOT_REJECTED')
        finally:ws.SetNamedSecurityInfo(str(target),ws.SE_FILE_OBJECT,ws.DACL_SECURITY_INFORMATION|ws.PROTECTED_DACL_SECURITY_INFORMATION,None,None,original_acl,None)
    case('separate_ACL_denial',acl_denied)
    def bounded_restart(trial):
        first=locked(trial)
        try:commit(trial,'block',new,source,r.sha(trial/'block.checkpoint'))
        except RuntimeError as exc:
            if str(exc)!='PRESERVED_ATOMIC_COMMIT_STOP':raise
            return dict(expected_safe_stop=True,original_events=first['native_events'],no_budget_reset_after_unlock=True)
        raise RuntimeError('RESTART_RESET_COMMIT_BUDGET')
    case('bounded_restart_after_unlock',bounded_restart)
    def child_locked(trial):
        pending=prepare(trial/'pending');path=pending/'child';path.write_bytes(body);protect(path)
        handle=win32file.CreateFile(str(path),win32con.GENERIC_READ,win32con.FILE_SHARE_READ,None,win32con.OPEN_EXISTING,0,None)
        try:
            try:pending.rename(trial/'committed')
            except OSError as exc:return dict(original_failure_mechanism_reproduced=True,winerror=exc.winerror,ACL_unchanged=True)
            raise RuntimeError('LOCKED_CHILD_RENAME_UNEXPECTED_SUCCESS')
        finally:handle.Close()
    case('original_locked_child_directory',child_locked)
    def concurrent_writer(trial):
        with writer_lock(trial,'block'):
            process=subprocess.run([sys.executable,str(Path(__file__).resolve()),'--contender',str(trial)],capture_output=True,text=True)
            import json
            result=json.loads(process.stdout)
            if process.returncode!=0 or result.get('winerror')!=33:raise RuntimeError('CONCURRENT_WRITER_NOT_FENCED')
            return dict(expected_safe_stop=True,winerror=33,separate_native_process=True)
    case('concurrent_writer',concurrent_writer)
    def readers(trial):
        commit(trial,'block',body,source);target=trial/'block.checkpoint';previous=r.sha(target)
        handle=win32file.CreateFile(str(target),win32con.GENERIC_READ,
            win32con.FILE_SHARE_READ|win32con.FILE_SHARE_WRITE|win32con.FILE_SHARE_DELETE,None,win32con.OPEN_EXISTING,0,None)
        try:
            old=win32file.ReadFile(handle,target.stat().st_size)[1]
            receipt=commit(trial,'block',new,source,previous)
            win32file.SetFilePointer(handle,0,0);snapshot=win32file.ReadFile(handle,len(old))[1]
            if snapshot!=old or read(target,source,hashlib.sha256(new).hexdigest())!=new:raise RuntimeError('READER_TORN_ARTIFACT')
            return dict(old_handle_snapshot_preserved=True,new_complete_artifact_visible=True,native_events=receipt['events'])
        finally:handle.Close()
    case('concurrent_shared_delete_reader',readers)
    def malformed(trial):
        target=trial/'block.checkpoint'
        target.write_bytes(b'partial');protect(target)
        try:commit(trial,'block',body,source)
        except ValueError:return dict(expected_safe_stop=True,partial_not_replaced=True)
        raise RuntimeError('PARTIAL_ACCEPTED')
    case('partial_checkpoint',malformed)
    def corruption(trial):
        commit(trial,'block',body,source);target=trial/'block.checkpoint'
        value=target.read_bytes();target.write_bytes(value[:-1]+b'x')
        try:read(target,source,digest)
        except ValueError:return dict(expected_safe_stop=True)
        raise RuntimeError('CORRUPT_ACCEPTED')
    case('corrupt_checkpoint',corruption)
    def missing(trial):
        try:read(trial/'missing.checkpoint',source,digest)
        except FileNotFoundError:return dict(expected_safe_stop=True)
        raise RuntimeError('MISSING_ACCEPTED')
    case('missing_checkpoint',missing)
    def mismatch(trial):
        commit(trial,'block',body,source)
        for identity,value in ((dict(dataset='other'),digest),(source,'0'*64)):
            try:read(trial/'block.checkpoint',identity,value)
            except ValueError:continue
            raise RuntimeError('IDENTITY_OR_HASH_MISMATCH_ACCEPTED')
        return dict(expected_safe_stop=True)
    case('source_hash_consistency',mismatch)
    def traversal(trial):
        escape=trial.parent/'escape'
        try:commit(trial/'..'/'escape','block',body,source)
        except RuntimeError as exc:
            if str(exc)!='PATH_TRAVERSAL_FORBIDDEN' or escape.exists():raise
            return dict(expected_safe_stop=True,no_outside_mutation=True)
        raise RuntimeError('TRAVERSAL_ACCEPTED')
    case('traversal_no_mutation',traversal)
    def fatal_restart(trial):
        from atomic_checkpoint import durable_record
        def stop_before(label,path):
            if label=='before_publish':raise RuntimeError('INJECT_BEFORE_NATIVE')
        try:commit(trial,'block',body,source,hook=stop_before)
        except RuntimeError as exc:
            if str(exc)!='INJECT_BEFORE_NATIVE':raise
        journal=next((trial/'staging').iterdir());identity=r.load(journal/'identity.json')
        durable_record(journal/'1.intent.json',dict(attempt=1,identity=identity))
        durable_record(journal/'1.result.json',dict(attempt=1,native_success=False,winerror=17))
        try:commit(trial,'block',body,source)
        except RuntimeError as exc:
            if str(exc)!='PRESERVED_TERMINAL_COMMIT_RESULT' or (trial/'block.checkpoint').exists():raise
            return dict(expected_safe_stop=True,winerror=17,no_STOP_file_required=True,no_native_retry=True)
        raise RuntimeError('FATAL_RESTART_ACCEPTED')
    case('fatal_result_without_STOP',fatal_restart)
    def interrupt(trial,boundary):
        result=subprocess.run([sys.executable,str(Path(__file__).resolve()),'--interrupt',str(trial),boundary],capture_output=True,text=True)
        if result.returncode!=97:raise RuntimeError('INTERRUPTION_NOT_EXECUTED')
        receipt=commit(trial,'block',body,source)
        if read(trial/'block.checkpoint',source,digest)!=body:raise RuntimeError('INTERRUPTION_RESUME_INVALID')
        return dict(injected_process_exit=97,resumed_complete=True,idempotent=receipt['idempotent'],resume_events=receipt['events'])
    case('interrupt_before_publish',lambda trial:interrupt(trial,'before_publish'))
    case('interrupt_after_publish_before_receipt',lambda trial:interrupt(trial,'after_publish'))
    def cross_volume(trial):
        try:commit(Path('Z:/outside_authorized_study'),'block',body,source)
        except RuntimeError as exc:
            if str(exc)!='OUTSIDE_SYNTHETIC_STUDY':raise
            return dict(expected_safe_stop=True,error_code=str(exc),scope='Other-volume root refused before I/O; no actual cross-volume move performed')
        raise RuntimeError('OTHER_VOLUME_ACCEPTED')
    case('cross_volume_root_rejection',cross_volume)
    def reparse(trial):
        target=prepare(trial/'target');link=trial/'junction'
        process=subprocess.run(['cmd','/d','/c','mklink','/J',str(link),str(target)],capture_output=True,text=True)
        if process.returncode:raise RuntimeError('SYNTHETIC_JUNCTION_CREATION_FAILED')
        try:commit(link,'block',body,source)
        except RuntimeError as exc:
            if str(exc)!='REPARSE_POINT_FORBIDDEN':raise
            return dict(expected_safe_stop=True,error_code=str(exc),native_junction_tested=True)
        raise RuntimeError('REPARSE_ACCEPTED')
    case('reparse_rejection',reparse)
    def during(trial):
        from envelope import pack
        commit(trial,'block',body,source);target=trial/'block.checkpoint'
        process=subprocess.Popen([sys.executable,str(Path(__file__).resolve()),'--during',str(trial)],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
        if process.stdout.readline().strip()!='READY':
            process.kill();process.communicate();raise RuntimeError('DURING_COMMIT_CHILD_NOT_READY')
        time.sleep(.005);process.kill();out,err=process.communicate(timeout=10)
        value=target.read_bytes()
        if value not in (pack(body,source),pack(new,source)):raise RuntimeError('TORN_ARTIFACT_AFTER_PROCESS_KILL')
        receipt=commit(trial,'block',new,source,r.sha(target))
        return dict(injected_process_exit=process.returncode,complete_old_or_new_observed=True,resume_complete=receipt['committed'],
            kill_scope='Within commit interval; exact syscall instruction not instrumented')
    case('process_kill_during_commit_interval',during)
    return results


def main():
    require_custodian()
    if '--contender' in sys.argv:
        try:commit(Path(sys.argv[2]),'block',b'synthetic-old',dict(dataset='synthetic',version=1))
        except OSError as exc:
            import json
            print(json.dumps(dict(winerror=exc.winerror)));return
        raise RuntimeError('UNEXPECTED_CONTENDER_RESULT')
    if '--during' in sys.argv:
        root=Path(sys.argv[2]);target=root/'block.checkpoint'
        def hook(label,path):
            if label=='before_publish':print('READY',flush=True);time.sleep(.02)
        commit(root,'block',b'synthetic-new',dict(dataset='synthetic',version=1),r.sha(target),hook)
        time.sleep(2);return
    if '--interrupt' in sys.argv:
        root=Path(sys.argv[2]);boundary=sys.argv[3]
        commit(root,'block',b'synthetic-old',dict(dataset='synthetic',version=1),hook=lambda label,path:os._exit(97) if label==boundary else None)
        return
    if '--child' in sys.argv:
        root=prepare(Path(sys.argv[2]));r.save(Path(sys.argv[3]),fixtures(root,100,'fresh_trusted_host_child'));return
    verify_history()
    seal=r.load(r.HERE/'implementation_registration2.json')
    for name,digest in seal['sha256'].items():
        if r.sha(r.HERE/name)!=digest:raise RuntimeError('IMPLEMENTATION_CHANGED')
    private=prepare(r.HERE/'.private');run=prepare(private/('run_'+uuid.uuid4().hex))
    result=dict(synthetic_only=True,neural_source_requests=0,protected_neural_contents_read=False,
        synthetic_run_namespace=run.name,
        os=platform.platform(),python=sys.version,st_dev=run.stat().st_dev,base_registration_sha256=r.sha(r.HERE/'registration.json'),
        implementation_registration_sha256=r.sha(r.HERE/'implementation_registration2.json'))
    result['original_directory_rename_trials']=original(prepare(run/'original'))
    result['noninjected_commits']=fixtures(prepare(run/'main'),100,'trusted_host_main')
    child=run/'child_receipt.json'
    process=subprocess.run([sys.executable,str(Path(__file__).resolve()),'--child',str(run/'child'),str(child)],capture_output=True,text=True)
    result['child_exit_code']=process.returncode
    if child.exists():result['noninjected_commits']+=r.load(child)
    else:result['child_error_code']='CHILD_RECEIPT_MISSING'
    result['injected_tests']=injections(prepare(run/'injected'))
    for name,digest in seal['sha256'].items():
        if r.sha(r.HERE/name)!=digest:raise RuntimeError('IMPLEMENTATION_CHANGED_DURING_EVALUATION')
    result['end_implementation_verified']=True
    output=r.HERE/'results/native.json'
    if '--replay' in sys.argv:
        from custody_security import check_path
        output=check_path(Path(sys.argv[sys.argv.index('--replay')+1]))
    r.save(output,result,True)
    print(dict(noninjected_count=len(result['noninjected_commits']),unexpected_failures=sum(not x['passed'] for x in result['noninjected_commits']),
        injection_tests_pass=sum(x['test_pass'] for x in result['injected_tests']),injection_tests_count=len(result['injected_tests']),
        original_directory_failures=sum(not x['rename_pass'] for x in result['original_directory_rename_trials'])))


if __name__=='__main__':main()
