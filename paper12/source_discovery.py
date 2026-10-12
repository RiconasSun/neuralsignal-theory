"""Discover official public recording-header object names, never raw signals."""
import xml.etree.ElementTree as ET
from acquire import get
from register import verify

if __name__ == '__main__':
    verify()
    url = 'https://allen-brain-observatory.s3.us-west-2.amazonaws.com/'
    response, _ = get('allen_s3_root', url, {'list-type': '2', 'delimiter': '/'})
    root = ET.fromstring(response.content)
    ns = {'s': 'http://s3.amazonaws.com/doc/2006-03-01/'}
    print([el.text for el in root.findall('.//s:Prefix', ns)])
