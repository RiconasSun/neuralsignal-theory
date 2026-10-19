"""One immutable Development interval; Windows reboot fails closed, no rebasing."""
import datetime
from functools import lru_cache
import math
import subprocess
import time
from .core import ResourceStop

UTC = datetime.timezone.utc


def utc_now(): return datetime.datetime.now(UTC)


def parse_utc(value):
    try:
        stamp = datetime.datetime.fromisoformat(value)
        if stamp.tzinfo is None or stamp.utcoffset() != datetime.timedelta(0): raise ValueError('not UTC')
        return stamp
    except (TypeError, ValueError) as exc:
        raise ResourceStop('Missing/malformed original UTC clock identity') from exc


@lru_cache(maxsize=1)
def boot_identity():
    try:
        value = subprocess.run(['powershell.exe', '-NoProfile', '-NonInteractive', '-Command',
            "(Get-CimInstance Win32_OperatingSystem -ErrorAction Stop).LastBootUpTime.ToUniversalTime().ToString('o')"],
            capture_output=True, text=True, timeout=15, check=True).stdout.strip()
        return parse_utc(value).isoformat()
    except (OSError, subprocess.SubprocessError) as exc:
        raise ResourceStop('Windows boot epoch unavailable; no source access') from exc


def make_stage(seconds):
    if type(seconds) not in (int, float) or not math.isfinite(seconds) or not 0 < seconds <= 172800:
        raise ResourceStop('Development interval exceeds original48h')
    boot = boot_identity()
    start = time.monotonic(); wall = utc_now()
    return {'start_monotonic': start, 'deadline_monotonic': start+seconds,
            'start_UTC': wall.isoformat(), 'deadline_UTC': (wall+datetime.timedelta(seconds=seconds)).isoformat(),
            'windows_boot_UTC': boot, 'no_reset': True}


def guard(stage):
    try:
        start, end = stage['start_monotonic'], stage['deadline_monotonic']
        if any(type(v) not in (int, float) or not math.isfinite(v) for v in [start, end]): raise ValueError('nonfinite')
        first, last = parse_utc(stage['start_UTC']), parse_utc(stage['deadline_UTC'])
        span = (last-first).total_seconds()
        if not 0 < end-start <= 172800 or abs(span-(end-start)) > 1e-6 or stage.get('no_reset') is not True:
            raise ValueError('interval mismatch')
        mono, wall = time.monotonic(), utc_now()
        if not start <= mono < end or not first <= wall < last: raise ValueError('stale/expired clock')
    except (KeyError, TypeError, ValueError, OverflowError) as exc:
        raise ResourceStop('Original Development48h deadline/stale clock; no phase reset') from exc


def verify_stage_environment(stage):
    guard(stage)
    if stage.get('windows_boot_UTC') != boot_identity():
        raise ResourceStop('Changed Windows boot epoch; original stage cannot resume')
    guard(stage)


def conservative_deadline(stage):
    guard(stage)
    return min(stage['deadline_monotonic'], time.monotonic()+(parse_utc(stage['deadline_UTC'])-utc_now()).total_seconds())
