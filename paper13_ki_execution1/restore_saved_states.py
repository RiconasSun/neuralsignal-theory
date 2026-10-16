"""Restore only original hash-bound A/C/B/E derived evidence, never raw/D data."""
import json
from pathlib import Path
import zipfile
from .source import P,ROOT,sha

E=ROOT/'ops/evidence/2026-10-16/p13-ki-pl-science-first-execution'


def restore(root,manifest):
    root=Path(root).resolve();archive=root/manifest['archive_file']
    if sha(archive.read_bytes())!=manifest['archive_sha256']:raise ValueError('Saved archive checksum mismatch')
    entries=manifest['entries'];names=[a['path'] for a in entries]
    if len(names)!=len(set(names)):raise ValueError('Duplicate saved-state entries')
    allowed={'A':'training_states','C':'training_states','B':'development_B','E':'exploratory_E'}
    payloads={}
    with zipfile.ZipFile(archive) as z:
        if len(z.namelist())!=len(names) or set(z.namelist())!=set(names):raise ValueError('Archive entry roster mismatch')
        for entry in entries:
            name=entry['path'];partition=entry['partition']
            if partition not in allowed:raise PermissionError('D or unregistered partition prohibited')
            expected=f'paper13_ki_execution1/work/{allowed[partition]}/{entry["mouse_id"]}.npz'
            if name!=expected or not (root/name).resolve().is_relative_to(root/'paper13_ki_execution1/work'):
                raise PermissionError('Saved-state path outside registered ignored evidence destination')
            raw=z.read(name)
            if len(raw)!=entry['bytes'] or sha(raw)!=entry['sha256']:raise ValueError('Saved state payload mismatch')
            payloads[name]=raw
    restored=0
    # Entire archive verified before creating any destination. Existing bytes never overwritten.
    for name,raw in payloads.items():
        target=root/name
        if target.exists():
            if target.read_bytes()!=raw:raise ValueError('Existing saved state differs; preserved without overwrite: '+name)
        else:
            target.parent.mkdir(parents=True,exist_ok=True)
            with target.open('xb') as f:f.write(raw)
            restored+=1
    return {'verified_original_saved_states':len(entries),'restored_missing_original_files':restored,
        'new_source_extraction':False,'new_fitting':False,'final_D_states':0}


def main():
    manifest=json.loads((E/'SAVED_DERIVED_STATES_MANIFEST.json').read_text(encoding='utf8'))
    if len(manifest['entries'])!=39:raise ValueError('Expected exact19A/C+10B+10E original evidence bundles')
    print(json.dumps(restore(ROOT,manifest)))


if __name__=='__main__':main()
