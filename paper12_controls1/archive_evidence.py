"""Lossless public JSON receipts only; never copies keys, arrays or plaintext tensors."""
import zipfile
from pathlib import Path
import study as r
def archive(name,output):
    target=r.HERE/'results'/(name+'.zip');manifest={}
    files=sorted(p for p in Path(output).glob('*.json') if not p.name.startswith('private_'))
    if not files:raise RuntimeError('NO_RECEIPTS_TO_ARCHIVE')
    with zipfile.ZipFile(target,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for p in files:
            raw=p.read_bytes();z.writestr(p.name,raw);manifest[p.name]=__import__('hashlib').sha256(raw).hexdigest()
    r.save(r.HERE/'results'/(name+'_archive.json'),{'archive':target.name,'archive_sha256':r.sha(target),'member_sha256':manifest,
        'source_directory':str(Path(output).relative_to(r.HERE)),'scope':'Exact original public numerical/role JSON receipts; no array/key/cipher/source payload'})
    return target
def main():
    import sys
    archive(sys.argv[1],r.HERE/sys.argv[2])
if __name__=='__main__':main()
