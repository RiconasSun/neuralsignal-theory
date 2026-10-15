"""Host package dependency, pinned to the original scientific selection version."""
import hashlib
import importlib.util
from pathlib import Path

VERSION = 'P12-PREDICTIVE-V2-original-selection'
SHA256 = '9a36e1c29ca9acc2e6b4e8534489c8730f68d3db313ab8b2fc2b40a1930d9d4e'

def load_views():
    path = Path(__file__).resolve().parents[1] / 'paper12_predictive_v2' / 'selection.py'
    if path.is_symlink() or getattr(path.lstat(), 'st_file_attributes', 0) & 0x400:
        raise PermissionError('SELECTION_LINK_FORBIDDEN')
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != SHA256:
        raise PermissionError('SELECTION_VERSION_HASH_MISMATCH')
    spec = importlib.util.spec_from_file_location('paper12_predictive_v2.selection', path)
    module = importlib.util.module_from_spec(spec)
    # Execute exactly the authenticated bytes; do not consult a cached .pyc/module.
    exec(compile(raw, str(path), 'exec'), module.__dict__)
    return module.views
