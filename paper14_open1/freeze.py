"""Explicit final-candidate freeze; reproduction never regenerates this."""
import datetime
from .retrieve import P,write,sha

def main():
    hashes={f.relative_to(P).as_posix():sha(f.read_bytes()) for f in sorted((P/'sources').rglob('*')) if f.is_file()}
    write(P/'SOURCE_FREEZE.json',dict(scope='Saved official metadata/documents and raw receipts; no neural data',hashes=hashes))
    payload={}
    for f in sorted(P.rglob('*')):
        parts=f.relative_to(P).parts
        if f.is_file() and not {'work','__pycache__'}&set(parts) and f.name!='CLOSEOUT_FREEZE.json':payload[f.relative_to(P).as_posix()]=sha(f.read_bytes())
    write(P/'CLOSEOUT_FREEZE.json',dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),scientific_protocol_frozen=False,scientific_decision='SOURCE_OR_TIMING_INCONCLUSIVE',hashes=payload))
    print('Frozen',len(hashes),'source/receipt files and',len(payload),'payload files; no scientific protocol activation.')

if __name__=='__main__':main()
