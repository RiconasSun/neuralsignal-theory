"""Synthetic probe executed only inside a fresh native AppContainer."""
import ctypes as c
from ctypes import wintypes as w
import json
from pathlib import Path
import socket
import sys


def main():
    deps, source, key, hostpid, sddl = sys.argv[1:]
    sys.path.insert(0, deps)
    import numpy
    import scipy
    import h5py
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    result = {'runtime_imports_pass': True, 'synthetic_only': True, 'versions':
              {'numpy': numpy.__version__, 'scipy': scipy.__version__, 'h5py': h5py.__version__}}
    for path, label in ((source, 'source_read_denied'), (key, 'key_read_denied')):
        try:
            with open(path, 'rb') as f:
                f.read(1)
            result[label] = False
        except PermissionError:
            result[label] = True
        except Exception:
            result[label] = None
    adv = c.WinDLL('advapi32', use_last_error=True)
    sd = c.c_void_p()
    adv.ConvertStringSecurityDescriptorToSecurityDescriptorW.argtypes = [w.LPCWSTR,w.DWORD,c.POINTER(c.c_void_p),c.c_void_p]
    adv.SetFileSecurityW.argtypes = [w.LPCWSTR,w.DWORD,c.c_void_p]
    if not adv.ConvertStringSecurityDescriptorToSecurityDescriptorW(sddl,1,c.byref(sd),None):
        raise RuntimeError('SDDL_SETUP_FAILED')
    try:
        ok = adv.SetFileSecurityW(key,4,sd)
        result['dacl_regrant_denied'] = not ok and c.get_last_error() == 5
    finally:
        free = c.WinDLL('kernel32').LocalFree
        free.argtypes = [c.c_void_p]
        free(sd)
    s = socket.socket()
    s.settimeout(3)
    try:
        status = s.connect_ex(('1.1.1.1',443))
        result['network_status_code'] = status
        result['network_denied'] = status == 10013
    finally:
        s.close()
    k = c.WinDLL('kernel32',use_last_error=True)
    k.OpenProcess.argtypes = [w.DWORD,w.BOOL,w.DWORD]
    k.OpenProcess.restype = w.HANDLE
    handle = k.OpenProcess(0x10|0x1000,False,int(hostpid))
    result['custodian_memory_access_denied'] = not handle and c.get_last_error()==5
    if handle:
        k.CloseHandle.argtypes = [w.HANDLE]
        k.CloseHandle(handle)
    plain = numpy.arange(20,dtype='<i4').tobytes()
    fixture_key = AESGCM.generate_key(bit_length=256)
    encrypted = AESGCM(fixture_key).encrypt(b'\0'*12,plain,b'synthetic')
    result['aead_roundtrip_pass'] = AESGCM(fixture_key).decrypt(b'\0'*12,encrypted,b'synthetic')==plain
    result['isolation_runtime_pass'] = all(result.get(n) is True for n in (
        'runtime_imports_pass','source_read_denied','key_read_denied','dacl_regrant_denied','network_denied',
        'custodian_memory_access_denied','aead_roundtrip_pass'))
    print(json.dumps(result))


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        print(json.dumps({'runtime_imports_pass':False,'synthetic_only':True,'error_type':type(exc).__name__}))
        sys.exit(1)
