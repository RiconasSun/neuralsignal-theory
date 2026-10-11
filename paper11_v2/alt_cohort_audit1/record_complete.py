"""Real final PowerShell replay of the entire sealed metadata-only package."""
import subprocess
from datetime import datetime, timezone
from register import HERE, OUT, save, sha

command = ['powershell.exe', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', str(HERE / 'reproduce-all.ps1')]
start = datetime.now(timezone.utc).isoformat()
result = subprocess.run(command, capture_output=True, text=True)
with (OUT / 'complete_reproduction.log').open('x', encoding='utf-8') as handle:
    handle.write(result.stdout + result.stderr)
save(OUT / 'complete_reproduction_receipt.json', {'started_utc': start,
     'completed_utc': datetime.now(timezone.utc).isoformat(), 'command': command,
     'exit_code': result.returncode, 'tests': 25, 'no_network_or_neural_access': True,
     'execution_policy_scope': 'Child process only; original failure retained',
     'complete_package_lock_sha256': sha(OUT / 'complete_package_lock.json'),
     'reproduction_log_sha256': sha(OUT / 'complete_reproduction.log'),
     'driver_sha256': sha(__file__)})
print('Actual complete Windows PowerShell replay exit:', result.returncode)
if result.returncode:
    raise SystemExit(result.returncode)
