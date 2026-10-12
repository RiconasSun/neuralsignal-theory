"""Compress generated metadata losslessly, preserving original bytes locally."""
import gzip
import json
from register import HERE,sha

if __name__=='__main__':
    paths=list((HERE/'metadata/native_headers').glob('*.json'))+list((HERE/'metadata').glob('channel_anatomy_page_*.receipt'))
    inventory=[]
    for path in paths:
        relative=path.relative_to(HERE)
        archive=HERE/'native_cache'/relative
        path.resolve().relative_to(HERE.resolve());archive.resolve().relative_to(HERE.resolve())
        packed=path.with_name(path.name+'.gz')
        data=path.read_bytes();compressed=gzip.compress(data,mtime=0)
        if gzip.decompress(compressed)!=data:raise RuntimeError('Compression parity failure')
        packed.write_bytes(compressed)
        inventory.append({'logical_path':relative.as_posix(),'original_sha256':sha(path),'compressed_sha256':sha(packed),
                          'original_bytes':len(data),'compressed_bytes':len(compressed)})
        archive.parent.mkdir(exist_ok=True,parents=True)
        if archive.exists():raise RuntimeError('Never replace archived metadata')
        path.rename(archive)
    (HERE/'metadata/compact_manifest.json').write_text(json.dumps(inventory,indent=2,sort_keys=True))
    print(json.dumps({'files':len(inventory),'original_bytes':sum(r['original_bytes'] for r in inventory),
                      'compressed_bytes':sum(r['compressed_bytes'] for r in inventory)}))
