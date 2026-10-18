"""Version only the reviewed reusable primitives; preserve all old packages."""
from pathlib import Path
import json
import hashlib

R = Path(__file__).resolve().parents[4]
E = Path(__file__).resolve().parent
P = R/'paper15_final1'
assert (E/'baseline.json').exists() and not P.exists()
P.mkdir()
copied=[]
for name in ['features.py','models.py','independent_ad.py','physiology.py','native_table.py',
             'source_integrity.py','controls.py','statistics.py']:
    raw=(R/'paper15_r1'/name).read_bytes()
    (P/name).write_bytes(raw)
    copied.append(dict(file=name,original_sha256=hashlib.sha256(raw).hexdigest(),
                       origin='paper15_r1/'+name,changes_at_copy='NONE'))
(P/'__init__.py').write_text('"""Frozen P15 Final source/C preparation and conditional one D assessment."""\n')
(P/'.gitignore').write_text('work/\n__pycache__/\n*.pyc\n')
(P/'requirements.txt').write_bytes((R/'paper15_r1/requirements.txt').read_bytes())
(E/'REUSE_REGISTRATION.json').write_text(json.dumps(dict(files=copied,
    scope='Unchanged mathematics, source codec and numerical/statistical primitives. Final-role admission wrappers and named verdicts are separately versioned/reviewed before use.'),indent=2)+'\n')
original=(R/'ops/daily-operations.md').read_bytes()
prefix=('# Current mission: P15-M6-INDEPENDENT-FINAL-VALIDATION\n\n'
        'Prospectively registered Prompt4 at exactBASE47608d2db5bae32b150e6fccd9567c059fe43e63;311original obligations frozen. '
        'Final source/native metadata preparation now authorized for original8reserved mice, then reviewed trusted C-only extraction/calibration. '
        'No D neural scientific values before complete independent pre-D admission; one D batch conditional only. '
        'Original M1/R1/Development/historical failures preserved; no Development rerun, Final search or Prompt5/PDF. '
        'Current Final source/C/D gates NOT YET RUN. Evidence:ops/evidence/2026-10-18/p15-m6-independent-final-validation.\n\n---\n')
(R/'ops/daily-operations.md').write_bytes(prefix.encode()+original)
print('Versioned8reviewedprimitive modules; source/C/D execution still pending')
