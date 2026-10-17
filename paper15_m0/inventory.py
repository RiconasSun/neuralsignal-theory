"""Public unsigned ONE-supported S3 metadata listing for frozen pilots only."""
import datetime,json
from .coverage import P,dump
from one.remote.aws import get_s3_public

def main():
    s3,bucket=get_s3_public();client=s3.meta.client
    f=json.loads((P/'PILOT_IDENTITY_FREEZE.json').read_text(encoding='utf8'))
    for p in f['pilots']:
        dest=P/'source'/(p['eid']+'_s3.json')
        if dest.exists():continue
        prefix=f"{p['lab']}/Subjects/{p['subject']}/{p['date']}/{int(p['session_number']):03}/"
        response=client.list_objects_v2(Bucket=bucket,Prefix=prefix,MaxKeys=1000)
        if not response.get('KeyCount'):
            prefix='data/'+prefix
            response=client.list_objects_v2(Bucket=bucket,Prefix=prefix,MaxKeys=1000)
        assert not response.get('IsTruncated'), 'Bounded per-session metadata page exceeded'
        items=[dict(key=x['Key'],bytes=x['Size'],etag=x['ETag'].strip('"'),last_modified=x['LastModified'].isoformat()) for x in response.get('Contents',[])]
        dump(dest,dict(bucket=bucket,prefix=prefix,listed_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),objects=items))
        print(p['subject'],len(items),prefix)
        for x in items:
            if any(z in x['key'] for z in ['spikes.times','spikes.clusters','clusters.','channels.brain','trials.','wheel.','saturation','Saturation','ephysTime','recording']):
                print(x['key'],x['bytes'])

if __name__=='__main__':main()
