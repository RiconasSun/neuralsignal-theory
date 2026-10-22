"""Bootstrap only, before any protected audit or synthetic computation."""
import datetime
import hashlib
import json
import subprocess
import time
from pathlib import Path
R=Path(__file__).resolve().parents[4]
E=Path(__file__).resolve().parent;P=R/'paper16_development_r5'
BASE='b7bb1227379462c2c7a1cef40ab0d0e99a6d020b'
assert subprocess.check_output(['git','-C',str(R),'rev-parse','HEAD']).decode().strip()==BASE
assert subprocess.check_output(['git','-C',str(R),'rev-parse','origin/test']).decode().strip()==BASE
assert not subprocess.check_output(['git','-C',str(R),'diff','--name-only']).strip()
owner=(E/'OWNER_REQUEST.txt').read_bytes()
statements=[(n,s.strip()) for n,s in enumerate(owner.decode('utf-8-sig').splitlines(),1) if s.strip() and not s.lstrip().startswith(('#','```'))]
req=[{'id':'REQ-%03d'%(i+1),'owner_line':n,'requirement':s,'status':'OPEN'} for i,(n,s) in enumerate(statements)]
boot=subprocess.run(['powershell.exe','-NoProfile','-NonInteractive','-Command',"(Get-CimInstance Win32_OperatingSystem -ErrorAction Stop).LastBootUpTime.ToUniversalTime().ToString('o')"],capture_output=True,text=True,timeout=20,check=True).stdout.strip()
parsed=datetime.datetime.fromisoformat(boot);assert parsed.utcoffset()==datetime.timedelta(0)
mono=time.monotonic();now=datetime.datetime.now(datetime.timezone.utc)
def once(path,obj):
    with path.open('x',encoding='utf8',newline='\n') as f:json.dump(obj,f,indent=2,ensure_ascii=False);f.write('\n');f.flush()
stage={'mission':'P16-M3-M5-SHUTDOWN-RECOVERY-R5','phase':'A_PREFLIGHT','start_monotonic':mono,'deadline_monotonic':mono+86400,'start_UTC':now.isoformat(),'deadline_UTC':(now+datetime.timedelta(seconds=86400)).isoformat(),'windows_boot_UTC':parsed.isoformat(),'no_reset':True,'new_real_A_optimization_authorized':False,'E_authorized':False,'Final_authorized':False}
once(E/'REQUIREMENT_BASELINE.json',{'mission':stage['mission'],'base':BASE,'frozen_at':now.isoformat(),'owner_sha256':hashlib.sha256(owner).hexdigest(),'requirement_count':len(req),'items':req,'normative_protocol':'paper16_shutdown_recovery_r5_protocol/PROSPECTIVE_MISSION.md','normative_protocol_sha256':hashlib.sha256((R/'paper16_shutdown_recovery_r5_protocol/PROSPECTIVE_MISSION.md').read_bytes()).hexdigest()})
once(P/'PHASE_A_CLAIM.json',stage)
once(E/'BOOTSTRAP.json',{'recorded_utc':now.isoformat(),'HEAD':BASE,'origin_test':BASE,'origin_main':None,'classification':'ORIGIN_MAIN_ABSENT','prechange_worktree':'CLEAN_VERIFIED_BEFORE_NAMESPACE_CREATION','scope':'R5_A_AND_COMPLETE_M4_ONLY','E_authorized':False,'Final_authorized':False})
print(json.dumps({'requirements_frozen':len(req),'phaseA_claim':stage}))
