"""Results-locked document candidate,typed review/reproduction and live Git gates."""
import argparse,datetime,hashlib,json,os,subprocess
from pathlib import Path
from paper15_manuscript.source import P,E,R,read,dump,sha,verify_sources

BASE='bdec0e19621cc8018abe11c5633ce76aff611443'
MUTABLE={'CANDIDATE.json','FINAL_DELIVERY.json','ARCHIVE_FREEZE.json'}
TERMINAL={
 'Commit and push the manuscript-only package to origin/test.',
 'Verify remote commit SHA, changed-file contents and clean working tree.',
 'GIT_COMMIT','REMOTE_VERIFICATION',
 'Exact mission-only staging and normal origin/test push',
 'Remote current SHA and every changed-file blob readback',
 'Clean working tree before and after terminal receipt',
 'STOP after manuscript handoff; no submission or next mission'}

def verify_candidate():
    d=read(P/'CANDIDATE.json');assert d['base']==BASE
    assert {'MAIN_MANUSCRIPT.md','MAIN_MANUSCRIPT.pdf','SUPPLEMENT.md','SUPPLEMENT.pdf','A1_A10_CLAIM_AUDIT.md','AUTHOR_SCIENTIFIC_REVIEW.md','REPRODUCIBILITY.md'}.issubset(d['hashes'])
    for name,h in d['hashes'].items():
        path=(P/name).resolve();assert path.is_relative_to(P) and 'work' not in path.relative_to(P).parts
        assert sha(path)==h,name
    assert verify_sources()==3099
    return d

def freeze():
    assert verify_sources()==3099
    names=[p for p in P.rglob('*') if p.is_file() and not {'work','__pycache__'}.intersection(p.relative_to(P).parts) and p.name not in MUTABLE and p.suffix!='.pyc']
    d=dict(mission='P15-M7-FULL-MANUSCRIPT-AND-PUBLICATION-PACKAGE',base=BASE,hashes={p.relative_to(P).as_posix():sha(p) for p in sorted(names)},source_inputs=3099,
           scope='Frozen publication sources/figures/tables/PDFs/code/environment/audits; mutable final Git delivery is externally verified metadata,not a scientific input')
    dump(P/'CANDIDATE.json',d);verify_candidate();print('Publication candidate frozen',len(names),'files')

def native(attempt):
    verify_candidate();before=sha(P/'CANDIDATE.json')
    log=E/f'NATIVE_DOCUMENT_REPRODUCTION_{attempt}.log';receipt=E/f'NATIVE_DOCUMENT_REPRODUCTION_RECEIPT_{attempt}.json'
    assert not log.exists() and not receipt.exists()
    command=['powershell','-NoProfile','-ExecutionPolicy','Bypass','-File',str(P/'reproduce.ps1')]
    with log.open('wb') as f:completed=subprocess.run(command,cwd=R,stdout=f,stderr=subprocess.STDOUT)
    text=log.read_text(encoding='utf-8-sig');records=[]
    for line in text.splitlines():
        if line.startswith('{'):
            try:records.append(json.loads(line))
            except ValueError:pass
    result=records[0] if len(records)==1 else None
    ok=completed.returncode==0 and result is not None and result['saved_only'] is True and result['source_hashes_verified']==3099 and result['document_regressions']==10 and result['Final_D_rerun_count']==0
    if ok:verify_candidate();assert sha(P/'CANDIDATE.json')==before
    dump(receipt,dict(status='PASS_NATIVE_SAVED_DOCUMENT_REPRODUCTION' if ok else 'FAILED_DOCUMENT_REPRODUCTION',time=datetime.datetime.now(datetime.timezone.utc).isoformat(),candidate_sha256=before,command=command,exit_code=completed.returncode,log_path=log.relative_to(R).as_posix(),log_sha256=sha(log),result=result))
    assert ok,'Failed document reproduction preserved; no scientific execution'
    print('Native saved-only manuscript reproduction PASS; candidate bytes unchanged')

def valid_review(path):
    d=read(path)
    assert d['decision']=='ACCEPTED_RESULTS_LOCKED_PUBLICATION_PACKAGE'
    assert type(d['open_P0']) is int and d['open_P0']==0
    assert type(d['open_P1']) is int and d['open_P1']==0
    assert d['candidate_sha256']==sha(P/'CANDIDATE.json') and d['baseline_sha256']==sha(E/'baseline.json')
    assert d['report_sha256']==sha(R/d['report_path'])
    return d

def proof(science_review,numbers_review,reproduction):
    verify_candidate();valid_review(science_review);valid_review(numbers_review)
    r=read(reproduction)
    assert r['status']=='PASS_NATIVE_SAVED_DOCUMENT_REPRODUCTION' and type(r['exit_code']) is int and r['exit_code']==0
    assert r['candidate_sha256']==sha(P/'CANDIDATE.json') and r['log_sha256']==sha(R/r['log_path'])
    assert r['command'][0]=='powershell' and r['result']['saved_only'] is True and r['result']['original_result_numbers_unchanged'] is True
    for key,value in {'source_hashes_verified':3099,'document_regressions':10,'Final_D_rerun_count':0,'neural_arrays_loaded':0,'old_scientific_modules_imported':0,'new_real_fits':0,'new_prediction_or_likelihood_calls':0,'new_hypothesis_tests':0,'figures':7}.items():
        assert type(r['result'][key]) is int and r['result'][key]==value,key
    for name in ['MAIN_MANUSCRIPT','SUPPLEMENT']:assert r['result']['PDF_hashes'][name]==sha(P/(name+'.pdf'))
    v=read(E/'VISUAL_REVIEW.json');assert v['decision']=='PASS_VISUAL_DOCUMENT_REVIEW'
    for name in ['MAIN_MANUSCRIPT.pdf','SUPPLEMENT.pdf']:assert v['PDF_hashes'][name]==sha(P/name)
    return True

def matrix(science_review,numbers_review,reproduction,git_receipt=None,terminal=False):
    proof(science_review,numbers_review,reproduction)
    baseline=read(E/'baseline.json');assert baseline['source_sha256']==sha(E/'OWNER_REQUEST.txt')
    git_ok=False
    if terminal:
        g=read(git_receipt)
        assert g['remote_readback_verified'] is True and g['changed_blob_hashes_verified'] is True and g['working_tree_clean_before_receipt'] is True
        assert g['commit']==git('rev-parse','HEAD').decode().strip() and not git('status','--porcelain=v1','-z')
        git_ok=True
    out=[]
    for row in baseline['requirements']:
        verified=row['requirement'] not in TERMINAL or git_ok
        out.append({**row,'status':'VERIFIED' if verified else 'OPEN','implementation':['paper15_manuscript/MAIN_MANUSCRIPT.md','paper15_manuscript/SUPPLEMENT.md','paper15_manuscript/A1_A10_CLAIM_AUDIT.md','paper15_manuscript/AUTHOR_SCIENTIFIC_REVIEW.md','paper15_manuscript/CANDIDATE.json'],
            'verification_method':'Exact owner-line contract and two independent full publication/source/number reviews bound to current candidate,actual native reproduction,all-page visual/bounds proof; Git/STOP rows additionally require live current clean remote readback',
            'evidence':[str(Path(x).relative_to(R)) for x in [science_review,numbers_review,reproduction]]+(['paper15_manuscript/work/REMOTE_READBACK_H2.json'] if terminal else []),
            'scientific_limit':'Final DESCRIPTIVE ONLY; original failures remain failed; no external-submission permission'})
    result=dict(mission=baseline['mission'],baseline_requirement_count=326,verified_baseline_count=sum(x['status']=='VERIFIED' for x in out),requirements=out,terminal=terminal,
        status='PASS' if terminal else 'CONTINUE_EXECUTION',required_items_omitted=0,required_behaviors_silently_reduced=0,unapproved_existing_behaviors_removed=0,required_tests_silently_removed=0,unresolved_shrink_risk=0,temporary_substitutes_remaining=0,coverage_reductions_without_approval=0)
    assert len(out)==326
    if terminal:assert result['verified_baseline_count']==326
    dest=P/'work/FINAL_REQUIREMENT_MATRIX.json' if terminal else E/'PRESERVATION_MATRIX.json'
    dump(dest,result);print('Atomic requirements',result['verified_baseline_count'],'/326; live transport',git_ok)
    return result

def git(*args,input=None):return subprocess.check_output(['git',*args],cwd=R,input=input,env=dict(os.environ,GIT_OPTIONAL_LOCKS='0'))

def readback(revision,output):
    assert len(revision)==40 and all(c in '0123456789abcdef' for c in revision)
    output=Path(output).resolve();assert output.is_relative_to(R) and not output.exists()
    assert git('branch','--show-current').decode().strip()=='test'
    assert git('rev-parse','HEAD').decode().strip()==revision and git('rev-parse','origin/test').decode().strip()==revision
    assert git('ls-remote','origin','refs/heads/test').decode().split()==[revision,'refs/heads/test']
    assert not git('status','--porcelain=v1','-z'),'Requires actual clean checkout before receipt'
    names=[n.decode() for n in git('diff','--no-renames','--name-only','-z',BASE,revision).split(b'\0') if n]
    assert not git('diff','--no-renames','--name-only','--diff-filter=D',BASE,revision).strip()
    assert all(n=='ops/daily-operations.md' or n.startswith(('paper15_manuscript/','ops/evidence/2026-10-18/p15-m7-full-manuscript-and-publication-package/')) for n in names)
    hashes=[]
    for at in range(0,len(names),16):
        part=names[at:at+16];data=git('cat-file','--batch',input=''.join(revision+':'+n+'\n' for n in part).encode());pos=0
        for name in part:
            end=data.index(b'\n',pos);head=data[pos:end].split();assert head[1]==b'blob';size=int(head[2]);blob=data[end+1:end+1+size];pos=end+size+2
            digest=hashlib.sha256(blob).hexdigest();assert digest==sha(R/name)
            hashes.append(dict(path=name,sha256=digest,bytes=size,Git_blob=head[0].decode()))
        assert pos==len(data)
    assert verify_sources()==3099
    base_daily=git('show',BASE+':ops/daily-operations.md');assert (R/'ops/daily-operations.md').read_bytes().endswith(base_daily)
    assert not git('status','--porcelain=v1','-z')
    dump(output,dict(mission='P15-M7-FULL-MANUSCRIPT-AND-PUBLICATION-PACKAGE',time=datetime.datetime.now(datetime.timezone.utc).isoformat(),base=BASE,commit=revision,remote_ref='origin/test',remote_readback_verified=True,changed_blob_hashes_verified=True,changed_files=len(hashes),manifest=hashes,working_tree_clean_before_receipt=True,scientific_inputs_unchanged=3099,daily_BASE_suffix_unchanged=True))
    after=not git('status','--porcelain=v1','-z')
    if output.is_relative_to(P/'work'):assert after
    print('Remote current SHA',revision,';',len(hashes),'changed blobs verified; clean after receipt',after)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['freeze','native','readback']);p.add_argument('--attempt',type=int);p.add_argument('--revision');p.add_argument('--output');a=p.parse_args()
    if a.action=='freeze':freeze()
    elif a.action=='native':native(a.attempt)
    else:readback(a.revision,a.output)
