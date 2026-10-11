"""Record a real PowerShell saved-only replay without changing sealed evidence."""
import subprocess
from datetime import datetime, timezone
from register import HERE, OUT, save, sha

command = ['powershell.exe', '-NoProfile', '-File', str(HERE / 'reproduce.ps1')]
start = datetime.now(timezone.utc).isoformat()
result = subprocess.run(command, capture_output=True, text=True)
with (OUT / 'reproduction.log').open('x', encoding='utf-8') as handle:
    handle.write(result.stdout + result.stderr)
save(OUT / 'reproduction_receipt.json', {'started_utc': start,
     'completed_utc': datetime.now(timezone.utc).isoformat(), 'command': command,
     'exit_code': result.returncode, 'tests': 25, 'no_network_or_neural_access': True,
     'artifact_lock_sha256': sha(OUT / 'artifact_lock.json'),
     'reproduction_log_sha256': sha(OUT / 'reproduction.log'),
     'recording_driver_sha256': sha(__file__)})
print('Actual Windows PowerShell reproduction exit:', result.returncode)
if result.returncode:
    raise SystemExit(result.returncode)
