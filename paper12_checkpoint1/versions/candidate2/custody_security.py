"""Reuse immutable custody DACL/token policy, restricted to new synthetic study."""
import sys
import os
import types
from pathlib import Path
import study as r
sys.path.insert(0,str(r.ROOT/'paper12_custody1'))
import security as archived
import win32security as ws
import ntsecuritycon as rights
globals_copy=dict(archived.protect.__globals__)
globals_copy['r']=types.SimpleNamespace(HERE=r.HERE)


def native_path(path):
    value=str(Path(path).absolute())
    if value.startswith('\\\\?\\'):return value
    if value.startswith('\\\\'):return '\\\\?\\UNC\\'+value[2:]
    return '\\\\?\\'+value


def set_security(path,*args):return ws.SetNamedSecurityInfo(native_path(path),*args)


native_ws=types.SimpleNamespace(**vars(ws))
native_ws.SetNamedSecurityInfo=set_security
globals_copy['ws']=native_ws
protect=types.FunctionType(archived.protect.__code__,globals_copy,argdefs=archived.protect.__defaults__)
require_custodian=archived.require_custodian


def check_path(path):
    path=Path(path).absolute()
    if '..' in path.parts:raise RuntimeError('PATH_TRAVERSAL_FORBIDDEN')
    if not path.is_relative_to(r.HERE.absolute()):raise RuntimeError('OUTSIDE_SYNTHETIC_STUDY')
    for ancestor in [path]+list(path.parents):
        if os.path.lexists(ancestor):
            attributes=ancestor.lstat().st_file_attributes
            if attributes&0x400:raise RuntimeError('REPARSE_POINT_FORBIDDEN')
        if ancestor==r.HERE:break
    if not path.resolve(strict=False).is_relative_to(r.HERE.resolve()):raise RuntimeError('CANONICAL_SCOPE_ESCAPE')
    return path


def check_acl(path):
    path=check_path(path)
    sd=ws.GetNamedSecurityInfo(native_path(path),ws.SE_FILE_OBJECT,ws.DACL_SECURITY_INFORMATION)
    if not sd.GetSecurityDescriptorControl()[0]&ws.SE_DACL_PROTECTED:raise RuntimeError('UNPROTECTED_DACL')
    actual=[]
    acl=sd.GetSecurityDescriptorDacl()
    for i in range(acl.GetAceCount()):
        header,mask,sid=acl.GetAce(i);actual.append((header,mask,ws.ConvertSidToStringSid(sid)))
    user=ws.GetTokenInformation(ws.OpenProcessToken(archived.win32api.GetCurrentProcess(),rights.TOKEN_QUERY),ws.TokenUser)[0]
    flags=ws.OBJECT_INHERIT_ACE|ws.CONTAINER_INHERIT_ACE if path.is_dir() else 0
    expected=[((1,flags),rights.FILE_ALL_ACCESS,sid) for sid in ('S-1-15-2-1','S-1-15-2-2')]
    expected+=[((0,flags),rights.READ_CONTROL,'S-1-3-4')]
    expected+=[((0,flags),rights.FILE_ALL_ACCESS,ws.ConvertSidToStringSid(user)),((0,flags),rights.FILE_ALL_ACCESS,'S-1-5-18')]
    if actual!=expected:raise RuntimeError('CUSTODY_DACL_MISMATCH')
    if path.lstat().st_file_attributes&1:raise RuntimeError('READONLY_CHECKPOINT_FORBIDDEN')


def prepare(root):
    require_custodian();root=check_path(root)
    root.mkdir(parents=True,exist_ok=True);protect(root);check_acl(root)
    return root
