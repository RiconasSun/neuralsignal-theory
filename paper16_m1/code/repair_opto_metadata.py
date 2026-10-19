import json
from .roster_metadata import P,E,sha,inspect,write_json
def main():
 reg=json.loads((E/'SOURCE_METADATA_REGISTRATION.json').read_text(encoding='utf8'));item=next(x for x in reg['objects'] if x['session_id']==737581020)
 policy=json.loads((E/'SOURCE_OPTO_TAG_REPAIR_REGISTRATION.json').read_text(encoding='utf8'));assert policy['session_id']==737581020
 reg['repair_registration_sha256']=sha(E/'SOURCE_OPTO_TAG_REPAIR_REGISTRATION.json')
 prior=sum(json.loads((P/f'metadata/{folder}/737581020.json').read_text(encoding='utf8'))['reserved_bytes'] for folder in ['roster_flashes','roster_flashes_repair1'])
 result=inspect(item,reg,P/'metadata/roster_flashes_repair2',prior);assert prior+result['reserved_bytes']<=4194304
 previous=json.loads((E/'ROSTER_METADATA_COMBINED.json').read_text(encoding='utf8'))
 sessions=[{**x,'path':'paper16_m1/metadata/roster_flashes_repair2/737581020.json','status':result['status'],'admitted':result.get('metadata_candidate_admitted')} if x['session_id']==737581020 else x for x in previous['sessions']]
 write_json(E/'ROSTER_METADATA_FINAL.json',{**previous,'metadata_attempts':63,'original_failures_retained':8,'current_complete':sum(x['status']=='COMPLETE' for x in sessions),'current_admitted':sum(bool(x['admitted']) for x in sessions),'transport_bytes':previous['transport_bytes']+result['transport_bytes'],'reserved_bytes':previous['reserved_bytes']+result['reserved_bytes'],'sessions':sessions})
if __name__=='__main__':main()
