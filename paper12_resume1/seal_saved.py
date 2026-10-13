import study as r


def main():
    r.verify()
    exclude={'.private','exports','replay','wrapper-work','__pycache__'}
    files=[p for p in r.HERE.rglob('*') if p.is_file() and not exclude.intersection(p.relative_to(r.HERE).parts)
           and p.name!='final_manifest.json' and not p.relative_to(r.HERE).as_posix().startswith('results/tests/')]
    r.save(r.HERE/'final_manifest.json',dict(sha256={p.relative_to(r.HERE).as_posix():r.sha(p) for p in sorted(files)},
        excludes='All neural/private/export content and changing replay/test logs',scope='Saved public evidence only'),True)
    print(dict(saved_public_files=len(files),manifest_sha256=r.sha(r.HERE/'final_manifest.json')))


if __name__=='__main__':main()
