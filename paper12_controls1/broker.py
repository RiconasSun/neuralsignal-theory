"""Trusted host verifier. Holds actual process handle; never grants a real D key."""
import ctypes as c
from ctypes import wintypes as w
from contextlib import contextmanager
from release_control import canonical,digest,read_json,verify_approval

@contextmanager
def hold_process(pid):
    import win32api,win32security as ws
    from native import security
    security().require_custodian()
    k=c.WinDLL('kernel32',use_last_error=True);adv=c.WinDLL('advapi32',use_last_error=True)
    k.OpenProcess.argtypes=[w.DWORD,w.BOOL,w.DWORD];k.OpenProcess.restype=w.HANDLE
    handle=k.OpenProcess(0x1000|0x100000,False,pid)
    if not handle:raise PermissionError('TARGET_PROCESS_UNAVAILABLE')
    token=None
    try:
        token=ws.OpenProcessToken(int(handle),8)
        adv.GetTokenInformation.argtypes=[w.HANDLE,c.c_int,c.c_void_p,w.DWORD,c.POINTER(w.DWORD)]
        def query(kind):
            size=w.DWORD();adv.GetTokenInformation(int(token),kind,None,0,c.byref(size));buf=c.create_string_buffer(size.value)
            if not adv.GetTokenInformation(int(token),kind,buf,size.value,c.byref(size)):raise PermissionError('TARGET_TOKEN_QUERY')
            return buf
        if not c.cast(query(29),c.POINTER(w.DWORD)).contents.value or c.cast(query(30),c.POINTER(w.DWORD)).contents.value:raise PermissionError('TARGET_ZERO_CAP_APPCONTAINER_REQUIRED')
        sidbuf=query(31);ptr=c.cast(sidbuf,c.POINTER(c.c_void_p)).contents.value
        adv.ConvertSidToStringSidW.argtypes=[c.c_void_p,c.POINTER(w.LPWSTR)];sid=w.LPWSTR()
        if not adv.ConvertSidToStringSidW(ptr,c.byref(sid)):raise PermissionError('TARGET_PACKAGE_QUERY')
        package=sid.value;k.LocalFree.argtypes=[c.c_void_p];k.LocalFree(c.cast(sid,c.c_void_p))
        times=[w.FILETIME() for _ in range(4)];k.GetProcessTimes.argtypes=[w.HANDLE,*([c.POINTER(w.FILETIME)]*4)]
        if not k.GetProcessTimes(handle,*[c.byref(x) for x in times]):raise PermissionError('TARGET_CREATION_QUERY')
        creation=(times[0].dwHighDateTime<<32)|times[0].dwLowDateTime
        identity={'package_sid':package,'pid':pid,'creation_identity':str(creation)}
        def verify(expected):
            status=w.DWORD();k.GetExitCodeProcess.argtypes=[w.HANDLE,c.POINTER(w.DWORD)]
            if expected!=identity or not k.GetExitCodeProcess(handle,c.byref(status)) or status.value!=259:raise PermissionError('TARGET_IDENTITY_OR_LIVENESS_CHANGED')
            return identity
        verify(identity);yield identity,verify
    finally:
        if token is not None:token.Close()
        k.CloseHandle.argtypes=[w.HANDLE];k.CloseHandle(handle)

def synthetic_capability(receipt,approval,anchor,binding_root,ledger,verify_target,target_directory):
    # This engineering broker cannot route a synthetic entitlement to a real-D realm.
    from pathlib import Path
    if receipt['realm']!='SYNTHETIC_D' or anchor['realm']!='SYNTHETIC_D':raise PermissionError('NO_REAL_D_AUTHORIZATION_IN_ENGINEERING')
    body=verify_approval(approval,anchor,binding_root);verify_target(body['principal'])
    if receipt['principal']!=body['principal'] or receipt['authorization_id']!=body['authorization_id'] or receipt['binding']!=digest(canonical(body)):raise PermissionError('RECEIPT_BINDING')
    used=read_json(Path(ledger)/'consumed.json');intent=read_json(Path(ledger)/'intent.json')
    if used['binding']!=receipt['binding'] or used['ledger_tail']!=receipt['ledger_tail'] or intent['binding']!=receipt['binding']:raise PermissionError('DURABLE_CONSUMPTION_REQUIRED')
    lines=(Path(ledger)/'events.jsonl').read_bytes().splitlines();previous=anchor['genesis_sha256']
    for i,line in enumerate(lines):
        event=__import__('json').loads(line)
        if event['sequence']!=i or event['previous']!=previous:raise PermissionError('BROKER_LEDGER_CHAIN')
        previous=digest(canonical(event))
    if previous!=receipt['ledger_tail'] or len(lines)!=3:raise PermissionError('BROKER_CONSUMPTION_TAIL')
    verify_target(body['principal'])
    capability=Path(target_directory)/'synthetic_released_canary.bin'
    # Exclusive creation also denies a duplicate broker grant after valid consumption.
    with capability.open('xb') as f:f.write(b'SYNTHETIC_D_CAPABILITY_ONLY_AFTER_DURABLE_CONSUMPTION');f.flush();__import__('os').fsync(f.fileno())
    return digest(capability.read_bytes())
