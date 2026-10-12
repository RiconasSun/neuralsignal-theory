"""Bounded native AppContainer alternative; synthetic files only, no neural access."""
import ctypes as c
from ctypes import wintypes as w
import os
import sys
import shutil
import subprocess
from pathlib import Path
import win32api
import win32security as ws
import ntsecuritycon as rights
import register as r
from security import require_custodian, token_info, protect, sid_text


def main():
    r.verify()
    require_custodian()
    api = c.WinDLL('userenv', use_last_error=True)
    api.CreateAppContainerProfile.argtypes = [w.LPCWSTR, w.LPCWSTR, w.LPCWSTR, c.c_void_p, w.DWORD, c.POINTER(c.c_void_p)]
    api.CreateAppContainerProfile.restype = c.c_long
    api.DeleteAppContainerProfile.argtypes = [w.LPCWSTR]
    api.DeleteAppContainerProfile.restype = c.c_long
    sid = c.c_void_p()
    name = 'P12CustodyProbe.' + os.urandom(8).hex()
    result = {'synthetic_only': True, 'native_profile_created': False, 'native_launch_succeeded': False,
              'source_full_session_decoded_by_custodian': False, 'final_values_exposed_to_analysis': False,
              'final_holdout_evaluated': False, 'mandatory_isolation_pass': False}
    hr = api.CreateAppContainerProfile(name, name, 'Synthetic custody boundary probe', None, 0, c.byref(sid))
    result['profile_creation_hresult'] = '0x%08x' % (hr & 0xffffffff)
    if hr != 0:
        r.save(r.HERE / output_name(), result, True)
        print(result)
        return
    result['native_profile_created'] = True
    package = sid_text(sid)
    root = r.HERE / 'exports/native_probe'
    root.mkdir(parents=True, exist_ok=True)
    user = ws.GetTokenInformation(ws.OpenProcessToken(win32api.GetCurrentProcess(), rights.TOKEN_QUERY), ws.TokenUser)[0]
    acl = ws.ACL()
    flags = ws.OBJECT_INHERIT_ACE | ws.CONTAINER_INHERIT_ACE
    for s in (user, ws.ConvertStringSidToSid(package)):
        acl.AddAccessAllowedAceEx(ws.ACL_REVISION, flags, rights.FILE_ALL_ACCESS, s)
    ws.SetNamedSecurityInfo(str(root), ws.SE_FILE_OBJECT, ws.DACL_SECURITY_INFORMATION | ws.PROTECTED_DACL_SECURITY_INFORMATION,
                           None, None, acl, None)
    source = r.HERE / '.private/native_probe_source.bin'
    key = r.HERE / '.private/native_probe_key.bin'
    for p in (source, key):
        p.write_bytes(os.urandom(32))
        protect(p, package)
    result['host_positive_reads'] = all(len(p.read_bytes()) == 32 for p in (source, key))

    class SI(c.Structure):
        _fields_ = [('cb', w.DWORD), ('lpReserved', w.LPWSTR), ('lpDesktop', w.LPWSTR), ('lpTitle', w.LPWSTR),
                    ('dwX', w.DWORD), ('dwY', w.DWORD), ('dwXSize', w.DWORD), ('dwYSize', w.DWORD),
                    ('dwXCountChars', w.DWORD), ('dwYCountChars', w.DWORD), ('dwFillAttribute', w.DWORD), ('dwFlags', w.DWORD),
                    ('wShowWindow', w.WORD), ('cbReserved2', w.WORD), ('lpReserved2', c.c_void_p),
                    ('hStdInput', w.HANDLE), ('hStdOutput', w.HANDLE), ('hStdError', w.HANDLE)]
    class SIX(c.Structure):
        _fields_ = [('si', SI), ('attrs', c.c_void_p)]
    class PI(c.Structure):
        _fields_ = [('process', w.HANDLE), ('thread', w.HANDLE), ('pid', w.DWORD), ('tid', w.DWORD)]
    class Caps(c.Structure):
        _fields_ = [('sid', c.c_void_p), ('caps', c.c_void_p), ('count', w.DWORD), ('reserved', w.DWORD)]
    k = c.WinDLL('kernel32', use_last_error=True)
    k.InitializeProcThreadAttributeList.argtypes = [c.c_void_p, w.DWORD, w.DWORD, c.POINTER(c.c_size_t)]
    k.UpdateProcThreadAttribute.argtypes = [c.c_void_p, w.DWORD, c.c_size_t, c.c_void_p, c.c_size_t, c.c_void_p, c.c_void_p]
    k.DeleteProcThreadAttributeList.argtypes = [c.c_void_p]
    k.CreateProcessW.argtypes = [w.LPCWSTR, w.LPWSTR, c.c_void_p, c.c_void_p, w.BOOL, w.DWORD,
                                c.c_void_p, w.LPCWSTR, c.POINTER(SIX), c.POINTER(PI)]
    for func in ('ResumeThread', 'WaitForSingleObject', 'CloseHandle', 'TerminateProcess', 'GetExitCodeProcess'):
        getattr(k, func).argtypes = {'ResumeThread':[w.HANDLE], 'WaitForSingleObject':[w.HANDLE,w.DWORD],
                                   'CloseHandle':[w.HANDLE], 'TerminateProcess':[w.HANDLE,w.UINT],
                                   'GetExitCodeProcess':[w.HANDLE,c.POINTER(w.DWORD)]}[func]
    size = c.c_size_t()
    k.InitializeProcThreadAttributeList(None, 1, 0, c.byref(size))
    buf = c.create_string_buffer(size.value)
    caps = Caps(sid, None, 0, 0)
    if not k.InitializeProcThreadAttributeList(buf, 1, 0, c.byref(size)):
        raise RuntimeError('NATIVE_ATTRIBUTES_INIT_FAILED')
    if not k.UpdateProcThreadAttribute(buf, 0, 0x20009, c.byref(caps), c.sizeof(caps), None, None):
        raise RuntimeError('NATIVE_CAPABILITIES_FAILED')
    names = ('SystemRoot', 'WINDIR', 'SystemDrive', 'USERPROFILE', 'LOCALAPPDATA', 'APPDATA', 'ProgramData', 'COMSPEC')
    public_env = {key: os.environ[key] for key in names if key in os.environ}
    public_env['PATH'] = os.environ['SystemRoot'] + '\\System32'
    public_env['TEMP'] = str(root)
    public_env['TMP'] = str(root)
    result['environment_name_whitelist'] = sorted(public_env)
    env = c.create_unicode_buffer('\0'.join(key + '=' + public_env[key] for key in sorted(public_env, key=str.upper)) + '\0\0')
    def run(label, command):
        si = SIX()
        si.si.cb = c.sizeof(SIX)
        si.si.dwFlags = 1
        si.si.wShowWindow = 0
        si.attrs = c.addressof(buf)
        pi = PI()
        exe = Path(os.environ['SystemRoot']) / 'System32/cmd.exe'
        output = root / (label + '.out')
        error = root / (label + '.err')
        body = command + ' >"' + str(output) + '" 2>"' + str(error) + '"'
        line = c.create_unicode_buffer('"' + str(exe) + '" /d /s /c "' + body + '"')
        ok = k.CreateProcessW(str(exe), line, None, None, False, 0x80000 | 4 | 0x8000000 | 0x400,
                              env, str(root), c.byref(si), c.byref(pi))
        if not ok:
            return {'created': False, 'winerror': c.get_last_error(), 'child_appcontainer': None}
        try:
            child = ws.OpenProcessToken(int(pi.process), rights.TOKEN_QUERY)
            adv = c.WinDLL('advapi32')
            adv.GetTokenInformation.argtypes = [w.HANDLE,c.c_int,c.c_void_p,w.DWORD,c.POINTER(w.DWORD)]
            flag, n = w.DWORD(), w.DWORD()
            got = adv.GetTokenInformation(int(child),29,c.byref(flag),4,c.byref(n))
            k.ResumeThread(pi.thread)
            status = k.WaitForSingleObject(pi.process,15000)
            if status == 258:
                k.TerminateProcess(pi.process,99)
                k.WaitForSingleObject(pi.process,3000)
            code = w.DWORD()
            k.GetExitCodeProcess(pi.process,c.byref(code))
            return {'created': True, 'child_appcontainer': bool(flag.value) if got else None,
                    'exit_code': code.value, 'timed_out': status == 258}
        finally:
            k.CloseHandle(pi.thread)
            k.CloseHandle(pi.process)
    try:
        result['allowed_output_probe'] = run('allowed', 'echo ALLOWED')
        result['source_probe'] = run('source', 'type "' + str(source) + '"')
        result['key_probe'] = run('key', 'type "' + str(key) + '"')
        result['dacl_probe'] = run('dacl', 'icacls "' + str(key) + '" /grant *' + ws.ConvertSidToStringSid(user) + ':F')
        result['native_launch_succeeded'] = result['allowed_output_probe'].get('created',False)
        positive = result['allowed_output_probe'].get('exit_code') == 0
        denied = all(result[x].get('created') and result[x].get('child_appcontainer') is True and
                     result[x].get('exit_code') not in (None,0,99) for x in ('source_probe','key_probe','dacl_probe'))
        # Native filesystem probes alone do not constitute a full runtime/network gate.
        result['filesystem_probe_pass'] = positive and denied
        result['network_and_scientific_runtime_verified'] = False
        if '--runtime' in sys.argv and result['filesystem_probe_pass']:
            runtime = root / 'runtime'
            base = runtime / 'base'
            deps = runtime / 'deps'
            if not base.exists():
                shutil.copytree(sys.base_prefix,base,ignore=shutil.ignore_patterns('__pycache__'))
            deps.mkdir(parents=True,exist_ok=True)
            installed = Path(sys.executable).parent.parent / 'Lib/site-packages'
            for p in installed.iterdir():
                if p.name in ('numpy','numpy.libs','scipy','scipy.libs','h5py','h5py.libs','cryptography','cffi') or p.name.startswith('_cffi_backend'):
                    target = deps / p.name
                    if p.is_dir() and not target.exists():
                        shutil.copytree(p,target,ignore=shutil.ignore_patterns('__pycache__'))
                    elif p.is_file():
                        shutil.copy2(p,target)
            script = runtime / 'runtime_canary.py'
            shutil.copy2(r.HERE/'runtime_canary.py',script)
            # Only this copied runtime gets an explicit native-role read/execute grant.
            ro = ws.ACL()
            ro.AddAccessAllowedAceEx(ws.ACL_REVISION,flags,rights.READ_CONTROL,ws.ConvertStringSidToSid('S-1-3-4'))
            ro.AddAccessAllowedAceEx(ws.ACL_REVISION,flags,rights.FILE_ALL_ACCESS,user)
            ro.AddAccessAllowedAceEx(ws.ACL_REVISION,flags,rights.FILE_GENERIC_READ|rights.FILE_GENERIC_EXECUTE,ws.ConvertStringSidToSid(package))
            for p in [runtime] + list(runtime.rglob('*')):
                ws.SetNamedSecurityInfo(str(p),ws.SE_FILE_OBJECT,ws.DACL_SECURITY_INFORMATION|ws.PROTECTED_DACL_SECURITY_INFORMATION,None,None,ro,None)
            sddl = 'D:P(A;;FA;;;' + ws.ConvertSidToStringSid(user) + ')'
            cmd = subprocess.list2cmdline([str(base/'python.exe'),'-I','-S',str(script),str(deps),str(source),str(key),str(os.getpid()),sddl])
            result['python_runtime_probe'] = run('runtime',cmd)
            path = root/'runtime.out'
            try:
                data = r.load(path)
                result['runtime_canary'] = data
                result['network_and_scientific_runtime_verified'] = data.get('isolation_runtime_pass') is True and result['python_runtime_probe'].get('exit_code')==0
            except Exception:
                result['runtime_output_parse_failed'] = True
            result['mandatory_isolation_pass'] = result['filesystem_probe_pass'] and result['network_and_scientific_runtime_verified']
    finally:
        k.DeleteProcThreadAttributeList(buf)
        result['profile_cleanup_hresult'] = '0x%08x' % (api.DeleteAppContainerProfile(name) & 0xffffffff)
        free = c.WinDLL('advapi32').FreeSid
        free.argtypes = [c.c_void_p]
        free(sid)
    r.save(r.HERE / output_name(), result, True)
    print(result)


def output_name():
    if '--runtime' in sys.argv:
        return 'results/isolation/native_profile_runtime2.json' if '--quote-retry' in sys.argv else 'results/isolation/native_profile_runtime1.json'
    return 'results/isolation/native_profile_env1.json' if '--env-retry' in sys.argv else 'results/isolation/native_profile.json'


if __name__ == '__main__':
    main()
