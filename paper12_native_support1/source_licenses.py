from pathlib import Path
import json
from sources import fetch
from register import HERE
if __name__=='__main__':
    pins=json.loads((HERE/'source_pins.json').read_text())
    data,r=fetch('sorting_license_txt','https://raw.githubusercontent.com/AllenInstitute/ecephys_spike_sorting/'+pins['sorting']+'/LICENSE.txt')
    if r['status']!=200:raise RuntimeError('License source unavailable')
    out=HERE/'source_licenses';out.mkdir(exist_ok=True)
    (out/'sorting_LICENSE.txt').write_bytes(data)
    (out/'AllenSDK_LICENSE.txt').write_bytes((HERE/'metadata/sdk_source_5.receipt').read_bytes())
    print('Verbatim source licenses preserved, no relicensing.')
