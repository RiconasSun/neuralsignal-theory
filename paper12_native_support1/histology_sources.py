import json
from sources import fetch
from register import HERE,ROOT,verify

if __name__=='__main__':
    verify()
    rows=json.loads((ROOT/'paper12/metadata/allen_sessions.receipt').read_text())['msg']
    ids=','.join(r['specimen_id'] for r in rows)
    criteria="model::ImageSeries,rma::criteria,specimen[id$in"+ids+"],rma::options[tabular$eq'image_series.id,specimen_id'][num_rows$eq'all']"
    body,r=fetch('histology_image_series','https://api.brain-map.org/api/v2/data/query.json',{'criteria':criteria})
    data=json.loads(body)
    print(json.dumps({k:v for k,v in data.items() if k!='msg'}))
    if data.get('success'):
        if len(data['msg'])!=data['total_rows'] or any(set(row)-{'id','specimen_id'} for row in data['msg']):raise RuntimeError('Histology provenance projection mismatch')
        print('Public anatomical image-series rows:',len(data['msg']))
    else:print('Projected image-series route unverified; not proof of no histology')
    pin=json.loads((HERE/'source_pins.json').read_text())['sdk']
    fetch('sdk_frame_clock_source','https://raw.githubusercontent.com/AllenInstitute/AllenSDK/'+pin+'/allensdk/brain_observatory/ecephys/file_io/ecephys_sync_dataset.py')
