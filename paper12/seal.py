"""Seal saved metadata and final relevant source state, not scientific success."""
import json
from datetime import datetime, timezone
from audit import HERE
from register import sha, verify

if __name__=='__main__':
    verify()
    metadata = {p.relative_to(HERE).as_posix():sha(p) for p in sorted((HERE/'metadata').rglob('*')) if p.is_file()}
    candidates = list(HERE.glob('*')) + list((HERE/'archive').glob('*')) + list((HERE/'source_licenses').glob('*'))
    sources = {p.relative_to(HERE).as_posix():sha(p) for p in sorted(candidates)
               if p.suffix in ('.py','.ps1','.md') or p.name in ('protocol_M0.json','HEADER_POLICY.json','IBL_POLICY.json','mission.json')}
    sources.update({p.relative_to(HERE).as_posix():sha(p) for p in (HERE/'source_licenses').glob('*.txt')})
    result = {'utc':datetime.now(timezone.utc).isoformat(), 'metadata_sha256':metadata,
              'source_sha256':sources,
              'result_sha256':{p.relative_to(HERE).as_posix():sha(p) for p in sorted((HERE/'results').glob('*')) if p.is_file()},
              'full_physiological_object_checksums_verified':False}
    (HERE/'manifest.json').write_text(json.dumps(result,indent=2,sort_keys=True))
    print('Sealed',len(metadata),'metadata files and',len(sources),'source/report files')
