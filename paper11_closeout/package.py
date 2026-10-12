"""Bundle the manuscript track without raw data or reproduction scratch files."""
import json
import shutil
import zipfile
from pathlib import Path
from freeze import HERE, ROOT, sha, load

target=HERE/'P11_MANUSCRIPT_PACKAGE.zip'
license_source=ROOT/'paper11/results/M2/DERIVED_DATA_LICENSE.txt'
freeze=load(HERE/'evidence_freeze.json')
assert sha(license_source)==freeze['previous_tracked_sha256']['paper11/results/M2/DERIVED_DATA_LICENSE.txt']
shutil.copyfile(license_source,HERE/'DATA_SOURCE_LICENSE.txt')
files=[p for p in HERE.rglob('*') if p.is_file() and not any(part in ('reproduction','__pycache__') for part in p.relative_to(HERE).parts)
       and p.name not in (target.name,'package_manifest.json')]
for path in files:
    assert HERE in path.parents
    assert path.suffix.lower() not in ('.nwb','.ncs','.nev','.ns5','.mat','.npz','.npy'),path
with zipfile.ZipFile(target,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as archive:
    for path in sorted(files):archive.write(path,path.relative_to(HERE).as_posix())
(HERE/'package_manifest.json').write_text(json.dumps({'zip_sha256':sha(target),'files':len(files),
      'payload_sha256':{p.relative_to(HERE).as_posix():sha(p) for p in files},
      'raw_data_included':False,'repository_checkout_required_for_reproduction':True,
      'manuscript_verdict':load(HERE/'evidence/gate_result.json')['manuscript_verdict'],
      'scientific_validation_pass':False},indent=2,sort_keys=True)+'\n',encoding='utf-8')
print('Manuscript delivery archive built:',len(files),'files;',target.stat().st_size,'bytes; no raw data.')
