"""Canonical package launcher; preserve the unchanged registered audit source."""
import datetime
import hashlib
import importlib
import json
import traceback
from pathlib import Path

E=Path(__file__).resolve().parent
registration=json.loads((E/'INDEPENDENT_REUSE_AUDIT_REGISTRATION_2.json').read_bytes())
digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert digest(Path(__file__))==registration['launcher_sha256']
assert digest(E/'INDEPENDENT_R5_REUSE_AUDIT.py')==registration['unchanged_audit_script_sha256']
audit=importlib.import_module('ops.evidence.2026-10-21.p16-m3-m5-shutdown-recovery-r5.INDEPENDENT_R5_REUSE_AUDIT')
try:
    audit.main()
except BaseException as exc:
    failure={'recorded_UTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),
             'context':audit.CONTEXT,'type':type(exc).__name__,'message':str(exc),
             'traceback':traceback.format_exc(),'counts_so_far':dict(audit.COUNTS),
             'same_original_phase_A_claim':True,'later_states_after_failure':False,
             'automatic_retry':False}
    audit.once(E/'INDEPENDENT_R5_AUDIT_FAILURE_2.json',failure)
    print(json.dumps(failure,indent=2),flush=True)
    raise
