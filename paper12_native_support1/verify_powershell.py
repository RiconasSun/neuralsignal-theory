import json
import shutil
import subprocess
from datetime import datetime,timezone
from register import HERE,sha

if __name__=='__main__':
    command=['powershell.exe','-NoProfile','-ExecutionPolicy','Bypass','-File',str(HERE/'reproduce.ps1'),'-FullDigitalTiming']
    result=subprocess.run(command,cwd=HERE.parent,capture_output=True,text=True)
    out=HERE/'evidence';out.mkdir(exist_ok=True)
    (out/'powershell.log').write_text(result.stdout+result.stderr)
    if result.returncode:raise RuntimeError('Native PowerShell full timing replay failed; see evidence/powershell.log')
    for name in ('tests.log','reproduction_result.json'):shutil.copyfile(HERE/'replay'/name,out/name)
    (out/'powershell_command.json').write_text(json.dumps({'utc':datetime.now(timezone.utc).isoformat(),
        'command':command,'exit_code':result.returncode,'manifest_sha256':sha(HERE/'manifest.json')},indent=2,sort_keys=True))
    print('Actual native PowerShell full timing audit reproduction exit0.')
