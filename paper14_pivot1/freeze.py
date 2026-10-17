"""Freeze an audited negative metadata decision; never activate a protocol."""
import datetime
from .retrieve import P,write,sha
def main():
    source={f.relative_to(P).as_posix():sha(f.read_bytes()) for f in sorted((P/'sources').rglob('*')) if f.is_file()}
    write(P/'SOURCE_FREEZE.json',dict(hashes=source,scope='Official release/license/identity metadata and static code; no neural payload'))
    payload={}
    for f in sorted(P.rglob('*')):
        if f.is_file() and not {'work','__pycache__'}&set(f.relative_to(P).parts) and f.name!='CLOSEOUT_FREEZE.json':payload[f.relative_to(P).as_posix()]=sha(f.read_bytes())
    write(P/'CLOSEOUT_FREEZE.json',dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),scientific_decision='DATA_INSUFFICIENT',full_scientific_protocol_frozen=False,hashes=payload))
    print('Frozen',len(source),'source/receipt files and',len(payload),'payload files; no scientific activation.')
if __name__=='__main__':main()
