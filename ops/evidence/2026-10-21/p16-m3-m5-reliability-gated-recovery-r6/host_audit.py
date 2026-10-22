"""Registered read-only native host evidence. No neural/model imports or OS writes."""
import ctypes
from ctypes import wintypes
import datetime
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import time
import base64

R = Path(__file__).resolve().parents[4]
E = Path(__file__).resolve().parent
P = R / 'paper16_development_r6'


def load(path):
    return json.loads(path.read_bytes())


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def guard():
    claim = load(P / 'PHASE_A_CLAIM.json')
    reg = load(E / 'HOST_AUDIT_REGISTRATION.json')
    assert sha(P / 'PHASE_A_CLAIM.json') == reg['phase_claim_sha256']
    assert claim['start_monotonic'] <= time.monotonic() < claim['deadline_monotonic']
    assert datetime.datetime.now(datetime.timezone.utc) < datetime.datetime.fromisoformat(claim['deadline_UTC'])
    assert claim['no_reset'] is True


def once(path, value):
    with path.open('x', encoding='utf8', newline='\n') as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.write('\n')
        stream.flush()
        os.fsync(stream.fileno())


def powershell(script):
    guard()
    env = os.environ.copy()
    env['PSModulePath'] = r'C:\Windows\System32\WindowsPowerShell\v1.0\Modules'
    command = ['powershell.exe', '-NoProfile', '-NonInteractive', '-EncodedCommand',
               base64.b64encode(script.encode('utf-16-le')).decode('ascii')]
    result = subprocess.run(command, env=env, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, timeout=60, creationflags=0x08000000)
    guard()
    return {'actual_native_exit_code': result.returncode,
            'stdout': result.stdout.decode('utf-8-sig', errors='replace'),
            'stderr': result.stderr.decode('utf-8-sig', errors='replace')}


def run():
    guard()
    registration = load(E / 'HOST_AUDIT_REGISTRATION.json')
    assert sha(Path(__file__)) == registration['script_sha256']
    target = E / 'HOST_AUDIT_NATIVE.json'
    assert not target.exists()
    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    kernel.GetCurrentProcess.restype = wintypes.HANDLE
    kernel.IsProcessInJob.argtypes = [wintypes.HANDLE, wintypes.HANDLE, ctypes.POINTER(wintypes.BOOL)]
    kernel.IsProcessInJob.restype = wintypes.BOOL
    member = wintypes.BOOL()
    assert kernel.IsProcessInJob(kernel.GetCurrentProcess(), None, ctypes.byref(member))
    session = wintypes.DWORD()
    assert kernel.ProcessIdToSessionId(os.getpid(), ctypes.byref(session))

    class Memory(ctypes.Structure):
        _fields_ = [('length', wintypes.DWORD), ('load', wintypes.DWORD),
                    ('total_physical', ctypes.c_ulonglong), ('available_physical', ctypes.c_ulonglong),
                    ('total_page', ctypes.c_ulonglong), ('available_page', ctypes.c_ulonglong),
                    ('total_virtual', ctypes.c_ulonglong), ('available_virtual', ctypes.c_ulonglong),
                    ('available_extended', ctypes.c_ulonglong)]

    memory = Memory()
    memory.length = ctypes.sizeof(memory)
    assert kernel.GlobalMemoryStatusEx(ctypes.byref(memory))
    disk = shutil.disk_usage(R)
    script = r'''
$ErrorActionPreference='Stop'
$OutputEncoding=[Console]::OutputEncoding=New-Object System.Text.UTF8Encoding
$o=Get-CimInstance Win32_OperatingSystem
$chain=@();$walk=__PY_PID__
for($i=0;$i -lt 10 -and $walk -gt 0;$i++){
  $v=Get-CimInstance Win32_Process -Filter ("ProcessId="+$walk) -ErrorAction SilentlyContinue
  if($null -eq $v){break}
  $chain+=@{pid=[int]$v.ProcessId;parent_pid=[int]$v.ParentProcessId;name=$v.Name;executable=$v.ExecutablePath;created_UTC=if($v.CreationDate){$v.CreationDate.ToUniversalTime().ToString('o')}else{$null}}
  $walk=[int]$v.ParentProcessId
}
$start=[DateTime]::Parse('2026-10-20T17:00:00Z').ToUniversalTime()
$until=[DateTime]::UtcNow
$system=@();$application=@();$queries=@()
foreach($kind in @('System','Application')){
  $ids=if($kind -eq 'System'){@(12,13,41,42,107,109,1074,1076,6005,6006,6008)}else{@(1000,1001,1002)}
  try{
    $events=@(Get-WinEvent -FilterHashtable @{LogName=$kind;StartTime=$start;EndTime=$until;Id=$ids} -MaxEvents 2000 -ErrorAction Stop)
    $queries+=@{log=$kind;query_succeeded=$true;returned=$events.Count;limit=2000}
    foreach($event in $events){
      $xml=[xml]$event.ToXml();$fields=@{}
      foreach($d in $xml.Event.EventData.Data){
        $name=[string]$d.Name;$value=[string]$d.'#text'
        if($name -match '^(AppName|AppPath|ProcessId|ExceptionCode|ModuleName|ModulePath|BugcheckCode|PowerButtonTimestamp|SleepInProgress|BootAppStatus|TargetState|EffectiveState|Reason|Flags|WakeTime|SleepTime|WakeSourceType|WakeSourceText|BootId|ShutdownActionType|ShutdownEventCode|ShutdownReason|param1|param3|param4|param5)$'){
          $fields[$name]=$value
        }
      }
      if($kind -eq 'Application' -and (($fields | ConvertTo-Json -Compress) -notmatch '(?i)python|codex|powershell')){continue}
      $row=@{log=$kind;id=[int]$event.Id;provider=$event.ProviderName;record_id=[long]$event.RecordId;time_UTC=$event.TimeCreated.ToUniversalTime().ToString('o');fields=$fields}
      if($kind -eq 'System'){$system+=$row}else{$application+=$row}
    }
  }catch{
    $none=$_.FullyQualifiedErrorId -match 'NoMatchingEventsFound'
    $queries+=@{log=$kind;query_succeeded=$none;no_matching_events=$none;error_id=$_.FullyQualifiedErrorId;exception_type=$_.Exception.GetType().FullName}
  }
}
@{boot_UTC=$o.LastBootUpTime.ToUniversalTime().ToString('o');OS_caption=$o.Caption;OS_version=$o.Version;total_visible_memory_KiB=[long]$o.TotalVisibleMemorySize;free_physical_memory_KiB=[long]$o.FreePhysicalMemory;parent_chain=$chain;event_window_start_UTC=$start.ToString('o');event_window_end_UTC=$until.ToString('o');queries=$queries;system_events=$system;relevant_application_events=$application}|ConvertTo-Json -Depth 12 -Compress
'''.replace('__PY_PID__', str(os.getpid()))
    native = powershell(script)
    assert native['actual_native_exit_code'] == 0, native['stderr']
    native['parsed'] = json.loads(native['stdout'])
    boot = datetime.datetime.fromisoformat(native['parsed']['boot_UTC'])
    assert boot == datetime.datetime.fromisoformat(load(P/'PHASE_A_CLAIM.json')['windows_boot_UTC'])
    power = []
    for args in [['/a'], ['/getactivescheme'], ['/query', 'SCHEME_CURRENT', 'SUB_SLEEP']]:
        guard()
        q = subprocess.run(['powercfg.exe', *args], stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE, timeout=20, creationflags=0x08000000)
        power.append({'command': ['powercfg.exe', *args], 'actual_native_exit_code': q.returncode,
                      'stdout': q.stdout.decode('utf8', errors='replace'),
                      'stderr': q.stderr.decode('utf8', errors='replace'),
                      'raw_stdout_base64': base64.b64encode(q.stdout).decode('ascii'),
                      'raw_stdout_sha256': hashlib.sha256(q.stdout).hexdigest()})
    requirements = load(P / 'RELIABILITY_REQUIREMENTS.json')
    resource_pass = (memory.available_physical >= requirements['minimum_available_memory_bytes']
                     and disk.free >= requirements['minimum_target_free_disk_bytes'])
    historical = []
    for name in ['paper16_development_r4/results/STAGE_CLAIM.json',
                 'paper16_development_r5/results/STAGE_CLAIM.json',
                 'paper16_development_r5/results/SUPERVISOR.json',
                 'paper16_development_r5/results/WORKER_CLAIM.json',
                 'ops/evidence/2026-10-21/p16-m3-m5-shutdown-recovery-r5/EXTERNAL_SCIENTIFIC_STOP.json',
                 'ops/evidence/2026-10-21/p16-m3-m5-shutdown-recovery-r5/ENVIRONMENT_REATTACH_PROCESS_LOSS_1.json']:
        path = R / name
        historical.append({'path': name, 'sha256': sha(path), 'metadata': load(path)})
    result = {'schema': 'R6_READ_ONLY_HOST_AUDIT_V1', 'mission': registration['mission'],
              'recorded_UTC': datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'registration_sha256': sha(E/'HOST_AUDIT_REGISTRATION.json'),
              'phase_claim_sha256': registration['phase_claim_sha256'],
              'native_process_pid': os.getpid(), 'native_process_in_inherited_job': bool(member.value),
              'windows_session_id': session.value, 'interactive_session_dependency_disclosed': session.value != 0,
              'total_physical_memory_bytes': memory.total_physical,
              'available_physical_memory_bytes': memory.available_physical,
              'target_volume_total_bytes': disk.total, 'target_volume_free_bytes': disk.free,
              'registered_resource_floor_pass': resource_pass, 'native_host': native, 'power_queries': power,
              'historical_receipts': historical, 'root_cause': 'UNKNOWN_PENDING_INDEPENDENT_EVIDENCE_REVIEW',
              'OS_settings_modified': False, 'neural_sources_or_arrays_read': False,
              'fits_derivatives_scores': 0, 'host_reliability_gate_pass': False,
              'remaining_gate': 'ACTUAL_SYNTHETIC_NATIVE_LIFECYCLE_AND_INDEPENDENT_REVIEW'}
    guard()
    once(target, result)
    print(json.dumps({'path': target.relative_to(R).as_posix(), 'sha256': sha(target),
                      'resource_floor_pass': resource_pass,
                      'process_in_inherited_job': bool(member.value),
                      'windows_session_id': session.value,
                      'system_event_count': len(native['parsed']['system_events']),
                      'relevant_application_event_count': len(native['parsed']['relevant_application_events']),
                      'host_gate_pass': False}, indent=2))


if __name__ == '__main__':
    run()
