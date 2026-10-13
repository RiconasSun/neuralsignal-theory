import study as r
from closure_verify import verify


def main():
    verify();files=[]
    for p in r.HERE.rglob('*'):
        if not p.is_file():continue
        path=p.relative_to(r.HERE)
        if any(x in path.parts for x in ('exports','.private','wrapper-work','__pycache__','replay')) or p.name=='final_manifest.json' or p.suffix=='.pyc':continue
        files.append(p)
    r.save(r.HERE/'final_manifest.json',dict(sha256={p.relative_to(r.HERE).as_posix():r.sha(p) for p in sorted(files)},scope='Public saved evidence only; no neural arrays, protected weights, private keys or real experiment replay'))
    print('PUBLIC_OFFSET_RECOVERY_SEALED',len(files))


if __name__=='__main__':main()
