"""Inventory every Allen raw object, without opening raw signal payloads."""
import json
import xml.etree.ElementTree as ET
from acquire import HERE, get
from audit import table
from register import verify

def main():
    verify()
    out = []
    for row in table('sessions'):
        sid = row['id']
        name = 'allen_raw_objects_' + sid
        path = HERE / 'metadata' / (name + '.receipt')
        if path.exists():
            content = path.read_bytes()
        else:
            res, _ = get(name, 'https://allen-brain-observatory.s3.us-west-2.amazonaws.com/',
                         {'list-type': '2', 'prefix': 'visual-coding-neuropixels/raw-data/' + sid + '/'})
            content = res.content
        root = ET.fromstring(content)
        ns = {'s': 'http://s3.amazonaws.com/doc/2006-03-01/'}
        if root.findtext('s:IsTruncated', namespaces=ns) != 'false':
            raise RuntimeError('Raw inventory truncated')
        objects = [{'key': e.findtext('s:Key', namespaces=ns), 'bytes': int(e.findtext('s:Size', namespaces=ns)),
                    'etag_not_assumed_checksum': e.findtext('s:ETag', namespaces=ns)}
                   for e in root.findall('s:Contents', ns)]
        out.append({'session_id': sid, 'objects': objects})
        print(json.dumps({'session': sid, 'objects': len(objects)}), flush=True)
    (HERE / 'metadata/allen_raw_inventory.json').write_text(json.dumps(out, indent=2))

if __name__ == '__main__': main()
