"""Actual Windows open-access checks without reading any protected bytes."""
import ctypes as c
from ctypes import wintypes as w
def denied_open(path):
    k=c.WinDLL('kernel32',use_last_error=True)
    k.CreateFileW.argtypes=[w.LPCWSTR,w.DWORD,w.DWORD,c.c_void_p,w.DWORD,w.DWORD,w.HANDLE];k.CreateFileW.restype=w.HANDLE
    handle=k.CreateFileW(str(path),0x80000000,7,None,3,0x80,None)
    if handle==w.HANDLE(-1).value:return c.get_last_error()==5
    k.CloseHandle.argtypes=[w.HANDLE];k.CloseHandle(handle)
    return False
