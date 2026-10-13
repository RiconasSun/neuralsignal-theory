"""Read-only runtime/code provenance and custody DACL metadata, no neural decode."""
import study as r
from prepare import security


def main():
    a=security();target=r.HERE/'exports/runtime'
    source=list((r.PREVIOUS/'exports').glob('replay_probe_*/runtime'))
    if len(source)!=1:raise RuntimeError('RUNTIME_SOURCE_AMBIGUOUS')
    original={p.relative_to(source[0]).as_posix():r.sha(p) for p in source[0].rglob('*') if p.is_file()}
    copied={p.relative_to(target).as_posix():r.sha(p) for p in target.rglob('*') if p.is_file()}
    if original!=copied:raise RuntimeError('COPIED_RUNTIME_MISMATCH')
    paths=[r.HERE/'.private',r.HERE/'.private/source_canary.bin',r.HERE/'.private/key_canary.bin',r.HERE/'.private/training_issuer.json']
    for p in paths:a.check_acl(p)
    outputs=[]
    for job in (r.HERE/'exports').glob('P12Analysis.*'):
        if (job/'code').exists():
            for p in (job/'code').glob('*.py'):
                origin=r.OLD/p.name if p.name in ('baseline_fit.py','baseline_features.py','native_analysis_check.py') else r.HERE/p.name
                outputs.append(dict(job=job.name,file=p.name,sha256=r.sha(p),unchanged=r.sha(p)==r.sha(origin)))
    if not all(x['unchanged'] for x in outputs):raise RuntimeError('NATIVE_CODE_COPY_CHANGED')
    r.save(r.HERE/'results/runtime_provenance.json',dict(runtime_sha256=copied,runtime_source_matches=True,
        native_code=outputs,custody_acl_checked=True,protected_contents_decoded=False,
        source_requests=0,final_access=False))
    print('RUNTIME_BYTES_AND_CUSTODY_ACLS_VERIFIED')


if __name__=='__main__':main()
