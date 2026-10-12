import study as r
from history_guard import verify


def main():
    verify();names=[]
    for path in r.HERE.rglob('*'):
        if not path.is_file():continue
        relative=path.relative_to(r.HERE)
        if any(part in ('.private','exports','replay','__pycache__') for part in relative.parts):continue
        if path.suffix=='.pyc' or relative.as_posix()=='final_manifest2.json':continue
        names.append(relative.as_posix())
    r.save(r.HERE/'final_manifest2.json',dict(sha256={name:r.sha(r.HERE/name) for name in sorted(names)},scope='Public synthetic-only study artifacts; first manifest/replay failure retained'),True)
    print(dict(public_files=len(names),manifest_sha256=r.sha(r.HERE/'final_manifest2.json')))


if __name__=='__main__':main()
