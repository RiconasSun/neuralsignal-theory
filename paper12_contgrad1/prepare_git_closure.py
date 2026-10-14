"""Exact candidate path/blob manifest and NUL pathspec, no Git mutation."""
import hashlib
import subprocess
from pathlib import Path
import study as r

def main():
    allowed=('paper12_contgrad1/','ops/evidence/2026-10-13/p12-m4-continuous-gradient-diag-1/')
    raw=subprocess.check_output(['git','ls-files','--others','--exclude-standard','-z'],cwd=r.ROOT).decode().split('\0')
    paths=[p for p in raw if p]
    if any(not p.startswith(allowed) for p in paths):raise RuntimeError('UNRELATED_UNTRACKED_FILE')
    modified=subprocess.check_output(['git','diff','--name-only','-z'],cwd=r.ROOT).decode().split('\0')
    if [p for p in modified if p]!=['ops/daily-operations.md']:raise RuntimeError('UNRELATED_MODIFICATION')
    paths.append('ops/daily-operations.md')
    output=r.ROOT/'ops/evidence/2026-10-13/p12-m4-continuous-gradient-diag-1/changed_files.json'
    paths.append(output.relative_to(r.ROOT).as_posix())
    paths=sorted(set(paths));entries=[]
    for p in paths:
        if p==output.relative_to(r.ROOT).as_posix():continue
        payload=(r.ROOT/p).read_bytes()
        entries.append({'path':p,'sha256':hashlib.sha256(payload).hexdigest(),'git_blob_sha1':hashlib.sha1(b'blob '+str(len(payload)).encode()+b'\0'+payload).hexdigest(),'bytes':len(payload)})
    r.save(output,{'base':r.BASE,'expected_changed_paths':paths,'changed_path_count':len(paths),'files_except_self':entries,'self_digest_bound_by_final_git_readback':True,'exact_staging_only':True})
    target=Path(r'C:\Users\85993\.codex\visualizations\2026\10\13\01a13780-a5dc-7e01-8acc-80dd913c1489\paper12_contgrad1_stage.nul')
    target.write_bytes(('\0'.join(paths)+'\0').encode('utf-8'))
    print('EXACT_PATHSPEC',target,'paths',len(paths),'manifest',r.sha(output))

if __name__=='__main__':main()
