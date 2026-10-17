"""Checkpoint packaging only; never invoked by saved reproduction."""
from .retrieve import P,write,digest
from .audit import verify_inputs


def build():
    verify_inputs()
    sources={x.relative_to(P).as_posix():digest(x.read_bytes()) for x in sorted((P/'sources').rglob('*')) if x.is_file()}
    write(P/'SOURCE_FREEZE.json',{'scope':'Official source/metadata only; no signal data chunks','hashes':sources})
    payload={x.relative_to(P).as_posix():digest(x.read_bytes()) for x in sorted(P.rglob('*')) if x.is_file() and 'work' not in x.parts and '__pycache__' not in x.parts and x.name!='CLOSEOUT_FREEZE.json'}
    write(P/'CLOSEOUT_FREEZE.json',{'mission':'P14-M1-SOURCE-CONTRACT-AND-PROTOCOL-FREEZE','base':'9cb5568be20821f5487d8987ff484201ecc22632','scientific_protocol_frozen':False,'scientific_decision':'SOURCE_RIGHTS_BLOCKED','hashes':payload})
    print('Frozen',len(sources),'source/receipt files and',len(payload),'checkpoint payload files. Not a scientific protocol freeze.')


if __name__=='__main__':build()
