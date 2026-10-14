"""Fresh process-local isolation assertions; synthetic only, never reads final keys."""
import ctypes as c
from ctypes import wintypes as w
import json
import socket


def check(source, key, hostpid, sddl):
    adv = c.WinDLL('advapi32', use_last_error=True)
    k = c.WinDLL('kernel32', use_last_error=True)
    k.GetCurrentProcess.restype = w.HANDLE
    adv.OpenProcessToken.argtypes = [w.HANDLE, w.DWORD, c.POINTER(w.HANDLE)]
    adv.GetTokenInformation.argtypes = [w.HANDLE, c.c_int, c.c_void_p, w.DWORD, c.POINTER(w.DWORD)]
    k.CloseHandle.argtypes = [w.HANDLE]
    token = w.HANDLE(); size = w.DWORD(); flag = w.DWORD()
    if not adv.OpenProcessToken(k.GetCurrentProcess(), 8, c.byref(token)):
        raise RuntimeError('NATIVE_TOKEN_QUERY_FAILED')
    try:
        if not adv.GetTokenInformation(token, 29, c.byref(flag), 4, c.byref(size)):
            raise RuntimeError('NATIVE_TOKEN_QUERY_FAILED')
        adv.GetTokenInformation(token, 30, None, 0, c.byref(size))
        capabilities = c.create_string_buffer(size.value)
        if not adv.GetTokenInformation(token, 30, capabilities, size.value, c.byref(size)):
            raise RuntimeError('NATIVE_CAPABILITIES_QUERY_FAILED')
        count = c.cast(capabilities, c.POINTER(w.DWORD)).contents.value
    finally:
        k.CloseHandle(token)
    result = dict(is_appcontainer=bool(flag.value), capability_count=count)
    for path, label in ((source, 'source_read_denied'), (key, 'key_read_denied')):
        try:
            with open(path, 'rb') as handle:
                handle.read(1)
            result[label] = False
        except PermissionError:
            result[label] = True
        except Exception:
            result[label] = False
    adv.ConvertStringSecurityDescriptorToSecurityDescriptorW.argtypes = [w.LPCWSTR, w.DWORD, c.POINTER(c.c_void_p), c.c_void_p]
    adv.SetFileSecurityW.argtypes = [w.LPCWSTR, w.DWORD, c.c_void_p]
    sd = c.c_void_p()
    if not adv.ConvertStringSecurityDescriptorToSecurityDescriptorW(sddl, 1, c.byref(sd), None):
        raise RuntimeError('NATIVE_CANARY_SDDL_FAILED')
    try:
        ok = adv.SetFileSecurityW(key, 4, sd)
        result['dacl_regrant_denied'] = not ok and c.get_last_error() == 5
    finally:
        k.LocalFree.argtypes = [c.c_void_p]; k.LocalFree(sd)
    connection = socket.socket(); connection.settimeout(3)
    try:
        result['network_status_code'] = connection.connect_ex(('1.1.1.1', 443))
        result['network_denied'] = result['network_status_code'] == 10013
    finally:
        connection.close()
    k.OpenProcess.argtypes = [w.DWORD, w.BOOL, w.DWORD]; k.OpenProcess.restype = w.HANDLE
    process = k.OpenProcess(0x10 | 0x1000, False, int(hostpid))
    result['custodian_memory_access_denied'] = not process and c.get_last_error() == 5
    if process:
        k.CloseHandle(process)
    result['pass'] = result['is_appcontainer'] and count == 0 and all(
        result[name] is True for name in ('source_read_denied', 'key_read_denied',
                                        'dacl_regrant_denied', 'network_denied',
                                        'custodian_memory_access_denied'))
    return result
