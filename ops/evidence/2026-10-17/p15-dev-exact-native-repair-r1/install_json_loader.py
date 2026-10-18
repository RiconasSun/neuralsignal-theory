"""Bind versioned orchestrators to lossless shared decoder; equations unchanged."""
from pathlib import Path
P=Path(__file__).resolve().parents[4]/'paper15_r1'
for path in P.glob('*.py'):
    if path.name in ('source.py','native_table.py') or path.name.startswith('test_'):continue
    text=path.read_text()
    if 'json.loads(' not in text:continue
    text=text.replace('json.loads(','load_json(')
    lines=text.splitlines();at=1 if lines[0].startswith('"""') else 0
    lines.insert(at,'from .source import load_json')
    path.write_text('\n'.join(lines)+'\n')
print('Lossless JSON decoder bound to versioned orchestration')
