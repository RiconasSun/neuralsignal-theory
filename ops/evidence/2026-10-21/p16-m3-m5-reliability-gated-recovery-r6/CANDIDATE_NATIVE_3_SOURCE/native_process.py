"""Native R6 process primitives; no data/model access or OS configuration writes."""
import ctypes as c
from ctypes import wintypes as w
import os
import math
from pathlib import Path
import subprocess
import time

from paper16_dev_r3.windows_job import Job, Extended, k, checked, resume_suspended, require_job

CREATE_BREAKAWAY_FROM_JOB = 0x01000000
DETACHED_PROCESS = 0x00000008
CREATE_NEW_PROCESS_GROUP = 0x00000200

k.QueryInformationJobObject.argtypes = [w.HANDLE, c.c_int, c.c_void_p, w.DWORD, c.POINTER(w.DWORD)]
k.QueryInformationJobObject.restype = w.BOOL
k.OpenProcess.argtypes = [w.DWORD, w.BOOL, w.DWORD]
k.OpenProcess.restype = w.HANDLE
k.WaitForSingleObject.argtypes = [w.HANDLE, w.DWORD]
k.WaitForSingleObject.restype = w.DWORD
k.GetExitCodeProcess.argtypes = [w.HANDLE, c.POINTER(w.DWORD)]
k.GetExitCodeProcess.restype = w.BOOL
k.GetProcessTimes.argtypes = [w.HANDLE, c.POINTER(w.FILETIME), c.POINTER(w.FILETIME),
                             c.POINTER(w.FILETIME), c.POINTER(w.FILETIME)]
k.GetProcessTimes.restype = w.BOOL
k.QueryFullProcessImageNameW.argtypes = [w.HANDLE, w.DWORD, w.LPWSTR, c.POINTER(w.DWORD)]
k.QueryFullProcessImageNameW.restype = w.BOOL
k.TerminateProcess.argtypes = [w.HANDLE, w.UINT]
k.TerminateProcess.restype = w.BOOL
for name,args,result in [
    ('CreateMutexW',[c.c_void_p,w.BOOL,w.LPCWSTR],w.HANDLE),
    ('OpenMutexW',[w.DWORD,w.BOOL,w.LPCWSTR],w.HANDLE),
    ('ReleaseMutex',[w.HANDLE],w.BOOL),
    ('CreateEventW',[c.c_void_p,w.BOOL,w.BOOL,w.LPCWSTR],w.HANDLE),
    ('OpenEventW',[w.DWORD,w.BOOL,w.LPCWSTR],w.HANDLE),
    ('SetEvent',[w.HANDLE],w.BOOL),
]:
    fn=getattr(k,name);fn.argtypes=args;fn.restype=result


def current_job():
    member = w.BOOL()
    checked(k.IsProcessInJob(k.GetCurrentProcess(), None, c.byref(member)))
    result = {'in_job': bool(member.value), 'limit_flags': None}
    if member.value:
        limits = Extended()
        checked(k.QueryInformationJobObject(None, 9, c.byref(limits), c.sizeof(limits), None))
        result['limit_flags'] = int(limits.basic.flags)
        result['explicit_breakaway_allowed'] = bool(limits.basic.flags & 0x800)
        result['silent_breakaway_allowed'] = bool(limits.basic.flags & 0x1000)
        result['kill_on_job_close'] = bool(limits.basic.flags & 0x2000)
    return result


def detached_flags(context):
    """Select one API path before creation; never retry a denied launch."""
    if type(context.get('in_job')) is not bool:
        raise RuntimeError('Unknown inherited Job membership')
    flags=DETACHED_PROCESS|CREATE_NEW_PROCESS_GROUP
    if not context['in_job']:
        return flags
    limits=context.get('limit_flags')
    if type(limits) is not int or limits<0:
        raise RuntimeError('Unknown inherited Job flags')
    if limits&0x1000:  # SILENT_BREAKAWAY_OK: explicit flag would be incorrect.
        return flags
    if limits&0x800:
        return flags|CREATE_BREAKAWAY_FROM_JOB
    raise RuntimeError('Inherited Job permits neither silent nor explicit breakaway')


def bounded_wait(deadline,maximum):
    seconds=min(maximum,deadline-time.monotonic())
    if seconds<=0:
        raise TimeoutError('Original ownership deadline expired')
    return seconds


class OwnershipGate:
    """Claim-bound mutex and irreversible manual-reset cancellation Event.

    Every birth, publication, assignment and resume holds this mutex. Cleanup
    first sets the Event under the same mutex, so no later birth may begin.
    Abandoned ownership is uncertain and never a cleanup or capability PASS.
    """
    def __init__(self,name,deadline,*,create=False):
        self.deadline=deadline;self.mutex=None;self.cancel_event=None;self.uncertainty_event=None;self.acquired=False
        try:
            if create:
                c.set_last_error(0);self.mutex=checked(k.CreateMutexW(None,False,name+'_MUTEX'))
                if c.get_last_error()==183:raise RuntimeError('Ownership mutex already exists')
                c.set_last_error(0);self.cancel_event=checked(k.CreateEventW(None,True,False,name+'_CANCEL'))
                if c.get_last_error()==183:raise RuntimeError('Ownership Event already exists')
                c.set_last_error(0);self.uncertainty_event=checked(k.CreateEventW(None,True,False,name+'_UNCERTAIN'))
                if c.get_last_error()==183:raise RuntimeError('Ownership uncertainty Event already exists')
            else:
                self.mutex=checked(k.OpenMutexW(0x00100001,False,name+'_MUTEX'))
                self.cancel_event=checked(k.OpenEventW(0x00100002,False,name+'_CANCEL'))
                self.uncertainty_event=checked(k.OpenEventW(0x00100002,False,name+'_UNCERTAIN'))
        except BaseException:
            self.close();raise

    def __enter__(self):
        state=k.WaitForSingleObject(self.mutex,int(bounded_wait(self.deadline,120.)*1000))
        if state==128:
            # WAIT_ABANDONED grants the lock, but cannot prove creator quiescence.
            self.acquired=True
            try:self.mark_uncertain()
            finally:
                checked(k.ReleaseMutex(self.mutex));self.acquired=False
            raise RuntimeError('Abandoned ownership mutex; all-owned cleanup is unverified')
        if state!=0:
            self.mark_uncertain()
            raise RuntimeError('Ownership mutex unavailable before original deadline')
        self.acquired=True;return self

    def __exit__(self,*args):
        if self.acquired:
            self.acquired=False;checked(k.ReleaseMutex(self.mutex))

    def cancelled(self):
        state=k.WaitForSingleObject(self.cancel_event,0)
        if state not in [0,258]:raise RuntimeError('Cancellation Event state unavailable')
        return state==0

    def set_cancel(self):
        checked(k.SetEvent(self.cancel_event))

    def mark_uncertain(self):
        # Sticky across roles: releasing an abandoned mutex cannot erase doubt.
        try:checked(k.SetEvent(self.uncertainty_event))
        finally:self.set_cancel()

    def uncertain(self):
        state=k.WaitForSingleObject(self.uncertainty_event,0)
        if state not in [0,258]:raise RuntimeError('Ownership uncertainty Event state unavailable')
        return state==0

    def close(self):
        for name in ['uncertainty_event','cancel_event','mutex']:
            handle=getattr(self,name,None)
            if handle:k.CloseHandle(handle);setattr(self,name,None)


def handle_identity(handle, pid):
    created, ended, kernel, user = [w.FILETIME() for _ in range(4)]
    checked(k.GetProcessTimes(handle, c.byref(created), c.byref(ended),
                              c.byref(kernel), c.byref(user)))
    buffer = c.create_unicode_buffer(32768)
    length = w.DWORD(len(buffer))
    checked(k.QueryFullProcessImageNameW(handle, 0, buffer, c.byref(length)))
    return {'pid': pid, 'creation_FILETIME': (created.dwHighDateTime << 32) | created.dwLowDateTime,
            'image': buffer.value}


def own_identity():
    return handle_identity(k.GetCurrentProcess(), os.getpid())


class OriginalProcessGone(RuntimeError):
    pass


class OwnedProcess:
    """A stable handle, verified against the recorded creation epoch and image."""
    def __init__(self, identity, *, allow_terminate=False):
        self.expected = identity
        self.handle = k.OpenProcess(0x00101000 | (1 if allow_terminate else 0),
                                    False, identity['pid'])
        self.allow_terminate = allow_terminate
        if not self.handle:
            error = c.get_last_error()
            if error == 87:
                raise OriginalProcessGone('Original process is gone')
            raise c.WinError(error)
        try:
            if k.WaitForSingleObject(self.handle, 0) == 0:
                raise OriginalProcessGone('Recorded process has already exited')
            actual = handle_identity(self.handle, identity['pid'])
            if (actual['creation_FILETIME'] != identity['creation_FILETIME']
                    or os.path.normcase(actual['image']) != os.path.normcase(identity['image'])):
                raise OriginalProcessGone('PID reused; unrelated process is never terminated')
        except BaseException:
            self.close()
            raise

    def alive(self):
        state = k.WaitForSingleObject(self.handle, 0)
        if state == 0:
            return False
        if state != 258:
            raise RuntimeError('Native process wait status unavailable')
        return True

    def wait(self, seconds):
        state = k.WaitForSingleObject(self.handle, max(0, int(seconds * 1000)))
        if state == 258:
            raise TimeoutError('Owned process still active')
        if state != 0:
            raise RuntimeError('Owned process wait failed')
        code = w.DWORD()
        checked(k.GetExitCodeProcess(self.handle, c.byref(code)))
        return int(code.value)

    def terminate(self):
        if not self.allow_terminate:
            raise RuntimeError('Termination not authorized on this verified handle')
        if self.alive():
            checked(k.TerminateProcess(self.handle, 201))

    def close(self):
        if self.handle:
            k.CloseHandle(self.handle)
            self.handle = None

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


def identity_alive(identity):
    try:
        with OwnedProcess(identity) as process:
            return process.alive()
    except OriginalProcessGone:
        return False


def wait_identity_dead(identity, seconds):
    try:
        with OwnedProcess(identity) as process:
            return process.wait(seconds)
    except OriginalProcessGone:
        return None


def valid_json(value):
    """Exact JSON types; Python bool/int coercion is never certificate identity."""
    if value is None or type(value) in [str,bool,int]:return True
    if type(value) is float:return math.isfinite(value)
    if type(value) is list:return all(valid_json(item) for item in value)
    if type(value) is dict:return all(type(key) is str and valid_json(item) for key,item in value.items())
    return False


def exact_json(left,right):
    if not valid_json(left) or not valid_json(right) or type(left) is not type(right):return False
    if type(left) is dict:return left.keys()==right.keys() and all(exact_json(left[key],right[key]) for key in left)
    if type(left) is list:return len(left)==len(right) and all(exact_json(a,b) for a,b in zip(left,right))
    return left==right


def finalize_owned(cancel_action,cleanup_action):
    """Pure orchestration: disk failure cannot bypass handle-bound cleanup."""
    failures=[];cleanup_result=None
    try:
        try:cancel_action()
        except BaseException as exc:failures.append({'phase':'cancellation','type':type(exc).__name__,'message':str(exc)})
    finally:
        try:cleanup_result=cleanup_action()
        except BaseException as exc:failures.append({'phase':'cleanup','type':type(exc).__name__,'message':str(exc)})
    return {'failures':failures,'cleanup':cleanup_result,'all_finalization_actions_succeeded':not failures}


def classify_terminal(outcome, completion, expected):
    """Native integrity only: caller must provide its exact frozen completion.

    This never certifies model numerics or independent M4 approval by itself.
    Missing/malformed/altered completion is fail closed even after native exit0.
    """
    reason = None
    if type(outcome) is not dict or not valid_json(outcome) or type(outcome.get('returncode')) is not int:
        reason = 'MALFORMED_NATIVE_OUTCOME'
    elif outcome['returncode'] != 0:
        reason = 'NONZERO_NATIVE_EXIT'
    elif any(outcome.get(k) is not True for k in ['native_job_tree_enforced', 'assigned_before_resume']):
        reason = 'MISSING_NATIVE_CONTAINMENT'
    elif outcome.get('killed_at_deadline') is not False:
        reason = 'DEADLINE_OR_UNKNOWN_TERMINATION'
    elif type(expected) is not dict or not expected or not valid_json(expected):
        reason = 'MISSING_FROZEN_EXPECTATION'
    elif type(completion) is not dict or not exact_json(completion,expected):
        reason = 'MISSING_MALFORMED_OR_IDENTITY_MISMATCHED_COMPLETION'
    return {'decision': 'STOP' if reason else 'ACCEPTED_NATIVE_COMPLETION',
            'reason': reason, 'native_completion_accepted': reason is None,
            'scientific_or_M4_PASS_implied': False}


def supervise(command, cwd, log_path, job_name, timeout, *, total_deadline, guard,spawn,ownership):
    """Actual Job implementation used by the fixture and proposed R6 worker."""
    guard()
    deadline = min(time.monotonic() + timeout, total_deadline-5)
    killed = False
    with Path(log_path).open('xb') as log:
        with Job(job_name) as job:
            child_env = os.environ.copy()
            child_env['P16_R6_SYNTHETIC_JOB'] = job_name
            child = spawn(command,cwd,log,env=child_env,job=job,job_name=job_name)
            try:
                while child.poll() is None:
                    guard()
                    if time.monotonic() >= deadline:
                        with ownership:job.terminate()
                        killed = True
                        break
                    time.sleep(0.01)
                code = child.wait(timeout=bounded_wait(total_deadline,3.))
            except BaseException:
                with ownership:
                    ownership.set_cancel()
                    try:job.terminate()
                    finally:
                        if child.poll() is None:child.kill()
                        child.wait(timeout=bounded_wait(total_deadline,3.))
                raise
    return {'returncode': code, 'killed_at_deadline': killed,
            'native_job_tree_enforced': True, 'assigned_before_resume': True,
            'job_name': job_name, 'child_pid': child.pid}
