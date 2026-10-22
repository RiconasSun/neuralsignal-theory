"""Exact namespace copies; all mathematical source bytes remain unchanged."""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[4];P=R/'paper16_development_r5';old=R/'paper16_development_r4'
rows=[]
for name in ['features.py','models.py','panels.py','controls.py','optimizer.py','optim_child.py']:
    raw=(old/name).read_bytes();new=raw
    if name in ['optimizer.py','optim_child.py']:
        new=new.replace(b'paper16_development_r4',b'paper16_development_r5').replace(b'P16_R4_JOB',b'P16_R5_JOB')
    with (P/name).open('xb') as f:f.write(new)
    rows.append({'source':(old/name).relative_to(R).as_posix(),'source_sha256':hashlib.sha256(raw).hexdigest(),
                 'target':(P/name).relative_to(R).as_posix(),'target_sha256':hashlib.sha256(new).hexdigest(),
                 'permitted_replacements':[] if raw==new else ['paper16_development_r4 -> paper16_development_r5','P16_R4_JOB -> P16_R5_JOB'],
                 'mathematics_unchanged':True})
with (P/'MATHEMATICAL_COPY_PROOF.json').open('x',encoding='utf8') as f:json.dump({'files':rows},f,indent=2)
