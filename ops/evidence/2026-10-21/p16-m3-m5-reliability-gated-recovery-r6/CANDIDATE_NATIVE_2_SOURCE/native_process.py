"""Native R6 process primitives; no data/model access or OS configuration writes."""
import ctypes as c
from ctypes import wintypes as w
import os
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


def launch_detached(command, cwd, stdout, *, breakaway):
    """No fallbacks: failed breakaway never retries inside the inherited Job."""
    flags = DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP
    if breakaway:
        flags |= CREATE_BREAKAWAY_FROM_JOB
    return subprocess.Popen(command, cwd=cwd, stdin=subprocess.DEVNULL, stdout=stdout,
                            stderr=subprocess.STDOUT, close_fds=True, creationflags=flags)


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


def classify_terminal(outcome, completion, expected):
    """Native integrity only: caller must provide its exact frozen completion.

    This never certifies model numerics or independent M4 approval by itself.
    Missing/malformed/altered completion is fail closed even after native exit0.
    """
    reason = None
    if not isinstance(outcome, dict) or type(outcome.get('returncode')) is not int:
        reason = 'MALFORMED_NATIVE_OUTCOME'
    elif outcome['returncode'] != 0:
        reason = 'NONZERO_NATIVE_EXIT'
    elif any(outcome.get(k) is not True for k in ['native_job_tree_enforced', 'assigned_before_resume']):
        reason = 'MISSING_NATIVE_CONTAINMENT'
    elif outcome.get('killed_at_deadline') is not False:
        reason = 'DEADLINE_OR_UNKNOWN_TERMINATION'
    elif not isinstance(expected, dict) or not expected:
        reason = 'MISSING_FROZEN_EXPECTATION'
    elif not isinstance(completion, dict) or completion != expected:
        reason = 'MISSING_MALFORMED_OR_IDENTITY_MISMATCHED_COMPLETION'
    return {'decision': 'STOP' if reason else 'ACCEPTED_NATIVE_COMPLETION',
            'reason': reason, 'native_completion_accepted': reason is None,
            'scientific_or_M4_PASS_implied': False}


def supervise(command, cwd, log_path, job_name, timeout, *, total_deadline, guard):
    """Actual Job implementation used by the fixture and proposed R6 worker."""
    guard()
    deadline = min(time.monotonic() + timeout, total_deadline)
    killed = False
    with Path(log_path).open('xb') as log:
        with Job(job_name) as job:
            child_env = os.environ.copy()
            child_env['P16_R6_SYNTHETIC_JOB'] = job_name
            child = subprocess.Popen(command, cwd=cwd, stdout=log, stderr=subprocess.STDOUT,
                                     creationflags=0x4, env=child_env)
            try:
                job.assign(child)
                resume_suspended(child)
                while child.poll() is None:
                    guard()
                    if time.monotonic() >= deadline:
                        job.terminate()
                        killed = True
                        break
                    time.sleep(0.01)
                code = child.wait(timeout=max(.1, deadline-time.monotonic()))
            except BaseException:
                job.terminate()
                if child.poll() is None:
                    child.kill()
                child.wait(timeout=max(.1, min(3., total_deadline-time.monotonic())))
                raise
    return {'returncode': code, 'killed_at_deadline': killed,
            'native_job_tree_enforced': True, 'assigned_before_resume': True,
            'job_name': job_name, 'child_pid': child.pid}
