"""Exact frozen pilot inventory only; official unsigned ONE S3 downloader."""
import argparse,datetime,hashlib,json,os
from pathlib import Path
from .coverage import P,dump

def digest(path,kind):
    h=hashlib.new(kind)
    with path.open('rb') as f:
        for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
    return h.hexdigest()

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--size',choices=['small','large'],required=True);args=ap.parse_args()
    os.environ['TQDM_DISABLE']='1'
    from one.remote.aws import s3_download_file,get_s3_public
    freeze=json.loads((P/'PILOT_FILE_FREEZE.json').read_text(encoding='utf8'))
    ids=json.loads((P/'PILOT_IDENTITY_FREEZE.json').read_text(encoding='utf8'))['pilots']
    assert len(ids)<=2 and all(x['allocation']=='DEVELOPMENT' for x in ids)
    allowed={x['eid'] for x in ids}; assert all(x['eid'] in allowed for x in freeze['files'])
    assert freeze['total_bytes']<=1200000000
    receipt=P/'results/FILE_RECEIPTS.json';records=json.loads(receipt.read_text(encoding='utf8')) if receipt.exists() else []
    s3,bucket=get_s3_public()
    for row in freeze['files']:
        if (row['bytes']>=100000000)!=(args.size=='large'):continue
        target=P/'work/native'/row['eid']/Path(row['key']).name
        done=next((r for r in records if r['key']==row['key'] and r.get('status')=='COMPLETE'),None)
        if done:
            assert target.exists() and target.stat().st_size==row['bytes'] and digest(target,'sha256')==done['sha256']
            continue
        attempts=sum(r['key']==row['key'] for r in records)
        assert attempts<2
        # Count conservative full-file reservation for every attempted download, including failures.
        assert sum(r['reserved_bytes'] for r in records)+row['bytes']<=1200000000
        r=dict(key=row['key'],subject=row['subject'],eid=row['eid'],role=row['role'],reserved_bytes=row['bytes'],
            attempt=attempts+1,status='STARTED',started_at=datetime.datetime.now(datetime.timezone.utc).isoformat())
        records.append(r);dump(receipt,records);target.parent.mkdir(parents=True,exist_ok=True)
        try:
            s3_download_file(row['key'],target,s3=s3,bucket_name=bucket,overwrite=False)
            assert target.stat().st_size==row['bytes']
            md5=digest(target,'md5'); assert '-' in row['etag'] or md5==row['etag']
            r.update(status='COMPLETE',sha256=digest(target,'sha256'),md5=md5,completed_at=datetime.datetime.now(datetime.timezone.utc).isoformat())
            dump(receipt,records);print(row['subject'],row['role'],row['bytes'],'verified',flush=True)
        except Exception as exc:
            r.update(status='FAILED',error=type(exc).__name__+': '+str(exc));dump(receipt,records);raise
if __name__=='__main__':main()
