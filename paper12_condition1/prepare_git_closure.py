"""Exact changed paths and blob manifest; no Git mutation."""
import hashlib
import subprocess
from pathlib import Path
import study as r
def main():
    allowed=('paper12_condition1/','ops/evidence/2026-10-14/p12-m4-conditioning-optimizer-1/')
    paths=[p for p in subprocess.check_output(['git','ls-files','--others','--exclude-standard','-z'],cwd=r.ROOT).decode().split('\0') if p]
    if any(not p.startswith(allowed) for p in paths):raise RuntimeError('UNRELATED_NEWFILE')
    modified=[p for p in subprocess.check_output(['git','diff','--name-only','-z'],cwd=r.ROOT).decode().split('\0') if p]
    if modified!=['ops/daily-operations.md']:raise RuntimeError('UNRELATED_CHANGE')
    paths.append('ops/daily-operations.md');manifest=r.ROOT/'ops/evidence/2026-10-14/p12-m4-conditioning-optimizer-1/changed_files.json';selfpath=manifest.relative_to(r.ROOT).as_posix();paths.append(selfpath);paths=sorted(set(paths));entries=[]
    for name in paths:
        if name==selfpath:continue
        payload=(r.ROOT/name).read_bytes();entries.append({'path':name,'sha256':hashlib.sha256(payload).hexdigest(),'git_blob_sha1':hashlib.sha1(b'blob '+str(len(payload)).encode()+b'\0'+payload).hexdigest(),'bytes':len(payload)})
    r.save(manifest,{'base':r.BASE,'scientific_outcome':'OPTIMIZATION_INCONCLUSIVE','expected_changed_paths':paths,'changed_path_count':len(paths),'files_except_self':entries,'self_bound_by_actual_git_readback':True})
    target=Path(r'C:\Users\85993\.codex\visualizations\2026\10\13\01a13780-a5dc-7e01-8acc-80dd913c1489\paper12_condition1_stage.nul');target.write_bytes(('\0'.join(paths)+'\0').encode());print('EXACT_CHANGED_FILE_MANIFEST',len(paths),'pathspec',target,'SHA256',r.sha(manifest))
if __name__=='__main__':main()
