"""Windows process-tree wall supervision; no data/security authorization policy."""
import ctypes as c
from ctypes import wintypes as w
import os

if os.name != 'nt': raise RuntimeError('Native Windows process supervisor required')
k = c.WinDLL('kernel32', use_last_error=True)


class Limits(c.Structure):
    _fields_ = [('process_time', c.c_longlong), ('job_time', c.c_longlong), ('flags', w.DWORD),
                ('min_working_set', c.c_size_t), ('max_working_set', c.c_size_t), ('active_limit', w.DWORD),
                ('affinity', c.c_size_t), ('priority', w.DWORD), ('scheduling', w.DWORD)]


class IO(c.Structure):
    _fields_ = [(name, c.c_ulonglong) for name in ['read_ops', 'write_ops', 'other_ops', 'read_bytes', 'write_bytes', 'other_bytes']]


class Extended(c.Structure):
    _fields_ = [('basic', Limits), ('io', IO), ('process_memory', c.c_size_t), ('job_memory', c.c_size_t),
                ('peak_process_memory', c.c_size_t), ('peak_job_memory', c.c_size_t)]


class ThreadEntry(c.Structure):
    _fields_ = [('size', w.DWORD), ('usage', w.DWORD), ('tid', w.DWORD), ('pid', w.DWORD),
                ('base_priority', w.LONG), ('delta_priority', w.LONG), ('flags', w.DWORD)]


for name, args, result in [
    ('CreateJobObjectW', [c.c_void_p, w.LPCWSTR], w.HANDLE),
    ('OpenJobObjectW', [w.DWORD, w.BOOL, w.LPCWSTR], w.HANDLE),
    ('SetInformationJobObject', [w.HANDLE, c.c_int, c.c_void_p, w.DWORD], w.BOOL),
    ('AssignProcessToJobObject', [w.HANDLE, w.HANDLE], w.BOOL),
    ('TerminateJobObject', [w.HANDLE, w.UINT], w.BOOL),
    ('IsProcessInJob', [w.HANDLE, w.HANDLE, c.POINTER(w.BOOL)], w.BOOL),
    ('GetCurrentProcess', [], w.HANDLE), ('CloseHandle', [w.HANDLE], w.BOOL),
    ('CreateToolhelp32Snapshot', [w.DWORD, w.DWORD], w.HANDLE),
    ('Thread32First', [w.HANDLE, c.POINTER(ThreadEntry)], w.BOOL),
    ('Thread32Next', [w.HANDLE, c.POINTER(ThreadEntry)], w.BOOL),
    ('OpenThread', [w.DWORD, w.BOOL, w.DWORD], w.HANDLE),
    ('ResumeThread', [w.HANDLE], w.DWORD),
]:
    fn = getattr(k, name); fn.argtypes = args; fn.restype = result


def checked(value):
    if not value: raise c.WinError(c.get_last_error())
    return value


def require_job(name):
    handle = checked(k.OpenJobObjectW(4, False, name))  # JOB_OBJECT_QUERY
    try:
        member = w.BOOL()
        checked(k.IsProcessInJob(k.GetCurrentProcess(), handle, c.byref(member)))
        if not member.value: raise RuntimeError('Worker is outside its exact external Job')
    finally: k.CloseHandle(handle)  # never retain a child handle that defeats kill-on-last-close


def resume_suspended(process):
    snapshot = k.CreateToolhelp32Snapshot(4, 0)  # TH32CS_SNAPTHREAD
    if snapshot == c.c_void_p(-1).value: raise c.WinError(c.get_last_error())
    threads = []
    try:
        entry = ThreadEntry(); entry.size = c.sizeof(entry)
        more = k.Thread32First(snapshot, c.byref(entry))
        while more:
            if entry.pid == process.pid: threads.append(entry.tid)
            more = k.Thread32Next(snapshot, c.byref(entry))
    finally: k.CloseHandle(snapshot)
    if len(threads) != 1: raise RuntimeError('Suspended own child must have exactly one primary thread')
    thread = checked(k.OpenThread(2, False, threads[0]))  # THREAD_SUSPEND_RESUME
    try:
        previous = k.ResumeThread(thread)
        if previous != 1: raise RuntimeError('Unexpected primary-thread suspend count')
    finally: k.CloseHandle(thread)


class Job:
    def __init__(self, name):
        c.set_last_error(0); self.handle = checked(k.CreateJobObjectW(None, name))
        if c.get_last_error() == 183:
            k.CloseHandle(self.handle); self.handle = None
            raise RuntimeError('Refuse to reuse an existing named process Job')
        limits = Extended(); limits.basic.flags = 0x2000  # JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE; no breakaway
        try: checked(k.SetInformationJobObject(self.handle, 9, c.byref(limits), c.sizeof(limits)))
        except BaseException:
            k.CloseHandle(self.handle); self.handle = None; raise
    def assign(self, process): checked(k.AssignProcessToJobObject(self.handle, w.HANDLE(int(process._handle))))
    def terminate(self): checked(k.TerminateJobObject(self.handle, 124))
    def close(self):
        if self.handle:
            checked(k.CloseHandle(self.handle)); self.handle = None
    def __enter__(self): return self
    def __exit__(self, *args): self.close()
