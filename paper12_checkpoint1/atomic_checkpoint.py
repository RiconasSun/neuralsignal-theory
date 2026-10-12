"""Same-volume native publication, bounded retries and exclusive writer fencing."""
import ctypes
import hashlib
import os
import time
import uuid
from contextlib import contextmanager
from pathlib import Path
import win32file
import win32con
import pywintypes
import study as r
from custody_security import check_path,check_acl,prepare,protect,require_custodian,native_path
from envelope import pack,unpack


def durable_record(path,value):
    import json
    with path.open('x',encoding='utf-8',newline='\n') as stream:
        json.dump(value,stream,sort_keys=True);stream.flush();os.fsync(stream.fileno())
    protect(path)


@contextmanager
def writer_lock(root,name):
    lock=root/(name+'.writer.lock')
    handle=win32file.CreateFile(native_path(lock),win32con.GENERIC_READ|win32con.GENERIC_WRITE,
        win32con.FILE_SHARE_READ|win32con.FILE_SHARE_WRITE,None,win32con.OPEN_ALWAYS,win32con.FILE_ATTRIBUTE_NORMAL,None)
    try:
        protect(lock);check_acl(lock)
        class Overlapped(ctypes.Structure):
            _fields_=[('internal',ctypes.c_size_t),('internal_high',ctypes.c_size_t),('offset',ctypes.c_ulong),('offset_high',ctypes.c_ulong),('event',ctypes.c_void_p)]
        k=ctypes.WinDLL('kernel32',use_last_error=True)
        k.LockFileEx.argtypes=[ctypes.c_void_p,ctypes.c_ulong,ctypes.c_ulong,ctypes.c_ulong,ctypes.c_ulong,ctypes.POINTER(Overlapped)]
        ov=Overlapped()
        if not k.LockFileEx(int(handle),3,0,1,0,ctypes.byref(ov)):raise ctypes.WinError(ctypes.get_last_error())
        yield
    finally:handle.Close()


def read(path,source,digest):
    check_acl(path)
    if Path(path).stat().st_size>4194304+65548:raise ValueError('ENVELOPE_SIZE_INVALID')
    return unpack(Path(path).read_bytes(),source,digest)


def commit(root,name,body,source,expected_previous=None,hook=None):
    require_custodian();root=check_path(root);check_acl(root)
    if not name.isidentifier():raise ValueError('CHECKPOINT_NAME_INVALID')
    stage_dir=root/'staging'
    if not stage_dir.exists():prepare(stage_dir)
    check_acl(stage_dir)
    if root.stat().st_dev!=stage_dir.stat().st_dev:raise RuntimeError('CROSS_VOLUME_FORBIDDEN')
    digest=hashlib.sha256(body).hexdigest();target=root/(name+'.checkpoint');events=[]
    check_path(target)
    hook=hook or (lambda stage,path:None)
    with writer_lock(root,name):
        if target.exists():
            check_acl(target)
            try:
                if read(target,source,digest)==body:return dict(committed=True,idempotent=True,attempts=0,events=events,body_sha256=digest)
            except (ValueError,KeyError):
                if expected_previous is None:raise
            if expected_previous is None or hashlib.sha256(target.read_bytes()).hexdigest()!=expected_previous:
                raise RuntimeError('PREVIOUS_ARTIFACT_CONFLICT')
        elif expected_previous is not None:raise RuntimeError('PREVIOUS_ARTIFACT_MISSING')
        encoded=pack(body,source)
        artifact_digest=hashlib.sha256(encoded).hexdigest()
        journal=stage_dir/(name+'_'+artifact_digest[:32])
        if len(str(journal/'payload.pending'))>=248:raise RuntimeError('CHECKPOINT_PATH_TOO_LONG')
        if not journal.exists():prepare(journal)
        check_acl(journal)
        identity=dict(source=source,body_sha256=digest,artifact_sha256=artifact_digest,expected_previous=expected_previous)
        identity_path=journal/'identity.json'
        if identity_path.exists():
            if r.load(identity_path)!=identity:raise RuntimeError('RESUME_IDENTITY_MISMATCH')
        else:durable_record(identity_path,identity)
        stop=journal/'STOP.json'
        if stop.exists():raise RuntimeError('PRESERVED_ATOMIC_COMMIT_STOP')
        stage=journal/'payload.pending'
        if not stage.exists():
            with stage.open('xb') as stream:
                protect(stage)
                midpoint=len(encoded)//2;stream.write(encoded[:midpoint]);stream.flush();os.fsync(stream.fileno())
                hook('during_write',stage)
                stream.write(encoded[midpoint:]);stream.flush();os.fsync(stream.fileno())
            protect(stage)
        check_acl(stage)
        if read(stage,source,digest)!=body:raise RuntimeError('STAGING_VERIFICATION_FAILED')
        used=[n for n in range(1,4) if (journal/(str(n)+'.intent.json')).exists()]
        if used!=list(range(1,len(used)+1)):raise RuntimeError('COMMIT_JOURNAL_INVALID')
        for number in used:
            if r.load(journal/(str(number)+'.intent.json'))!=dict(attempt=number,identity=identity):
                raise RuntimeError('COMMIT_INTENT_IDENTITY_INVALID')
            saved=journal/(str(number)+'.result.json')
            if saved.exists():
                result=r.load(saved)
                if result.get('attempt')!=number or type(result.get('native_success')) is not bool:
                    raise RuntimeError('COMMIT_RESULT_INVALID')
                if result['native_success']:raise RuntimeError('SAVED_COMMIT_SUCCESS_WITHOUT_ARTIFACT')
                if result.get('winerror') not in (5,32,33) or number==3:
                    raise RuntimeError('PRESERVED_TERMINAL_COMMIT_RESULT')
        if len(used)==3:raise RuntimeError('ATOMIC_COMMIT_BUDGET_EXHAUSTED')
        hook('before_publish',stage)
        for attempt in range(len(used)+1,4):
            check_acl(root);check_acl(stage_dir);check_acl(stage)
            if target.exists():check_acl(target)
            # No MOVEFILE_COPY_ALLOWED, delete-first operation or directory rename.
            flags=8|(1 if expected_previous is not None else 0)
            durable_record(journal/(str(attempt)+'.intent.json'),dict(attempt=attempt,identity=identity))
            try:
                if expected_previous is None:
                    win32file.MoveFileEx(native_path(stage),native_path(target),flags)
                else:
                    kernel=ctypes.WinDLL('kernel32',use_last_error=True)
                    kernel.ReplaceFileW.argtypes=[ctypes.c_wchar_p,ctypes.c_wchar_p,ctypes.c_wchar_p,ctypes.c_ulong,ctypes.c_void_p,ctypes.c_void_p]
                    # No ignore-ACL/merge flags; old protected artifact remains in backup.
                    if not kernel.ReplaceFileW(native_path(target),native_path(stage),native_path(journal/'previous.backup'),0,None,None):
                        raise ctypes.WinError(ctypes.get_last_error())
                events.append(dict(attempt=attempt,native_success=True))
                durable_record(journal/(str(attempt)+'.result.json'),events[-1]);break
            except (OSError,pywintypes.error) as exc:
                code=getattr(exc,'winerror',None) or (exc.args[0] if exc.args else None)
                events.append(dict(attempt=attempt,native_success=False,winerror=code))
                durable_record(journal/(str(attempt)+'.result.json'),events[-1])
                hook('native_denied',stage)
                if code not in (5,32,33) or attempt==3:
                    durable_record(stop,dict(events=events,error_code='ATOMIC_COMMIT_SAFE_STOP'))
                    error=RuntimeError('ATOMIC_COMMIT_SAFE_STOP');error.events=events;raise error from exc
                time.sleep((.1,.5)[attempt-1])
        hook('after_publish',target)
        check_acl(target)
        if hashlib.sha256(target.read_bytes()).hexdigest()!=artifact_digest or read(target,source,digest)!=body:
            raise RuntimeError('POST_COMMIT_INTEGRITY_FAILED')
        return dict(committed=True,idempotent=False,attempts=attempt,events=events,body_sha256=digest,artifact_sha256=artifact_digest)
