"""Seal the stopped package; never rewrite prospective registration."""
import register as r


def main():
    r.verify()
    files = [p for p in r.HERE.rglob('*') if p.is_file() and p.name != 'seal.json'
             and not any(x in p.parts for x in ('__pycache__', 'replay', 'evidence', 'opaque_cache'))]
    r.save(r.HERE / 'seal.json', {'mission': r.MISSION,
                                'sha256': {p.relative_to(r.HERE).as_posix(): r.sha(p) for p in files}})
    print({'sealed_files': len(files), 'seal_sha256': r.sha(r.HERE / 'seal.json')})


if __name__ == '__main__':
    main()
