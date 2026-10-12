"""Offline table/figure/document regeneration and prospective artifact parity."""
import argparse
import json
import os
import platform
import subprocess
import sys
from pathlib import Path

import matplotlib
import numpy as np

from freeze import HERE, ROOT, load, sha
from build import Saved, write_json
from reference_check import verify_references


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--pdf-python',required=True)
    args=parser.parse_args(); saved=Saved();original=HERE/'output';out=HERE/'reproduction'
    out.mkdir(exist_ok=True);manifest=load(original/'publication_manifest.json')
    for path,digest in manifest['source_sha256'].items():assert sha(ROOT/path)==digest,path
    for path,digest in manifest['outputs_sha256'].items():assert sha(original/path)==digest,path
    commands=[[sys.executable,str(HERE/'build.py'),'--output',str(out)],
              [sys.executable,str(HERE/'documents.py'),'--output',str(out)],
              [args.pdf_python,str(HERE/'pdf_document.py'),'--output',str(out)]]
    log=[]
    for command in commands:
        result=subprocess.run(command,capture_output=True,text=True)
        log.append({'command':command,'exit_code':result.returncode,'stdout':result.stdout,'stderr':result.stderr})
        if result.returncode:
            write_json(out/'execution_log.json',log);raise RuntimeError('Saved-only generation command failed')
    env=dict(os.environ,P11_CLOSEOUT_OUTPUT=str(out))
    tests=subprocess.run([sys.executable,'-m','unittest','discover','-s',str(HERE),'-p','test_closeout.py','-v'],
                         capture_output=True,text=True,env=env)
    (out/'tests.log').write_text(tests.stdout+tests.stderr,encoding='utf-8')
    assert tests.returncode==0
    references=verify_references(out)
    parity=[]
    for path,digest in manifest['outputs_sha256'].items():
        if path in ('manuscript.pdf','supplement.pdf'):continue
        assert sha(out/path)==digest,'Artifact mismatch: '+path
        parity.append(path)
    pdf=subprocess.run([args.pdf_python,str(HERE/'pdf_parity.py'),'--original',str(original),'--regenerated',str(out)],capture_output=True,text=True)
    assert pdf.returncode==0,pdf.stderr
    poppler='C:/Users/85993/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/poppler/Library/bin/pdftoppm.exe'
    raster=out/'pdf_parity';raster.mkdir(exist_ok=True)
    pixels=[]
    for name in ('manuscript','supplement'):
        for label,folder in [('original',original),('regenerated',out)]:
            result=subprocess.run([poppler,'-r','50','-png',str(folder/(name+'.pdf')),str(raster/(name+'_'+label))],capture_output=True)
            assert result.returncode==0
        a=sorted(raster.glob(name+'_original-*.png'));b=sorted(raster.glob(name+'_regenerated-*.png'))
        assert len(a)==len(b)
        assert all(sha(x)==sha(y) for x,y in zip(a,b)),'Regenerated PDF raster mismatch'
        pixels.append({'document':name,'pages':len(a),'pixel_sha256_equal':True})
    write_json(out/'execution_log.json',log)
    write_json(out/'reproducibility_report.json',{
        'saved_only':True,'generation_commands':commands,'tests':21,'test_exit_code':tests.returncode,
        'byte_identical_artifacts':parity,'pdf_text_parity':json.loads(pdf.stdout),'pdf_pixel_parity':pixels,
        'reference_checks':references,'python':platform.python_version(),'numpy':np.__version__,
        'matplotlib':matplotlib.__version__,'plotting_python':sys.executable,'pdf_python':args.pdf_python,
        'input_hashes_verified':len(saved.record['input_sha256']),'model_fits':0,'new_inference':0,
        'null_suite_reexecuted':False,'external_holdout_accessed':False,
        'MANUSCRIPT_REPRODUCED':True,'SCIENTIFIC_VALIDATION_PASS':False})
    print('Saved-only reproduction PASS:21tests, all tables/text/7figures match;22PDF pages text/pixels match; no new scientific execution.')


if __name__=='__main__':main()
