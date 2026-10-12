"""Before-request source/reuse/role policy registration,without network access."""
from datetime import datetime, timezone
import subprocess
import common as r


def main():
    r.old.verify()
    if subprocess.check_output(['git','rev-parse','HEAD'], cwd=r.ROOT).decode().strip() != 'cf6321b7e3afadb212cc730c99f8cd972079b6d8':
        raise RuntimeError('RECOVERY_CHECKPOINT_CHANGED')
    files = subprocess.check_output(['git','ls-files','-z'], cwd=r.ROOT).decode().split('\0')
    animals = r.load(r.ROOT/'paper12_curated_v1/locks/animals.json')
    items = {x['session_id']:x for x in r.load(r.ROOT/'paper12/metadata/allen_header_capability.json')}
    reused = {}; source = {}
    for a in animals:
        sid=a['session_id']; item=items[sid]
        path=r.OLD/'results/M2/index2/sessions'/(sid+'.json')
        source[sid]=dict(file_id=item['file_id'],etag=item['etag'],bytes=int(item['content_range'].split('/')[-1]),
                        whole_file_sha256=None,raw_index_audit_sha256=r.sha(r.OLD/'results/index2/audit'/(sid+'.json')))
        if path.exists():
            reused[sid]=dict(receipt_sha256=r.sha(path),ciphertext_receipts=r.load(path)['ciphertext_receipts'])
    if len(reused)!=8:raise RuntimeError('EIGHT_SESSION_REUSE_DENOMINATOR_CHANGED')
    names=[r.HERE/x for x in ('mission.json','policy.json','.gitignore','common.py','register_recovery.py')]
    names += [r.ROOT/'ops/evidence/2026-10-12/p12-m2-transport-recovery-1/goldenstandards.md']
    record=dict(utc=datetime.now(timezone.utc).isoformat(),checkpoint='cf6321b7e3afadb212cc730c99f8cd972079b6d8',
                prior_sha256={p:r.sha(r.ROOT/p) for p in files if p and p!='ops/daily-operations.md'},
                amendment_sha256={p.relative_to(r.ROOT).as_posix():r.sha(p) for p in names},
                old_ops=(r.ROOT/'ops/daily-operations.md').read_text(encoding='utf-8'),
                sources=source,reuse=reused,original_timeout_sha256=r.sha(r.OLD/'results/M2/index2/failures/779839471.json'),
                new_source_requests=0,final_values_exposed_to_analysis=False,final_holdout_evaluated=False)
    r.save(r.HERE/'registration.json',record,True);r.verify()
    print('PROSPECTIVE_TRANSPORT_POLICY_AND26SOURCE_IDENTITIES_FROZEN;NO_SOURCE_REQUEST')


if __name__=='__main__':main()
