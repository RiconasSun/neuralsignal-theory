"""Read-only Git remote/blob proof; output goes to an explicit workspace path."""
import argparse
import datetime
import hashlib
import os
from pathlib import Path
import re
import subprocess
from paper15_final1.source import R,E,read,dump,sha


def git(*args,input=None):
    return subprocess.check_output(['git',*args],cwd=R,input=input,env=dict(os.environ,GIT_OPTIONAL_LOCKS='0'))


def verify(revision,output):
    assert re.fullmatch('[0-9a-f]{40}',revision)
    output=Path(output).resolve();assert output.is_relative_to(R) and not output.exists()
    base=read(E/'baseline.json')['base']
    assert git('rev-parse','HEAD').decode().strip()==revision
    assert git('branch','--show-current').decode().strip()=='test'
    remote=git('ls-remote','origin','refs/heads/test').decode().strip().split()
    assert remote==[revision,'refs/heads/test'] and git('rev-parse','origin/test').decode().strip()==revision
    assert not git('status','--porcelain=v1','-z'),'Readback requires an actually clean checkout before the receipt'
    paths=[n.decode('utf8') for n in git('diff','--no-renames','--name-only','-z',base,revision).split(b'\0') if n]
    assert paths and not git('diff','--no-renames','--name-only','--diff-filter=D',base,revision).strip()
    allowed=('paper15_final1/','ops/evidence/2026-10-18/p15-m6-independent-final-validation/')
    assert all(n=='ops/daily-operations.md' or n.startswith(allowed) for n in paths)
    records=[]
    for at in range(0,len(paths),16):
        names=paths[at:at+16];assert all('\n' not in n and '\r' not in n for n in names)
        data=git('cat-file','--batch',input=''.join(revision+':'+n+'\n' for n in names).encode('utf8'));pos=0
        for name in names:
            end=data.index(b'\n',pos);header=data[pos:end].split();assert len(header)==3 and header[1]==b'blob'
            size=int(header[2]);start=end+1;blob=data[start:start+size];pos=start+size+1
            assert len(blob)==size and data[pos-1:pos]==b'\n'
            expected=hashlib.sha256(blob).hexdigest();path=R/name
            assert path.resolve().is_relative_to(R) and sha(path)==expected,name
            records.append(dict(path=name,Git_blob=header[0].decode(),bytes=size,sha256=expected))
        assert pos==len(data)
    before=not git('status','--porcelain=v1','-z');assert before
    receipt=dict(time=datetime.datetime.now(datetime.timezone.utc).isoformat(),base=base,commit=revision,
                 remote_ref='refs/heads/test',remote_readback_verified=True,changed_blob_hashes_verified=True,
                 changed_files=len(records),manifest=records,working_tree_clean_before_receipt=before,
                 scientific_source_change_scope='Only P15 Final package/evidence and current daily prefix; no historical deletion',
                 self_reference_note='A receipt inside the next commit certifies this historical archive; final live HEAD readback is stored outside tracked files')
    dump(output,receipt)
    after=not git('status','--porcelain=v1','-z')
    if output.is_relative_to(R/'paper15_final1/work'):assert before and after,'Final ignored receipt requires an actually clean checkout'
    print('Remote',revision,'read back;',len(records),'changed blobs SHA256 matched; clean after receipt:',after)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--revision',required=True);p.add_argument('--output',required=True)
    a=p.parse_args();verify(a.revision,a.output)
