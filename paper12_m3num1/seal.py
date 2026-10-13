"""Seal public saved evidence; omit custody, replay and transient caches."""
import study as r
from closure_verify import verify as verify_history


def main():
    verify_history()
    from saved_links import verify
    verify()
    paths=[]
    for p in r.HERE.rglob('*'):
        if not p.is_file():continue
        relative=p.relative_to(r.HERE)
        if any(x in relative.parts for x in ('exports','.private','wrapper-work','__pycache__','replay')):continue
        if p.name=='final_manifest.json':continue
        paths.append(p)
    r.save(r.HERE/'final_manifest.json',dict(sha256={p.relative_to(r.HERE).as_posix():r.sha(p) for p in sorted(paths)},
        scope='Public code, reports, saved outputs and execution logs only; no neural data or secrets'))
    print('PUBLIC_EVIDENCE_SEALED',len(paths))


if __name__=='__main__':main()
