"""Exact normal origin/test readback and binary blob proof; writes only external receipt."""
import argparse
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import subprocess

E=Path(__file__).resolve().parent;ROOT=E.parents[3]

def require(value,label):
    if not value:raise RuntimeError(label)
def git(*args):return subprocess.run(['git',*args],cwd=ROOT,capture_output=True,check=True).stdout
def digest(value):return hashlib.sha256(value).hexdigest()

def main():
    p=argparse.ArgumentParser();p.add_argument('--commit',required=True);p.add_argument('--receipt',required=True);args=p.parse_args();commit=args.commit
    require(len(commit)==40 and all(c in '0123456789abcdef' for c in commit),'FULL_COMMIT_SHA')
    remote=git('ls-remote','origin','refs/heads/test').decode().split();require(len(remote)==2 and remote[0]==commit and remote[1]=='refs/heads/test','ACTUAL_REMOTE_TEST_SHA')
    git('fetch','origin','--prune')
    require(git('rev-parse','HEAD').decode().strip()==git('rev-parse','origin/test').decode().strip()==commit,'HEAD_REMOTE_READBACK')
    require(git('branch','--show-current').decode().strip()=='test','EXACT_TEST_BRANCH')
    git('merge-base','--is-ancestor','76b19508a5a0728e500ff2e5f9c959309fbf967e',commit)
    manifest=json.loads((E/'git_file_manifest.json').read_text());paths=manifest['paths'];changed=git('diff-tree','--no-commit-id','--name-only','-r',commit).decode('utf-8').splitlines()
    require(len(paths)==len(set(paths)) and set(paths)==set(changed),'EXACT_COMMITTED_FILE_MANIFEST')
    allowed=('paper12_production1/','ops/evidence/2026-10-15/p12-d-production-path-readiness-1/')
    require(all((x=='ops/daily-operations.md' or x.startswith(allowed)) and not any(v in '/'+x for v in ('/.private/','/jobs/','/exports/')) for x in paths),'MISSION_ONLY_NO_PRIVATE_JOB_EXPORTS')
    batch=''.join(commit+':'+name+'\n' for name in paths).encode('utf-8');answer=subprocess.run(['git','cat-file','--batch'],input=batch,cwd=ROOT,capture_output=True,check=True).stdout;offset=0;hashes={}
    for name in paths:
        end=answer.index(b'\n',offset);header=answer[offset:end].split();require(len(header)==3 and header[1]==b'blob','REMOTE_TREE_BLOB:'+name);size=int(header[2]);offset=end+1;raw=answer[offset:offset+size];offset+=size
        require(answer[offset:offset+1]==b'\n','BINARY_BATCH_FRAME');offset+=1
        expected=digest((ROOT/name).read_bytes());require(digest(raw)==expected,'EXACT_SAVED_REMOTE_BLOB_BYTES:'+name);hashes[name]=expected
    require(offset==len(answer),'EXACT_BATCH_PAYLOAD')
    daily=(ROOT/'ops/daily-operations.md').read_bytes();require(daily.endswith((E/'daily_at_registration.bin').read_bytes()),'HISTORICAL_DAILY_SUFFIX_IMMUTABLE')
    clean=git('status','--porcelain=v1','--untracked-files=normal');require(not clean,'CLEAN_WORKING_TREE')
    receipt=Path(args.receipt).resolve();external=Path('C:/Users/85993/.codex/visualizations/2026/10/13/01a13780-a5dc-7e01-8acc-80dd913c1489').resolve()
    require(receipt.is_relative_to(external) and not receipt.is_relative_to(ROOT),'EXTERNAL_RECEIPT_BOUNDARY')
    report={'mission':'P12-D-PRODUCTION-PATH-READINESS-1','utc':datetime.now(timezone.utc).isoformat(),'base':'76b19508a5a0728e500ff2e5f9c959309fbf967e','branch':'test','commit':commit,'remote_readback':remote[0],'tree':git('rev-parse',commit+'^{tree}').decode().strip(),'changed_files':len(paths),'remote_blob_sha256':hashes,'working_tree_clean':True,'push_policy_evidence':'Separate actual normal git push origin test command receipt; readback alone does not establish action history','D_RELEASE_CONSUMED':False,'D_EVALUATION_EXECUTED':False}
    with receipt.open('x',encoding='utf-8',newline='\n') as handle:json.dump(report,handle,indent=2,sort_keys=True);handle.write('\n')
    print(json.dumps({'remote_test_sha':commit,'exact_blob_readback':'PASS','changed_files':len(paths),'clean':True,'external_receipt':str(receipt)}))

if __name__=='__main__':main()
