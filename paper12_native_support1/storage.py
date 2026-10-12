"""Lossless compact metadata storage; decompression never opens physiology."""
import gzip
import json
from pathlib import Path

def bytes_for(path):
    path=Path(path)
    if path.exists():return path.read_bytes()
    packed=Path(str(path)+'.gz')
    return gzip.decompress(packed.read_bytes())
def load(path):return json.loads(bytes_for(path))
def logical_paths(directory,pattern):
    directory=Path(directory)
    return sorted(set(directory.glob(pattern))|{Path(str(p)[:-3]) for p in directory.glob(pattern+'.gz')})
