"""Narrow versioned cache adapter edits; historical production source is untouched."""
from pathlib import Path
P=Path(__file__).resolve().parents[4]/'paper15_r1'
f=P/'reader.py';s=f.read_text();start=s.index('def neural_file(');end=s.index('\n\ndef run():',start)
s=s[:start]+'''def neural_file(row,file,s3=None):
    from .cached_source import cached_neural
    return cached_neural(row,file,s3)
'''+s[end:]
s=s.replace('    from one.remote.aws import get_s3_public\n','').replace('    s3,bucket=get_s3_public();assert bucket==BUCKET','    s3=None  # Read-only verified native source cache; no new source fetch')
f.write_text(s)
f=P/'selection.py';s=f.read_text().replace("        assert sha(path)==next(x for x in qc['files'] if x['key']==f['key'])['sha256']", "        rec=next(x for x in qc['files'] if x['key']==f['key'])\n        if 'original_path' in rec:path=R/rec['original_path']\n        assert sha(path)==rec['sha256']")
f.write_text(s)
f=P/'evaluation_support.py';s=f.read_text().replace("        assert sha(path)==receipt['sha256'];paths[f['role']]=path", "        if 'original_path' in receipt:path=R/receipt['original_path']\n        assert sha(path)==receipt['sha256'];paths[f['role']]=path")
f.write_text(s)
print('Versioned cache adapter complete; no source/math/data changed')
