"""Bind actual unsigned S3 GET bodies to prospectively frozen object identities."""
import hashlib
import math


def verify_etag_bytes(data, etag, part_size=8*1024*1024):
    """IBL multipart8MiB evidence check; unknown layouts cannot pass by assumption."""
    if '-' not in etag:
        return hashlib.md5(data).hexdigest()==etag
    root,parts=etag.rsplit('-',1)
    if int(parts)!=math.ceil(len(data)/part_size):
        return False
    digests=b''.join(hashlib.md5(data[i:i+part_size]).digest() for i in range(0,len(data),part_size))
    return hashlib.md5(digests).hexdigest()==root


def conditional_download(client, bucket, file, pin, target):
    """If-Match prevents a HEAD/GET race; response identity checked before any write."""
    kwargs=dict(Bucket=bucket,Key=file['key'],IfMatch='"'+pin['etag']+'"')
    if pin.get('version_id') is not None:
        kwargs['VersionId']=pin['version_id']
    response=client.get_object(**kwargs)
    try:
        if (response['ETag'].strip('"')!=pin['etag'] or response['ContentLength']!=pin['bytes']
                or response.get('VersionId')!=pin.get('version_id')
                or ('VersionId' in response)!=pin['version_id_header_present']
                or response['LastModified'].isoformat()!=pin['last_modified']):
            raise ValueError('Conditional GET object identity differs from frozen pin')
        partial=target.with_name(target.name+'.partial')
        if target.exists() or partial.exists():
            raise FileExistsError('Preserve prior complete/partial source; no automatic retry')
        written=0
        with partial.open('xb') as output:
            for block in iter(lambda:response['Body'].read(8*1024*1024),b''):
                output.write(block);written+=len(block)
        if written!=pin['bytes']:
            raise ValueError('Truncated conditional source body; partial preserved')
        partial.rename(target)
    finally:
        response['Body'].close()
