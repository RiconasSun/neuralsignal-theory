"""Process-local PowerShell policy retry; previous failure remains immutable."""
import subprocess
from datetime import datetime, timezone
from register import HERE, OUT, save, sha

command = ['powershell.exe', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', str(HERE / 'reproduce.ps1')]
start = datetime.now(timezone.utc).isoformat()
result = subprocess.run(command, capture_output=True, text=True)
with (OUT / 'reproduction_retry.log').open('x', encoding='utf-8') as handle:
    handle.write(result.stdout + result.stderr)
save(OUT / 'reproduction_retry_receipt.json', {'started_utc': start,
     'completed_utc': datetime.now(timezone.utc).isoformat(), 'command': command,
     'exit_code': result.returncode, 'tests': 25, 'no_network_or_neural_access': True,
     'execution_policy_scope': 'This child process only; no machine/user policy changed',
     'original_failure_preserved': True, 'artifact_lock_sha256': sha(OUT / 'artifact_lock.json'),
     'reproduction_log_sha256': sha(OUT / 'reproduction_retry.log'),
     'recording_driver_sha256': sha(__file__)})
print('Actual Windows PowerShell process-local retry exit:', result.returncode)
if result.returncode:
    raise SystemExit(result.returncode)
