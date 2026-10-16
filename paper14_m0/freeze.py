"""Explicit closeout packaging only; never called by saved reproduction."""
from .audit import P, write, sha, verify_inputs


def build():
    verify_inputs()
    metadata={str(p.relative_to(P)).replace('\\','/'):sha(p) for p in sorted((P/'metadata').rglob('*')) if p.is_file()}
    write(P/'METADATA_FREEZE.json',{'scope':'Exact public scalar/event/anatomy/support metadata snapshot; no neural arrays','hashes':metadata})
    files={str(p.relative_to(P)).replace('\\','/'):sha(p) for p in sorted(P.rglob('*')) if p.is_file() and 'work' not in p.parts and '__pycache__' not in p.parts and p.name!='CLOSEOUT_FREEZE.json'}
    write(P/'CLOSEOUT_FREEZE.json',{'mission':'P14-CONTEXT-DYNAMICS-DATA-FEASIBILITY','base':'fae4fa316bbb499a86949d496e6ba4f36380e29f','hashes':files})
    print('Frozen',len(metadata),'metadata files and',len(files),'M0 payload files; original input hashes preserved.')


if __name__=='__main__':build()
