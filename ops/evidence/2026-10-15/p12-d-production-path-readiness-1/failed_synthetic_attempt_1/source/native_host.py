"""Actual zero-capability Windows processes and narrow, verified artifact ACLs."""
import ctypes as c
from ctypes import wintypes as w
import os
from pathlib import Path
import subprocess
import time
import win32api
import win32security as ws
import ntsecuritycon as rights
if __package__:
    from .common import new,sha
else:from common import new,sha

ROOT=Path(__file__).resolve().parents[1]
HERE=ROOT/'paper12_production1'
_runtime_packages={}

class SI(c.Structure):
    _fields_=[('cb',w.DWORD),('lpReserved',w.LPWSTR),('lpDesktop',w.LPWSTR),('lpTitle',w.LPWSTR),('dwX',w.DWORD),('dwY',w.DWORD),('dwXSize',w.DWORD),('dwYSize',w.DWORD),('dwXCountChars',w.DWORD),('dwYCountChars',w.DWORD),('dwFillAttribute',w.DWORD),('dwFlags',w.DWORD),('wShowWindow',w.WORD),('cbReserved2',w.WORD),('lpReserved2',c.c_void_p),('hStdInput',w.HANDLE),('hStdOutput',w.HANDLE),('hStdError',w.HANDLE)]
class SIX(c.Structure):_fields_=[('si',SI),('attributes',c.c_void_p)]
class PI(c.Structure):_fields_=[('process',w.HANDLE),('thread',w.HANDLE),('pid',w.DWORD),('tid',w.DWORD)]
class Caps(c.Structure):_fields_=[('sid',c.c_void_p),('capabilities',c.c_void_p),('count',w.DWORD),('reserved',w.DWORD)]

def user_sid():return ws.GetTokenInformation(ws.OpenProcessToken(win32api.GetCurrentProcess(),rights.TOKEN_QUERY),ws.TokenUser)[0]
def require_custodian():
    adv=c.WinDLL('advapi32',use_last_error=True);k=c.WinDLL('kernel32');k.GetCurrentProcess.restype=w.HANDLE
    adv.OpenProcessToken.argtypes=[w.HANDLE,w.DWORD,c.POINTER(w.HANDLE)];adv.GetTokenInformation.argtypes=[w.HANDLE,c.c_int,c.c_void_p,w.DWORD,c.POINTER(w.DWORD)]
    token=w.HANDLE();flag=w.DWORD();size=w.DWORD()
    if not adv.OpenProcessToken(k.GetCurrentProcess(),8,c.byref(token)):raise PermissionError('CUSTODIAN_TOKEN_QUERY')
    try:
        if not adv.GetTokenInformation(token,29,c.byref(flag),4,c.byref(size)) or flag.value:raise PermissionError('TRUSTED_HOST_REQUIRED')
    finally:k.CloseHandle.argtypes=[w.HANDLE];k.CloseHandle(token)

def checked(path):
    path=Path(path).absolute()
    if not path.is_relative_to(HERE) or '..' in path.parts:raise PermissionError('PRODUCTION_PATH_ESCAPE')
    for p in [path]+list(path.parents):
        if p.exists() and (getattr(p.lstat(),'st_file_attributes',0)&0x400 or p.is_symlink() or (p.is_file() and p.lstat().st_nlink!=1)):raise PermissionError('PRODUCTION_LINK_SUBSTITUTION')
        if p==HERE:break
    return path

def acl_for(path,packages=(),writable=False,private=False):
    flags=ws.OBJECT_INHERIT_ACE|ws.CONTAINER_INHERIT_ACE if Path(path).is_dir() else 0;acl=ws.ACL()
    if private:
        for sid in ('S-1-15-2-1','S-1-15-2-2'):acl.AddAccessDeniedAceEx(ws.ACL_REVISION,flags,rights.FILE_ALL_ACCESS,ws.ConvertStringSidToSid(sid))
    acl.AddAccessAllowedAceEx(ws.ACL_REVISION,flags,rights.READ_CONTROL,ws.ConvertStringSidToSid('S-1-3-4'))
    for sid in (user_sid(),ws.ConvertStringSidToSid('S-1-5-18')):acl.AddAccessAllowedAceEx(ws.ACL_REVISION,flags,rights.FILE_ALL_ACCESS,sid)
    allowed=rights.FILE_GENERIC_READ|rights.FILE_GENERIC_EXECUTE|(rights.FILE_GENERIC_WRITE if writable else 0)
    for sid in packages:acl.AddAccessAllowedAceEx(ws.ACL_REVISION,flags,allowed,ws.ConvertStringSidToSid(sid))
    return acl

def set_acl(path,acl):
    ws.SetNamedSecurityInfo(str(path),ws.SE_FILE_OBJECT,ws.DACL_SECURITY_INFORMATION|ws.PROTECTED_DACL_SECURITY_INFORMATION,None,None,acl,None)
    actual=ws.GetNamedSecurityInfo(str(path),ws.SE_FILE_OBJECT,ws.DACL_SECURITY_INFORMATION)
    a=actual.GetSecurityDescriptorDacl()
    if not actual.GetSecurityDescriptorControl()[0]&ws.SE_DACL_PROTECTED or [a.GetAce(i) for i in range(a.GetAceCount())]!=[acl.GetAce(i) for i in range(acl.GetAceCount())]:raise PermissionError('PRODUCTION_ACL_READBACK')

def protect(path):
    require_custodian();path=checked(path);set_acl(path,acl_for(path,private=True))
def assert_private(path):
    require_custodian();path=checked(path);expected=acl_for(path,private=True);actual=ws.GetNamedSecurityInfo(str(path),ws.SE_FILE_OBJECT,ws.DACL_SECURITY_INFORMATION);a=actual.GetSecurityDescriptorDacl()
    if not actual.GetSecurityDescriptorControl()[0]&ws.SE_DACL_PROTECTED or [a.GetAce(i) for i in range(a.GetAceCount())]!=[expected.GetAce(i) for i in range(expected.GetAceCount())]:raise PermissionError('AUTHORITY_PRIVATE_ACL')
def grant(path,package,writable=False,shared=False):
    require_custodian();path=checked(path)
    if '/exports/' not in str(path).replace('\\','/'):raise PermissionError('GRANT_OUTSIDE_REGISTERED_EXPORTS')
    packages=_runtime_packages.setdefault(str(path),set()) if shared else set()
    packages.add(package)
    for p in [path]+list(path.rglob('*')) if path.is_dir() else [path]:checked(p);set_acl(p,acl_for(p,sorted(packages),writable))

class NativeProcess:
    def __init__(self,job,role,data,code,runtime):
        try:self.initialize(job,role,data,code,runtime)
        except BaseException:
            if getattr(self,'launched',False):self.k.TerminateProcess(self.pi.process,97);self.k.WaitForSingleObject(self.pi.process,5000);self.k.CloseHandle(self.pi.thread);self.k.CloseHandle(self.pi.process)
            if getattr(self,'initialized',False):self.k.DeleteProcThreadAttributeList(self.buffer)
            if getattr(self,'sid',None) and self.sid.value:
                self.api.DeleteAppContainerProfile(self.name);adv=c.WinDLL('advapi32');adv.FreeSid.argtypes=[c.c_void_p];adv.FreeSid(self.sid)
            raise
    def initialize(self,job,role,data,code,runtime):
        require_custodian();self.job=checked(job);self.role=role;self.data=checked(data);self.code=checked(code);self.runtime=checked(runtime)
        self.name='P12Production.'+os.urandom(4).hex();self.work=self.job/'exports'/self.name;self.output=self.work/'output';self.output.mkdir(parents=True)
        self.api=c.WinDLL('userenv',use_last_error=True);self.k=c.WinDLL('kernel32',use_last_error=True);self.sid=c.c_void_p();self.pi=PI();self.initialized=False;self.launched=False;self.closed=False
        self.api.CreateAppContainerProfile.argtypes=[w.LPCWSTR,w.LPCWSTR,w.LPCWSTR,c.c_void_p,w.DWORD,c.POINTER(c.c_void_p)];self.api.CreateAppContainerProfile.restype=c.c_long;self.api.DeleteAppContainerProfile.argtypes=[w.LPCWSTR];self.api.DeleteAppContainerProfile.restype=c.c_long
        if self.api.CreateAppContainerProfile(self.name,self.name,'Synthetic production readiness only',None,0,c.byref(self.sid))!=0:raise RuntimeError('PRODUCTION_PROFILE_CREATE')
        adv=c.WinDLL('advapi32');adv.ConvertSidToStringSidW.argtypes=[c.c_void_p,c.POINTER(w.LPWSTR)];txt=w.LPWSTR()
        if not adv.ConvertSidToStringSidW(self.sid,c.byref(txt)):raise RuntimeError('PROFILE_SID_STRING')
        self.package=txt.value;self.k.LocalFree.argtypes=[c.c_void_p];self.k.LocalFree(c.cast(txt,c.c_void_p))
        self.k.InitializeProcThreadAttributeList.argtypes=[c.c_void_p,w.DWORD,w.DWORD,c.POINTER(c.c_size_t)];self.k.UpdateProcThreadAttribute.argtypes=[c.c_void_p,w.DWORD,c.c_size_t,c.c_void_p,c.c_size_t,c.c_void_p,c.c_void_p];self.k.DeleteProcThreadAttributeList.argtypes=[c.c_void_p]
        self.k.CreateProcessW.argtypes=[w.LPCWSTR,w.LPWSTR,c.c_void_p,c.c_void_p,w.BOOL,w.DWORD,c.c_void_p,w.LPCWSTR,c.POINTER(SIX),c.POINTER(PI)]
        self.k.ResumeThread.argtypes=[w.HANDLE];self.k.WaitForSingleObject.argtypes=[w.HANDLE,w.DWORD];self.k.CloseHandle.argtypes=[w.HANDLE];self.k.TerminateProcess.argtypes=[w.HANDLE,w.UINT];self.k.GetExitCodeProcess.argtypes=[w.HANDLE,c.POINTER(w.DWORD)]
        size=c.c_size_t();self.k.InitializeProcThreadAttributeList(None,1,0,c.byref(size));self.buffer=c.create_string_buffer(size.value)
        if not self.k.InitializeProcThreadAttributeList(self.buffer,1,0,c.byref(size)):raise RuntimeError('NATIVE_ATTRIBUTE_INIT')
        self.initialized=True;self.caps=Caps(self.sid,None,0,0)
        if not self.k.UpdateProcThreadAttribute(self.buffer,0,0x20009,c.byref(self.caps),c.sizeof(self.caps),None,None):raise RuntimeError('ZERO_CAPABILITY_ATTRIBUTE')
        grant(self.work,self.package);grant(self.output,self.package,True);grant(self.code,self.package);grant(self.data,self.package);grant(self.runtime,self.package,shared=True)
        environment={key:os.environ[key] for key in ('SystemRoot','WINDIR','SystemDrive','USERPROFILE','LOCALAPPDATA','APPDATA','ProgramData','COMSPEC') if key in os.environ}
        environment.update(PATH=os.environ['SystemRoot']+'\\System32',TEMP=str(self.output),TMP=str(self.output),OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
        self.environment=c.create_unicode_buffer('\0'.join(k+'='+environment[k] for k in sorted(environment,key=str.upper))+'\0\0')
        self.sddl='D:P(A;;FA;;;'+ws.ConvertSidToStringSid(user_sid())+')';self.started=time.monotonic()
        exe=self.runtime/'base/python.exe';args=[str(exe),'-I','-S','-B',str(self.code/'worker.py'),str(self.runtime/'deps'),str(self.data),str(self.output),str(self.job/'.private/source_canary.bin'),str(self.job/'.private/key_canary.bin'),str(os.getpid()),self.sddl]
        self.command=args;info=SIX();info.si.cb=c.sizeof(SIX);info.si.dwFlags=1;info.si.wShowWindow=0;info.attributes=c.addressof(self.buffer)
        if not self.k.CreateProcessW(str(exe),c.create_unicode_buffer(subprocess.list2cmdline(args)),None,None,False,0x80000|4|0x8000000|0x400,self.environment,str(self.output),c.byref(info),c.byref(self.pi)):raise RuntimeError('PRODUCTION_CREATEPROCESS:'+str(c.get_last_error()))
        self.launched=True
    def resume(self):
        if not getattr(self,'resumed',False):
            if self.k.ResumeThread(self.pi.thread)==0xffffffff:raise RuntimeError('NATIVE_RESUME_FAILED')
            self.resumed=True
    def poll(self):
        value=w.DWORD();self.k.GetExitCodeProcess(self.pi.process,c.byref(value));return None if value.value==259 else value.value
    def wait(self,timeout=43200):
        end=time.monotonic()+timeout
        while self.poll() is None and time.monotonic()<end:self.k.WaitForSingleObject(self.pi.process,1000)
        if self.poll() is None:self.k.TerminateProcess(self.pi.process,99);self.k.WaitForSingleObject(self.pi.process,5000);raise TimeoutError('FROZEN_NATIVE_WALL_LIMIT')
        return self.poll()
    def close(self):
        if self.closed:return
        exit_code=self.poll() if self.launched else None
        if self.launched:
            if exit_code is None:self.k.TerminateProcess(self.pi.process,98);self.k.WaitForSingleObject(self.pi.process,5000)
            self.k.CloseHandle(self.pi.thread);self.k.CloseHandle(self.pi.process)
        if self.initialized:self.k.DeleteProcThreadAttributeList(self.buffer)
        cleanup='0x%08x'%(self.api.DeleteAppContainerProfile(self.name)&0xffffffff);adv=c.WinDLL('advapi32');adv.FreeSid.argtypes=[c.c_void_p];adv.FreeSid(self.sid);self.closed=True
        new(self.job/('native_'+self.role+'_receipt.json'),{'role':self.role,'package_sid':self.package,'pid':self.pi.pid,'command':self.command,'exit_code':exit_code,'elapsed_seconds':time.monotonic()-self.started,'profile_cleanup_hresult':cleanup,'output':str(self.output),'declared_realm':getattr(self,'realm','UNVERIFIED'),'operation_status':'Consult durable consumption and assessment-start/completion records; process exit alone proves no absence of access'})
        if cleanup!='0x00000000':raise RuntimeError('APPCONTAINER_PROFILE_CLEANUP')

def hold_process(pid):
    # Keep the original reviewed held-handle implementation, with only its native
    # custodian dependency resolved to this package's actual-token check.
    import contextlib,types,ast
    path=ROOT/'paper12_controls1/broker.py';reg=__import__('json').loads((ROOT/'ops/evidence/2026-10-15/p12-d-production-path-readiness-1/registration.json').read_text())
    if sha(path)!=reg['source_sha256']['paper12_controls1/broker.py']:raise PermissionError('FROZEN_HELD_PROCESS_SOURCE')
    tree=ast.parse(path.read_text());fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='hold_process')
    original_import=__import__('builtins').__import__
    def route(name,globals=None,locals=None,fromlist=(),level=0):
        if name=='native':return types.SimpleNamespace(security=lambda:types.SimpleNamespace(require_custodian=require_custodian))
        return original_import(name,globals,locals,fromlist,level)
    namespace={'c':c,'w':w,'contextmanager':contextlib.contextmanager,'__builtins__':dict(vars(__import__('builtins')),__import__=route)}
    exec(compile(ast.fix_missing_locations(ast.Module(body=[fn],type_ignores=[])),str(path),'exec'),namespace)
    return namespace['hold_process'](pid)
