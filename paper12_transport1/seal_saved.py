"""Seal public saved inputs; exclude replay, runtime and private contents."""
import common as r


def main():
    r.verify()
    names=[]
    for path in r.HERE.rglob('*'):
        if not path.is_file():continue
        relative=path.relative_to(r.HERE)
        if any(part in ('replay','__pycache__','.private') for part in relative.parts):continue
        if path.suffix=='.pyc' or relative.as_posix()=='final_manifest.json':continue
        names.append(relative.as_posix())
    r.save(r.HERE/'final_manifest.json',dict(scope='Public saved recovery evidence only; no private artifacts',
        sha256={name:r.sha(r.HERE/name) for name in sorted(names)}),True)
    print(dict(sealed_public_files=len(names),final_manifest_sha256=r.sha(r.HERE/'final_manifest.json')))


if __name__=='__main__':main()
