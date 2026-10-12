"""Server-projected channel anatomy; labels are not independent histology."""
import json
from sources import fetch
from register import HERE,verify

FIELDS='ecephys_channels.id,ecephys_probe_id,local_index,probe_horizontal_position,probe_vertical_position,anterior_posterior_ccf_coordinate,dorsal_ventral_ccf_coordinate,left_right_ccf_coordinate,structures.id as structure_id,structures.acronym as structure_acronym'

def main():
    verify()
    allowed={f.split(' as ')[-1].split('.')[-1] for f in FIELDS.split(',')}
    offset=0;total=None;identities=set()
    while total is None or offset<total:
        criteria="model::EcephysChannel,rma::include,structure,rma::options[tabular$eq'"+FIELDS+"'][num_rows$eq10000][start_row$eq"+str(offset)+"][order$eq'id']"
        body,receipt=fetch('channel_anatomy_page_'+str(offset),'https://api.brain-map.org/api/v2/data/query.json',{'criteria':criteria})
        data=json.loads(body)
        if not data['success'] or data['start_row']!=offset:raise RuntimeError('Failed anatomy page')
        if total is not None and total!=data['total_rows']:raise RuntimeError('Anatomy denominator changed mid-query')
        total=data['total_rows']
        if not data['msg']:raise RuntimeError('Empty anatomy page before completion')
        if any(set(row)-allowed for row in data['msg']):raise RuntimeError('Unexpected anatomy columns')
        for row in data['msg']:
            if row['id'] in identities:raise RuntimeError('Duplicate paged channel')
            identities.add(row['id'])
        offset+=len(data['msg'])
        print(json.dumps({'completed_channel_rows':offset,'total':total}),flush=True)
    (HERE/'metadata/anatomy_completion.json').write_text(json.dumps({'rows':len(identities),'pages':(offset+9999)//10000},indent=2))

if __name__=='__main__':main()
