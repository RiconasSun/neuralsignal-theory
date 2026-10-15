"""Package reviewed public-only ceremony sources; no custody/key/state tree traversal."""
import hashlib
import json
from pathlib import Path
import tempfile
import subprocess
import sys
import zipfile

E=Path(__file__).resolve().parent;ROOT=E.parents[3];H=ROOT/'paper12_singleowner1'

def main():
    names=('__init__.py','common.py','owner_protocol.py','ed25519_public.py','owner_onboarding.py','public_key.py')
    freeze=json.loads((H/'source_freeze.json').read_text());entries={}
    for name in names:
        raw=(H/name).read_bytes()
        if hashlib.sha256(raw).hexdigest()!=freeze['source_sha256'][name]:raise RuntimeError('PUBLIC_KIT_SOURCE_DRIFT:'+name)
        entries['paper12_singleowner1/'+name]=raw
    entries['paper12_controls1/release_control.py']=(ROOT/'paper12_controls1/release_control.py').read_bytes()
    entries['OWNER_SETUP.md']=(H/'OWNER_SETUP.md').read_bytes()
    entries['SECURITY_AMENDMENT.md']=(E/'SECURITY_AMENDMENT.md').read_bytes()
    entries['PUBLIC_KEY_VALIDITY_AMENDMENT.md']=(E/'PUBLIC_KEY_VALIDITY_AMENDMENT.md').read_bytes()
    entries['source_freeze.json']=(H/'source_freeze.json').read_bytes()
    identity={'mission':'P12-REAL-D-SINGLE-APPROVER-AMEND-1','base':'6e952aeb0bc19abead5b208327b56298f25dc290','production_freeze_sha256':hashlib.sha256((H/'source_freeze.json').read_bytes()).hexdigest(),'public_sources_only':True,'no_private_signer_or_material':True,'owner_environment_not_yet_provisioned':True,'dependencies':'Owner offline device: Python3.11 and cryptography; no neural/runtime bundles needed for prepare/confirm','sha256':{n:hashlib.sha256(raw).hexdigest() for n,raw in entries.items()}}
    entries['PUBLIC_KIT_MANIFEST.json']=(json.dumps(identity,indent=2,sort_keys=True)+'\n').encode()
    path=E/'owner_public_toolkit_r3.zip'
    with zipfile.ZipFile(path,'x',compression=zipfile.ZIP_DEFLATED) as archive:
        for name,raw in sorted(entries.items()):
            info=zipfile.ZipInfo(name,date_time=(2026,10,15,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;archive.writestr(info,raw)
    temp=H/'jobs/test_tmp'
    with tempfile.TemporaryDirectory(dir=temp) as folder:
        with zipfile.ZipFile(path) as archive:
            if archive.namelist()!=sorted(entries):raise RuntimeError('EXACT_PUBLIC_KIT_ROSTER')
            for name,raw in entries.items():
                if archive.read(name)!=raw:raise RuntimeError('PUBLIC_KIT_BYTES')
            archive.extractall(folder)
        result=subprocess.run([sys.executable,'-B','-m','paper12_singleowner1.public_key','--help'],cwd=folder,capture_output=True,text=True)
        if result.returncode!=0 or 'prepare' not in result.stdout or 'confirm' not in result.stdout:raise RuntimeError('PUBLIC_KIT_IMPORT_CLI')
    receipt={'zip_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'files':len(entries),'byte_identity_verified':True,'fresh_directory_public_entrypoint_import':'PASS','private_key_or_REAL_provisioning':False,**identity}
    with (E/'public_kit_receipt_r3.json').open('x',encoding='utf-8') as f:json.dump(receipt,f,indent=2,sort_keys=True);f.write('\n')
    print(json.dumps({'owner_public_toolkit':str(path),'files':len(entries),'source_identity_and_fresh_public_CLI':'PASS','no_private_or_REAL_operations':True},sort_keys=True))

if __name__=='__main__':main()
