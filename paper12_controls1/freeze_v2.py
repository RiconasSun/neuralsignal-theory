"""Append-only final implementation identity, before any real C access."""
import study as r

def main():
    hashes=dict(r.verify()['source_sha256'])
    for pattern in ('*.py','*.ps1','SECURITY_ARCHITECTURE.md','SEALING_V2.md'):
        hashes.update({p.relative_to(r.ROOT).as_posix():r.sha(p) for p in r.HERE.glob(pattern)})
    r.save(r.HERE/'implementation_snapshot_v2.json',{'base':r.BASE,'mission':r.MISSION,'before_real_C':True,
        'real_D_authorization':False,'supersedes_for_engineering_approval':'implementation_snapshot.json',
        'prior_snapshot_sha256':r.sha(r.HERE/'implementation_snapshot.json'),'utc':r.datetime.now(r.timezone.utc).isoformat(),'sha256':hashes})
    print({'snapshot_v2_sha256':r.sha(r.HERE/'implementation_snapshot_v2.json'),'files':len(hashes)})
if __name__=='__main__':main()
