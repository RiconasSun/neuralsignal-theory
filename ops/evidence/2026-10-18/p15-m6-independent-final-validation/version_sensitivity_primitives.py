"""Copy exact registered case definitions/mask transformation; no arrays read."""
from pathlib import Path
import ast
R=Path(__file__).resolve().parents[4];P=R/'paper15_final1'
text=(R/'paper15_r1/sensitivities.py').read_text();tree=ast.parse(text)
nodes=[node for node in tree.body if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='CASES' for t in node.targets)
       or isinstance(node,ast.FunctionDef) and node.name=='metadata_case']
assert len(nodes)==2
lines=text.splitlines(keepends=True)
out='"""Unchanged M1 eleven cases and metadata masks; C-only preparation below."""\nimport copy\nimport numpy as np\n\n'
out+='\n\n'.join(''.join(lines[n.lineno-1:n.end_lineno]) for n in nodes)+'\n'
assert not (P/'sensitivities.py').exists();(P/'sensitivities.py').write_text(out)
