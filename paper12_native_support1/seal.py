"""Bind future replay to exact audit metadata, source and recorded results."""
import json
from datetime import datetime,timezone
from register import HERE,sha,verify

if __name__=='__main__':
    verify()
    groups={}
    groups['metadata_sha256']={p.relative_to(HERE).as_posix():sha(p) for p in sorted((HERE/'metadata').rglob('*'))
                               if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc'}
    source=list(HERE.glob('*.py'))+list(HERE.glob('*.ps1'))+list(HERE.glob('*.md'))+list(HERE.glob('*POLICY*.json'))+list(HERE.glob('*PROTOCOL*.json'))
    source += [p for p in HERE.glob('*.json') if p.name!='manifest.json']+list((HERE/'source_licenses').glob('*'))
    groups['source_sha256']={p.relative_to(HERE).as_posix():sha(p) for p in sorted(set(source)) if p.is_file()}
    groups['results_sha256']={p.relative_to(HERE).as_posix():sha(p) for p in sorted((HERE/'results').rglob('*')) if p.is_file()}
    (HERE/'manifest.json').write_text(json.dumps({'utc':datetime.now(timezone.utc).isoformat(),**groups},indent=2,sort_keys=True))
    print({k:len(v) for k,v in groups.items()})
