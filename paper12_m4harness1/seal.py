import study as r
from closure_verify import verify


def main():
    verify(archive_required=True);files=[]
    for path in r.HERE.rglob('*'):
        if not path.is_file():continue
        relative=path.relative_to(r.HERE)
        if any(x in relative.parts for x in ('exports','.private','wrapper-work','__pycache__','replay')):continue
        if path.name=='final_manifest.json' or path.suffix=='.pyc':continue
        files.append(path)
    r.save(r.HERE/'final_manifest.json',dict(sha256={p.relative_to(r.HERE).as_posix():r.sha(p) for p in sorted(files)},
        scope='Public source, saved numerical tests and development metrics only; no neural arrays, private keys or live re-execution'))
    print('PUBLIC_REPAIR_TRACK_SEALED',len(files))


if __name__=='__main__':main()
