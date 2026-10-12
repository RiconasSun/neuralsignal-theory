"""Capture a real native PowerShell command and its saved-metadata proof."""
import json
import shutil
import subprocess
from datetime import datetime, timezone
from audit import HERE
from register import sha

if __name__=='__main__':
    command = ['powershell.exe','-NoProfile','-ExecutionPolicy','Bypass','-File',str(HERE/'reproduce.ps1')]
    run = subprocess.run(command,cwd=HERE.parent,capture_output=True,text=True)
    output = HERE/'evidence'
    output.mkdir(exist_ok=True)
    (output/'powershell.log').write_text(run.stdout+run.stderr)
    if run.returncode: raise RuntimeError('Actual native PowerShell replay failed; see evidence/powershell.log')
    for name in ('reproduction_result.json','tests.log'):
        shutil.copyfile(HERE/'replay'/name,output/name)
    receipt = {'utc':datetime.now(timezone.utc).isoformat(),'command':command,
               'exit_code':run.returncode,'manifest_sha256':sha(HERE/'manifest.json'),
               'scope':'Offline saved metadata only; no re-download, neural experiment or scientific validation'}
    (output/'powershell_command.json').write_text(json.dumps(receipt,indent=2,sort_keys=True))
    print(json.dumps(receipt,indent=2))
