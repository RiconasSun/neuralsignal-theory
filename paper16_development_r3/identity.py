"""R3 append-only identities. No neural reader or mathematical worker imports."""
from pathlib import Path
import hashlib,json,os
R=Path(__file__).resolve().parents[1];P=R/'paper16_development_r3'
E=R/'ops/evidence/2026-10-19/p16-m3-m5-metadata-compat-and-development-r3'
BASE='e740f6ac80ad1348a393c889fcf20778e9d24523'
MISSION='P16-M3-M5-METADATA-COMPAT-AND-DEVELOPMENT-R3'
class ProvenanceStop(RuntimeError):pass
class ContractStop(RuntimeError):pass
def load(path):return json.loads(Path(path).read_bytes())
def sha(path):
    with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def once(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x',encoding='utf8',newline='\n') as f:
        json.dump(value,f,indent=2,allow_nan=False);f.write('\n');f.flush();os.fsync(f.fileno())
def verify_pins():
    for name,digest in load(P/'SOURCE_PINS.json')['files'].items():
        if not (R/name).is_file() or sha(R/name)!=digest:raise ProvenanceStop('Frozen input identity: '+name)
def records():
    return sorted([r for r in load(R/'paper16_source_r4/SOURCE_AND_PHYSIOLOGY_ACCOUNT.json')['sources'] if r['selection']['admitted']],key=lambda r:int(r['source']['mouse_id']))
def exact_record(record):
    if record not in records():raise ProvenanceStop('Only the exact 27 admitted Development source records are permitted')
def check(path,digest):
    if not Path(path).is_file() or sha(path)!=digest:raise ProvenanceStop('Missing or corrupt source reference: '+str(path))
