"""Saved evidence and immutable bytes only; no real C/D loader or fitter."""
import hashlib
import json
import zipfile
import study as r
def main():
    r.verify();seal=r.load(r.HERE/'final_manifest.json')
    for name,h in seal['sha256'].items():
        if r.sha(r.ROOT/name)!=h:raise RuntimeError('CLOSEOUT_CHANGED:'+name)
    prior=r.load(r.HERE/'preservation_manifest.json')['tracked_working_bytes_sha256'];old=r.HERE/'historical_daily_operations.bin'
    for name,h in prior.items():
        if name=='ops/daily-operations.md':
            if r.sha(old)!=h or not (r.ROOT/name).read_bytes().endswith(old.read_bytes()):raise RuntimeError('DAILY_HISTORY')
        elif r.sha(r.ROOT/name)!=h:raise RuntimeError('HISTORICAL_BYTES_CHANGED:'+name)
    members=0
    for p in (r.HERE/'results').glob('*_archive.json'):
        m=r.load(p);archive=p.parent/m['archive']
        if r.sha(archive)!=m['archive_sha256']:raise RuntimeError('ARCHIVE_CHANGED')
        with zipfile.ZipFile(archive) as z:
            if sorted(z.namelist())!=sorted(m['member_sha256']):raise RuntimeError('ARCHIVE_MEMBER_ROSTER')
            for name,h in m['member_sha256'].items():
                if hashlib.sha256(z.read(name)).hexdigest()!=h:raise RuntimeError('ARCHIVE_MEMBER_CHANGED')
                members+=1
    handoff=r.load(r.HERE/'HANDOFF.json')
    if handoff['D_RELEASE_CONSUMED'] or handoff['D_EVALUATION_EXECUTED']:raise RuntimeError('FORBIDDEN_D_EXECUTION')
    print(json.dumps({'saved_reproduction':'PASS','preserved_files':len(prior),'archived_exact_receipts':members,'new_fits':0,'real_C_reads':0,'D_release':False,'D_evaluation':False,'engineering_result':handoff['ENGINEERING_CONTROL_PASS'],'C_result':handoff['REAL_C_CALIBRATION_PASS']}))
if __name__=='__main__':main()
