"""Bounded six-fixture native API diagnosis; never touches experimental data."""
import ctypes
import uuid
import win32file
import win32con
import pywintypes
import study as r
from history_guard import verify
from custody_security import prepare,protect,check_acl,require_custodian


def main():
    verify();require_custodian()
    root=prepare(r.HERE/'.private'/('replacement_probe_'+uuid.uuid4().hex));rows=[]
    kernel=ctypes.WinDLL('kernel32',use_last_error=True)
    kernel.ReplaceFileW.argtypes=[ctypes.c_wchar_p,ctypes.c_wchar_p,ctypes.c_wchar_p,ctypes.c_ulong,ctypes.c_void_p,ctypes.c_void_p]
    for method in ('MoveFileExW','ReplaceFileW'):
        for sharing in ('closed','shared_delete','no_delete_sharing'):
            trial=prepare(root/(method+'_'+sharing));source=trial/'source';target=trial/'target'
            source.write_bytes(b'synthetic-new');target.write_bytes(b'synthetic-old');protect(source);protect(target)
            check_acl(source);check_acl(target);handle=None
            if sharing!='closed':
                flags=win32con.FILE_SHARE_READ|win32con.FILE_SHARE_WRITE|(win32con.FILE_SHARE_DELETE if sharing=='shared_delete' else 0)
                handle=win32file.CreateFile(str(target),win32con.GENERIC_READ,flags,None,win32con.OPEN_EXISTING,0,None)
            try:
                if method=='MoveFileExW':
                    try:win32file.MoveFileEx(str(source),str(target),9);success=True;code=0
                    except pywintypes.error as exc:success=False;code=exc.winerror
                else:
                    success=bool(kernel.ReplaceFileW(str(target),str(source),None,0,None,None));code=0 if success else ctypes.get_last_error()
                rows.append(dict(method=method,sharing=sharing,success=success,winerror=code,
                    target_old_or_new=target.read_bytes() in (b'synthetic-old',b'synthetic-new'),source_acl_before_verified=True,
                    same_volume=source.parent.stat().st_dev==target.parent.stat().st_dev))
            finally:
                if handle:handle.Close()
    r.save(r.HERE/'results/replacement_probe.json',dict(rows=rows,registered_fixture_count=6,
        code_sha256=r.sha(r.HERE/'replacement_probe.py'),neural_source_requests=0),True)
    print(rows)


if __name__=='__main__':main()
