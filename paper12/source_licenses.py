"""Preserve verbatim source licenses adjacent to cached source receipts."""
import base64
import json
from acquire import HERE

if __name__=='__main__':
    directory = HERE/'source_licenses'
    directory.mkdir(exist_ok=True)
    for source in ('allen','ibl'):
        record = json.loads((HERE/'metadata'/f'{source}_source_license.receipt').read_text())
        (directory/(source+'_LICENSE.txt')).write_bytes(base64.b64decode(record['content']))
    print('Verbatim third-party source licenses retained; not relicensed.')
