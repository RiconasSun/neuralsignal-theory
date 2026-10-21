"""Local-only exact archive inventory and publication prescreen. Never pushes."""
import argparse
import datetime
import hashlib
import json
import re
import subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[4]
P=R/'paper16_development_r4'
E=Path(__file__).resolve().parent
LOCAL=E/'PUBLICATION_LOCAL'
DEST='https://github.com/RiconasSun/neuralsignal-theory.git'
PREFIXES=['paper16_development_r4/','ops/evidence/2026-10-20/p16-m3-m5-uniform-numerical-amendment-r4/']
ALLOWED={'.py','.ps1','.md','.json','.jsonl','.csv','.txt','.log',''}
def git(*args):return subprocess.check_output(['git','-C',str(R),*args])
def sha(data):return hashlib.sha256(data).hexdigest()
def paths():
    result=set()
    for raw in [git('ls-files','-z','--',*PREFIXES),git('ls-files','-z','--others','--exclude-standard','--',*PREFIXES)]:
        result.update(p.decode('utf8') for p in raw.split(b'\0') if p)
    return sorted(p for p in result if p!='paper16_development_r4/ARCHIVE_MANIFEST.json')
def prescreen(names):
    numeric=[];findings=[]
    patterns={
      'private_key':r'-----BEGIN (?:OPENSSH |RSA |EC |ED25519 )?PRIVATE KEY-----',
      'github_token':r'\b(?:ghp_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{35,})\b',
      'aws_access_key':r'\bAKIA[0-9A-Z]{16}\b',
      'bearer_value':r'(?i)authorization\s*[:=]\s*[\"\x27]?bearer\s+[a-zA-Z0-9_.-]{20,}',
    }
    def walk(obj,path,jpath='$'):
        if isinstance(obj,list):
            if obj and all(isinstance(v,(float,int)) and not isinstance(v,bool) for v in obj):numeric.append({'path':path,'json_path':jpath,'length':len(obj)})
            else:
                for i,v in enumerate(obj):walk(v,path,jpath+'['+str(i)+']')
        elif isinstance(obj,dict):
            for k,v in obj.items():walk(v,path,jpath+'.'+k)
    for name in names:
        p=R/name
        assert p.is_file() and not p.is_symlink(),name
        assert p.suffix.lower() in ALLOWED,name
        parts=p.relative_to(R).parts
        assert not any(v in parts for v in ['work','__pycache__','TEST_TEMP','PUBLICATION_LOCAL']),name
        raw=p.read_bytes()
        assert not raw.startswith((b'PK\x03\x04',b'\x93NUMPY',b'\x89HDF')),name
        text=raw.decode('utf-16') if raw.startswith((b'\xff\xfe',b'\xfe\xff')) else raw.decode('utf-8-sig')
        assert '\x00' not in text,name
        for rule,pattern in patterns.items():
            for match in re.finditer(pattern,text):findings.append({'path':name,'line':text.count('\n',0,match.start())+1,'rule':rule})
        if p.suffix.lower()=='.json':walk(json.loads(text),name)
    assert not findings,findings
    return {'candidate_count_excluding_manifest':len(names),'secret_pattern_findings':findings,'numeric_json_lists_requiring_review':numeric,'raw_binary_magic_findings':0,'protected_path_findings':0,'scope':'Prescreen supports manual/independent review; not a guarantee of arbitrary-secret absence.'}
def main():
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=['prescreen','manifest','verify-index','verify-commit']);a=parser.parse_args()
    LOCAL.mkdir(exist_ok=True)
    names=paths()
    if a.action=='prescreen':
        out=prescreen(names)
        with (LOCAL/'PUBLIC_PRESCREEN.json').open('w',encoding='utf8') as f:json.dump(out,f,indent=2)
        print(json.dumps({k:v for k,v in out.items() if k!='numeric_json_lists_requiring_review'},indent=2));return
    if a.action=='manifest':
        assert not (P/'ARCHIVE_MANIFEST.json').exists(),'Create-only public manifest; no overwrite'
        prescreen(names)
        rows=[{'path':n,'bytes':(R/n).stat().st_size,'sha256':sha((R/n).read_bytes())} for n in names]
        obj={'mission':'P16-M3-M5-UNIFORM-NUMERICAL-AMENDMENT-R4','base':'3a7fb87c879410155595ae6a640730c290e080a9','destination':DEST,'branch':'test','publication_authorized':False,'includes_manifest_itself':False,'files':rows,'file_count_excluding_manifest':len(rows),'public_file_count_including_manifest':len(rows)+1,'bytes_excluding_manifest':sum(r['bytes'] for r in rows),'protected_arrays_included':False,'private_work_and_caches_excluded':True}
        with (P/'ARCHIVE_MANIFEST.json').open('x',encoding='utf8',newline='\n') as f:json.dump(obj,f,indent=2);f.write('\n')
        print(json.dumps({'public_file_count':len(rows)+1,'manifest_sha256':sha((P/'ARCHIVE_MANIFEST.json').read_bytes())}));return
    manifest=json.loads((P/'ARCHIVE_MANIFEST.json').read_bytes())
    by={r['path']:r for r in manifest['files']}
    expected=sorted([*by,'paper16_development_r4/ARCHIVE_MANIFEST.json'])
    assert names==sorted(by),'Exact candidate set changed'
    for n,row in by.items():assert sha((R/n).read_bytes())==row['sha256'] and (R/n).stat().st_size==row['bytes'],n
    mode=a.action
    if mode=='verify-index':
        staged=git('diff','--cached','--name-only','-z').split(b'\0');actual=sorted(n.decode() for n in staged if n)
        assert actual==expected,'Staged file set differs from manifest'
        blobs=[{'path':n,'sha256':sha(git('show',':'+n))} for n in expected]
    else:
        actual=sorted(n.decode() for n in git('diff-tree','--no-commit-id','--name-only','-r','-z','HEAD').split(b'\0') if n)
        assert actual==expected,'Commit file set differs from reviewed exact payload'
        blobs=[{'path':n,'sha256':sha(git('show','HEAD:'+n))} for n in expected]
        assert not git('status','--porcelain').strip(),'Working tree must be clean'
        assert git('rev-parse','HEAD^').decode().strip()==manifest['base'],'Unexpected parent'
    for row in blobs:assert row['sha256']==sha((R/row['path']).read_bytes()),row['path']
    out={'mode':mode,'recorded_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'head':git('rev-parse','HEAD').decode().strip(),'public_file_count':len(expected),'manifest_sha256':sha((P/'ARCHIVE_MANIFEST.json').read_bytes()),'all_git_blob_raw_sha256_match':True,'files':blobs,'new_payload_pushed':False,'owner_authorization_pending':True}
    with (LOCAL/(mode+'.json')).open('x',encoding='utf8') as f:json.dump(out,f,indent=2);f.write('\n')
    print(json.dumps({k:v for k,v in out.items() if k!='files'}))
if __name__=='__main__':main()
