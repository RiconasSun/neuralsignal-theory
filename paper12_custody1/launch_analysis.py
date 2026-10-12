"""Trusted native-role launcher. Direct Python child, no inherited handles/network caps."""
import ctypes as c
from ctypes import wintypes as w
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
import win32api
import win32security as ws
import ntsecuritycon as rights
import register as r
import custodian
from security import sid_text


class SI(c.Structure):
    _fields_ = [('cb', w.DWORD), ('lpReserved', w.LPWSTR), ('lpDesktop', w.LPWSTR), ('lpTitle', w.LPWSTR),
                ('dwX', w.DWORD), ('dwY', w.DWORD), ('dwXSize', w.DWORD), ('dwYSize', w.DWORD),
                ('dwXCountChars', w.DWORD), ('dwYCountChars', w.DWORD), ('dwFillAttribute', w.DWORD),
                ('dwFlags', w.DWORD), ('wShowWindow', w.WORD), ('cbReserved2', w.WORD),
                ('lpReserved2', c.c_void_p), ('hStdInput', w.HANDLE), ('hStdOutput', w.HANDLE), ('hStdError', w.HANDLE)]


class SIX(c.Structure):
    _fields_ = [('si', SI), ('attributes', c.c_void_p)]


class PI(c.Structure):
    _fields_ = [('process', w.HANDLE), ('thread', w.HANDLE), ('pid', w.DWORD), ('tid', w.DWORD)]


class Caps(c.Structure):
    _fields_ = [('sid', c.c_void_p), ('capabilities', c.c_void_p), ('count', w.DWORD), ('reserved', w.DWORD)]


def grant(root, user, package, writable=False):
    root = Path(root)
    if not root.resolve().is_relative_to((r.HERE / 'exports').resolve()):
        raise PermissionError('ANALYSIS_GRANT_OUTSIDE_MISSION_EXPORTS')
    acl = ws.ACL(); flags = ws.OBJECT_INHERIT_ACE | ws.CONTAINER_INHERIT_ACE
    acl.AddAccessAllowedAceEx(ws.ACL_REVISION, flags, rights.READ_CONTROL, ws.ConvertStringSidToSid('S-1-3-4'))
    acl.AddAccessAllowedAceEx(ws.ACL_REVISION, flags, rights.FILE_ALL_ACCESS, user)
    allowed = rights.FILE_GENERIC_READ | rights.FILE_GENERIC_EXECUTE
    if writable:
        allowed |= rights.FILE_GENERIC_WRITE
    acl.AddAccessAllowedAceEx(ws.ACL_REVISION, flags, allowed, ws.ConvertStringSidToSid(package))
    for path in [root] + list(root.rglob('*')):
        if os.lstat(path).st_file_attributes & 0x400:
            raise PermissionError('ANALYSIS_REPARSE_POINT_FORBIDDEN')
        ws.SetNamedSecurityInfo(str(path), ws.SE_FILE_OBJECT,
                                ws.DACL_SECURITY_INFORMATION | ws.PROTECTED_DACL_SECURITY_INFORMATION,
                                None, None, acl, None)


def main():
    custodian.check_gate()
    registration = r.load(r.HERE / 'development_registration.json')
    for name, digest in registration['implementation_sha256'].items():
        if r.sha(r.HERE / name) != digest:
            raise PermissionError('ANALYSIS_IMPLEMENTATION_CHANGED')
    security_only = '--security-only' in sys.argv
    if not security_only and r.load(r.HERE / 'results/M2/aggregate4/gate_result.json')['gate'] != 'PASS':
        raise PermissionError('FULL_M2_GATE_REQUIRED')
    data = r.HERE / 'exports/development1'
    if not security_only:
        manifest = r.load(data / 'manifest.json')
        method = r.load(r.HERE / 'M3_METHOD_DECISION1.json')
        method_registration = r.load(r.HERE / 'method_registration1.json')
        if manifest['method_decision_sha256'] != r.sha(r.HERE / 'M3_METHOD_DECISION1.json') or method_registration['method_sha256'] != manifest['method_decision_sha256'] or method_registration['implementation_registration_sha256'] != r.sha(r.HERE / 'development_registration.json') or manifest['ridge_normalization'] != method['ridge_normalization']:
            raise PermissionError('PROSPECTIVE_METHOD_BINDING_FAILED')
        from manifest_validation import validate_manifest
        old = r.ROOT / 'paper12_curated_v1'
        animals = r.load(old / 'locks/animals.json')
        qc = {a['session_id']: r.load(r.HERE / 'results/M2/index2/sessions' / (a['session_id'] + '.json'))
              for a in animals if a['group'] == 'development'}
        validate_manifest(manifest, animals, qc, r.sha(r.HERE / 'results/M2/aggregate4/gate_result.json'),
                          r.sha(r.HERE / 'development_registration.json'))
        issuer = r.load(r.HERE / '.private/development_export_issuer.json')
        if issuer != dict(manifest_sha256=r.sha(data / 'manifest.json'), M2_gate_sha256=manifest['M2_gate_sha256'],
                          development_registration_sha256=manifest['development_registration_sha256'],
                          method_decision_sha256=manifest['method_decision_sha256']):
            raise PermissionError('PROTECTED_EXPORT_ISSUER_BINDING_FAILED')
        all_trials = r.load(old / 'locks/trials.json'); all_units = r.load(old / 'locks/units.json')
        for session in manifest['sessions']:
            if Path(session['file']).name != session['file'] or r.sha(data / session['file']) != session['sha256']:
                raise PermissionError('INPUT_INTEGRITY_FAILED')
            sid = session['session_id']
            for compartment, partition in (('A', 'train'), ('B', 'validation')):
                expected_trials = [t['trial_id'] for t in all_trials if t['session_id'] == sid and
                                   t['partition'] == partition and t['metadata_admitted']]
                if session['trial_ids'][compartment] != expected_trials:
                    raise PermissionError('FROZEN_TRIAL_EXPORT_MISMATCH')
            for region in ('CA1', 'DG'):
                ids = session['unit_ids'][region]
                allowed = {u['unit_id'] for u in all_units if u['session_id'] == sid and u['subfield'] == region}
                if len(ids) != len(set(ids)) or not 5 <= len(ids) <= 32 or not set(ids) <= allowed:
                    raise PermissionError('FROZEN_UNIT_EXPORT_MISMATCH')
    user = ws.GetTokenInformation(ws.OpenProcessToken(win32api.GetCurrentProcess(), rights.TOKEN_QUERY), ws.TokenUser)[0]
    api = c.WinDLL('userenv', use_last_error=True)
    api.CreateAppContainerProfile.argtypes = [w.LPCWSTR, w.LPCWSTR, w.LPCWSTR, c.c_void_p, w.DWORD, c.POINTER(c.c_void_p)]
    api.CreateAppContainerProfile.restype = c.c_long
    api.DeleteAppContainerProfile.argtypes = [w.LPCWSTR]; api.DeleteAppContainerProfile.restype = c.c_long
    sid = c.c_void_p(); name = 'P12Analysis.' + os.urandom(8).hex()
    if api.CreateAppContainerProfile(name, name, 'Registered P12 development only', None, 0, c.byref(sid)) != 0:
        raise RuntimeError('ANALYSIS_PROFILE_CREATION_FAILED')
    k = c.WinDLL('kernel32', use_last_error=True)
    k.InitializeProcThreadAttributeList.argtypes = [c.c_void_p, w.DWORD, w.DWORD, c.POINTER(c.c_size_t)]
    k.UpdateProcThreadAttribute.argtypes = [c.c_void_p, w.DWORD, c.c_size_t, c.c_void_p, c.c_size_t, c.c_void_p, c.c_void_p]
    k.DeleteProcThreadAttributeList.argtypes = [c.c_void_p]
    k.CreateProcessW.argtypes = [w.LPCWSTR, w.LPWSTR, c.c_void_p, c.c_void_p, w.BOOL, w.DWORD,
                                c.c_void_p, w.LPCWSTR, c.POINTER(SIX), c.POINTER(PI)]
    k.ResumeThread.argtypes = [w.HANDLE]; k.WaitForSingleObject.argtypes = [w.HANDLE, w.DWORD]
    k.CloseHandle.argtypes = [w.HANDLE]; k.TerminateProcess.argtypes = [w.HANDLE, w.UINT]
    k.GetExitCodeProcess.argtypes = [w.HANDLE, c.POINTER(w.DWORD)]
    size = c.c_size_t(); k.InitializeProcThreadAttributeList(None, 1, 0, c.byref(size))
    buffer = c.create_string_buffer(size.value); initialized = False; launched = False; pi = PI()
    receipt = dict(scope='Synthetic native prerequisite only' if security_only else 'Development M3 baselines only',
                   synthetic_only=security_only, final_values_exposed_to_analysis=False,
                   final_holdout_evaluated=False, profile_created=True)
    try:
        package = sid_text(sid)
        job = r.HERE / 'exports' / name
        code = job / 'code'; output = job / 'output'
        code.mkdir(parents=True); output.mkdir()
        if security_only:
            data = job / 'synthetic_empty_input'; data.mkdir()
        for filename in ('analysis_worker.py', 'baseline_features.py', 'baseline_fit.py', 'native_analysis_check.py',
                         'test_baseline_features.py', 'test_baseline_fit.py'):
            shutil.copy2(r.HERE / filename, code / filename)
        runtime = r.HERE / 'exports/native_probe/runtime'
        grant(job, user, package); grant(code, user, package)
        grant(runtime, user, package); grant(data, user, package); grant(output, user, package, True)
        initialized = bool(k.InitializeProcThreadAttributeList(buffer, 1, 0, c.byref(size)))
        if not initialized:
            raise RuntimeError('ANALYSIS_ATTRIBUTE_INIT_FAILED')
        capabilities = Caps(sid, None, 0, 0)
        if not k.UpdateProcThreadAttribute(buffer, 0, 0x20009, c.byref(capabilities), c.sizeof(capabilities), None, None):
            raise RuntimeError('ANALYSIS_CAPABILITIES_FAILED')
        whitelist = ('SystemRoot', 'WINDIR', 'SystemDrive', 'USERPROFILE', 'LOCALAPPDATA', 'APPDATA', 'ProgramData', 'COMSPEC')
        environment = {key: os.environ[key] for key in whitelist if key in os.environ}
        environment.update(PATH=os.environ['SystemRoot'] + '\\System32', TEMP=str(output), TMP=str(output),
                           OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1')
        env = c.create_unicode_buffer('\0'.join(key + '=' + environment[key] for key in sorted(environment, key=str.upper)) + '\0\0')
        exe = runtime / 'base/python.exe'
        sddl = 'D:P(A;;FA;;;' + ws.ConvertSidToStringSid(user) + ')'
        args = [str(exe), '-I', '-S', str(code / 'analysis_worker.py'), str(runtime / 'deps'),
                str(data), str(output), str(r.HERE / '.private/native_probe_source.bin'),
                str(r.HERE / '.private/native_probe_key.bin'), str(os.getpid()), sddl]
        if security_only:
            args.append('--security-only')
        command = c.create_unicode_buffer(subprocess.list2cmdline(args))
        info = SIX(); info.si.cb = c.sizeof(SIX); info.si.dwFlags = 1; info.si.wShowWindow = 0
        info.attributes = c.addressof(buffer)
        launched = bool(k.CreateProcessW(str(exe), command, None, None, False,
                                        0x80000 | 4 | 0x8000000 | 0x400, env, str(output), c.byref(info), c.byref(pi)))
        if not launched:
            raise RuntimeError('ANALYSIS_PROCESS_CREATE_FAILED:%d' % c.get_last_error())
        receipt['process_id'] = pi.pid
        k.ResumeThread(pi.thread)
        start = time.monotonic(); status = 258
        while status == 258 and time.monotonic() - start < 43200:
            status = k.WaitForSingleObject(pi.process, 30000)
        if status == 258:
            k.TerminateProcess(pi.process, 99); k.WaitForSingleObject(pi.process, 5000)
        exit_code = w.DWORD(); k.GetExitCodeProcess(pi.process, c.byref(exit_code))
        receipt.update(exit_code=exit_code.value, elapsed_seconds=time.monotonic() - start,
                       timed_out=status == 258, output_directory=str(output.relative_to(r.HERE)))
        # Only public metrics/proof receipts are copied. No unrestricted input export.
        public = r.HERE / ('results/M3/synthetic_native1' if security_only else 'results/M3/native1')
        public.mkdir(parents=True, exist_ok=False)
        for path in output.glob('*.json'):
            shutil.copy2(path, public / path.name)
        receipt['role_proof_pass'] = r.load(public / 'role_proof.json')['pass'] if (public / 'role_proof.json').exists() else False
        receipt['M3_gate'] = r.load(public / 'gate_result.json')['gate'] if (public / 'gate_result.json').exists() else 'NOT_COMPLETE'
    finally:
        if launched:
            if k.WaitForSingleObject(pi.process, 0) == 258:
                k.TerminateProcess(pi.process, 98); k.WaitForSingleObject(pi.process, 5000)
            k.CloseHandle(pi.thread); k.CloseHandle(pi.process)
        if initialized:
            k.DeleteProcThreadAttributeList(buffer)
        receipt['profile_cleanup_hresult'] = '0x%08x' % (api.DeleteAppContainerProfile(name) & 0xffffffff)
        adv = c.WinDLL('advapi32'); adv.FreeSid.argtypes = [c.c_void_p]; adv.FreeSid(sid)
        r.save(r.HERE / ('results/M3/synthetic_native_launch_receipt.json' if security_only else
                        'results/M3/native_launch_receipt.json'), receipt, True)
    print(receipt)


if __name__ == '__main__':
    main()
