"""Real Windows token/DACL/network probes. Never reads experimental values."""
import ctypes
from ctypes import wintypes
import hashlib
import os
from pathlib import Path
import socket
import sys
import win32api
import win32security as ws
import ntsecuritycon as rights
import register as r

NETWORK_CAPS = {'S-1-15-3-1', 'S-1-15-3-2', 'S-1-15-3-3'}


class SidAttr(ctypes.Structure):
    _fields_ = [('sid', ctypes.c_void_p), ('attributes', wintypes.DWORD)]


class Groups(ctypes.Structure):
    _fields_ = [('count', wintypes.DWORD), ('first', SidAttr)]


def sid_text(pointer):
    api = ctypes.WinDLL('advapi32', use_last_error=True)
    api.ConvertSidToStringSidW.argtypes = [ctypes.c_void_p, ctypes.POINTER(wintypes.LPWSTR)]
    out = wintypes.LPWSTR()
    if not api.ConvertSidToStringSidW(pointer, ctypes.byref(out)):
        raise RuntimeError('TOKEN_SID_CONVERSION_FAILED')
    try:
        return out.value
    finally:
        kernel = ctypes.WinDLL('kernel32')
        kernel.LocalFree.argtypes = [ctypes.c_void_p]
        kernel.LocalFree(ctypes.cast(out, ctypes.c_void_p))


def token_info():
    api = ctypes.WinDLL('advapi32', use_last_error=True)
    api.GetTokenInformation.argtypes = [wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p,
                                       wintypes.DWORD, ctypes.POINTER(wintypes.DWORD)]
    token = ws.OpenProcessToken(win32api.GetCurrentProcess(), rights.TOKEN_QUERY)
    def query(kind):
        size = wintypes.DWORD()
        api.GetTokenInformation(int(token), kind, None, 0, ctypes.byref(size))
        if not size.value:
            raise RuntimeError('TOKEN_INFORMATION_UNAVAILABLE')
        buf = ctypes.create_string_buffer(size.value)
        if not api.GetTokenInformation(int(token), kind, buf, size.value, ctypes.byref(size)):
            raise RuntimeError('TOKEN_INFORMATION_FAILED')
        return buf
    flag = ctypes.cast(query(29), ctypes.POINTER(wintypes.DWORD)).contents.value
    buf = query(30)
    count = ctypes.cast(buf, ctypes.POINTER(wintypes.DWORD)).contents.value
    caps = [sid_text(SidAttr.from_address(ctypes.addressof(buf) + Groups.first.offset + i * ctypes.sizeof(SidAttr)).sid)
            for i in range(count)]
    user = ws.GetTokenInformation(token, ws.TokenUser)[0]
    identity = hashlib.sha256(ws.ConvertSidToStringSid(user).encode()).hexdigest()
    package = None
    if flag:
        package_buffer = query(31)
        package = sid_text(ctypes.cast(package_buffer, ctypes.POINTER(ctypes.c_void_p)).contents.value)
    return {'is_appcontainer': bool(flag), 'network_capability_present': bool(NETWORK_CAPS & set(caps)),
            'capability_count': count, 'capability_sids': caps, 'underlying_user_sid_sha256': identity,
            'package_sid': package}


def require_custodian():
    info = token_info()
    if info['is_appcontainer']:
        raise PermissionError('CUSTODIAN_ROLE_REQUIRED')
    return info


def protect(path, exact_package_sid=None):
    require_custodian()
    path = Path(path)
    if not path.resolve().is_relative_to(r.HERE.resolve()):
        raise RuntimeError('PROTECTION_PATH_OUTSIDE_MISSION')
    if path.exists() and os.lstat(path).st_file_attributes & 0x400:
        raise RuntimeError('REPARSE_POINT_FORBIDDEN')
    user = ws.GetTokenInformation(ws.OpenProcessToken(win32api.GetCurrentProcess(), rights.TOKEN_QUERY), ws.TokenUser)[0]
    dacl = ws.ACL()
    inherit = ws.OBJECT_INHERIT_ACE | ws.CONTAINER_INHERIT_ACE if path.is_dir() else 0
    for sid in ([exact_package_sid] if exact_package_sid else []) + ['S-1-15-2-1', 'S-1-15-2-2']:
        dacl.AddAccessDeniedAceEx(ws.ACL_REVISION, inherit, rights.FILE_ALL_ACCESS, ws.ConvertStringSidToSid(sid))
    # Remove implicit owner WRITE_DAC; explicit host-user grant remains.
    dacl.AddAccessAllowedAceEx(ws.ACL_REVISION, inherit, rights.READ_CONTROL, ws.ConvertStringSidToSid('S-1-3-4'))
    for sid in (user, ws.ConvertStringSidToSid('S-1-5-18')):
        dacl.AddAccessAllowedAceEx(ws.ACL_REVISION, inherit, rights.FILE_ALL_ACCESS, sid)
    ws.SetNamedSecurityInfo(str(path), ws.SE_FILE_OBJECT,
                           ws.DACL_SECURITY_INFORMATION | ws.PROTECTED_DACL_SECURITY_INFORMATION,
                           None, None, dacl, None)


def prepare(retry=False):
    r.verify()
    info = require_custodian()
    package = r.load(r.HERE / 'results/isolation/identity_retry.json')['token']['package_sid'] if retry else None
    private = r.HERE / ('.private/explicit_sid_retry' if retry else '.private')
    private.mkdir(exist_ok=True)
    protect(private, package)
    for name in ('synthetic_source.bin', 'synthetic_key.bin'):
        path = private / name
        with path.open('xb') as f:
            f.write(os.urandom(32))
        protect(path, package)
    result = {'token': info, 'protected_objects_created': 2,
              'host_source_positive_read': len((private / 'synthetic_source.bin').read_bytes()) == 32,
              'host_key_positive_read': len((private / 'synthetic_key.bin').read_bytes()) == 32,
              'synthetic_only': True, 'source_full_session_decoded_by_custodian': False,
              'final_values_exposed_to_analysis': False, 'final_holdout_evaluated': False}
    r.save(r.HERE / ('results/isolation/host_retry.json' if retry else 'results/isolation/host.json'), result, True)
    print({'host_appcontainer': info['is_appcontainer'], 'synthetic_only': True,
           'host_positive_reads': result['host_source_positive_read'] and result['host_key_positive_read']})


def analysis_probe(retry=False):
    r.verify()
    info = token_info()
    result = {'token': info, 'synthetic_only': True}
    private = r.HERE / ('.private/explicit_sid_retry' if retry else '.private')
    for name, key in [('synthetic_source.bin', 'source_read_denied'), ('synthetic_key.bin', 'key_read_denied')]:
        try:
            with (private / name).open('rb') as f:
                f.read(1)
            result[key] = False
        except PermissionError:
            result[key] = True
        except Exception:
            result[key] = None  # Missing file is not proof of access control.
    try:
        path = private / 'synthetic_key.bin'
        user = ws.GetTokenInformation(ws.OpenProcessToken(win32api.GetCurrentProcess(), rights.TOKEN_QUERY), ws.TokenUser)[0]
        dacl = ws.ACL()
        dacl.AddAccessAllowedAce(ws.ACL_REVISION, rights.FILE_ALL_ACCESS, user)
        ws.SetNamedSecurityInfo(str(path), ws.SE_FILE_OBJECT, ws.DACL_SECURITY_INFORMATION, None, None, dacl, None)
        result['dacl_regrant_denied'] = False
    except ws.error as exc:
        result['dacl_regrant_denied'] = exc.winerror == 5
    try:
        require_custodian()
        result['custodian_role_entry_denied'] = False
    except PermissionError:
        result['custodian_role_entry_denied'] = True
    s = socket.socket()
    s.settimeout(4)
    try:
        status = s.connect_ex(('1.1.1.1', 443))
        result['direct_ip_network_denied'] = status == 10013
        result['network_status_code'] = status
    finally:
        s.close()
    checks = [info['is_appcontainer'], not info['network_capability_present']]
    checks += [result[k] is True for k in ('source_read_denied', 'key_read_denied', 'dacl_regrant_denied',
                                         'custodian_role_entry_denied', 'direct_ip_network_denied')]
    result['isolation_probe_pass'] = all(checks)
    r.save(r.HERE / ('results/isolation/analysis_retry.json' if retry else 'results/isolation/analysis.json'), result, True)
    print({k: v for k, v in result.items() if k != 'token'})


if __name__ == '__main__':
    if sys.argv[1] == 'prepare':
        prepare()
    elif sys.argv[1] == 'analysis':
        analysis_probe()
    elif sys.argv[1] == 'identity-retry':
        r.verify()
        r.save(r.HERE / 'results/isolation/identity_retry.json', {'token': token_info(), 'synthetic_only': True}, True)
        print('Actual AppContainer package SID recorded; no keys/data printed')
    elif sys.argv[1] == 'prepare-retry':
        prepare(True)
    elif sys.argv[1] == 'analysis-retry':
        analysis_probe(True)
    else:
        raise RuntimeError('UNKNOWN_SECURITY_PROBE')
