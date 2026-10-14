"""Full working-byte Git blob preservation audit, no neural-array decoding."""
import hashlib
import study as r
def blob(p):
    length=p.stat().st_size;h=hashlib.sha1(b'blob '+str(length).encode()+b'\0')
    with p.open('rb') as f:
        for chunk in iter(lambda:f.read(1048576),b''):h.update(chunk)
    return h.hexdigest()
def main():
    old=r.load(r.HERE/'prior_git_manifest.json')['blob_sha1'];changed=[]
    for name,digest in old.items():
        if blob(r.ROOT/name)!=digest:changed.append(name)
    original=r.HERE/'original_daily_operations.md'
    if changed!=['ops/daily-operations.md'] or blob(original)!=old['ops/daily-operations.md'] or not (r.ROOT/'ops/daily-operations.md').read_bytes().endswith(original.read_bytes()):raise RuntimeError('HISTORICAL_EVIDENCE_CHANGED:'+str(changed))
    r.save(r.HERE/'preservation_audit.json',{'base':r.BASE,'prior_files':len(old),'unchanged':len(old)-1,'only_authorized_new_daily_prefix_changed':True,'original_daily_suffix_exact':True,'historical_scientific_failures_immutable':True,'all_prior_mathematical_and_gradient_audit_sources_unchanged':True,'original_daily_blob_sha1':blob(original)})
    print('ALL_PRIOR_BYTES_PRESERVED',len(old),'onlydailynewprefix')
if __name__=='__main__':main()
