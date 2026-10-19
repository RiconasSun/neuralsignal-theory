"""Exactly seven registered metadata-parser failures; no model/array access changes."""
import concurrent.futures,json
from .roster_metadata import P,E,sha,inspect,write_json
def main():
 reg=json.loads((E/'SOURCE_METADATA_REGISTRATION.json').read_text(encoding='utf8'));repair=json.loads((E/'SOURCE_TAG_REPAIR_REGISTRATION.json').read_text(encoding='utf8'))
 reg['repair_registration_sha256']=sha(E/'SOURCE_TAG_REPAIR_REGISTRATION.json')
 required=set(repair['failed_original_sessions']);assert len(required)==7
 jobs=[]
 for item in reg['objects']:
  if item['session_id'] not in required:continue
  old=json.loads((P/'metadata/roster_flashes'/f"{item['session_id']}.json").read_text(encoding='utf8'))
  assert old['status']=='SOURCE_METADATA_UNRESOLVED' and old['error']=='ValueError: Unknown global invalid tags'
  jobs.append((item,old['reserved_bytes']))
 assert len(jobs)==7
 directory=P/'metadata/roster_flashes_repair1'
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:repaired=list(pool.map(lambda pair:inspect(pair[0],reg,directory,pair[1]),jobs))
 combined=[]
 for item in reg['objects']:
  sid=item['session_id'];path=directory/f'{sid}.json' if sid in required else P/'metadata/roster_flashes'/f'{sid}.json'
  result=json.loads(path.read_text(encoding='utf8'));combined.append({'session_id':sid,'path':path.relative_to(P.parent).as_posix(),'status':result['status'],'admitted':result.get('metadata_candidate_admitted')})
 allattempts=[json.loads(p.read_text(encoding='utf8')) for folder in [P/'metadata/roster_flashes',directory] for p in folder.glob('*.json') if not p.name.endswith('.attempt.json')]
 for sid in required:assert sum(x['reserved_bytes'] for x in allattempts if x['session_id']==sid)<=4194304
 write_json(E/'ROSTER_METADATA_COMBINED.json',{'original_objects':55,'metadata_attempts':62,'original_failures_retained':7,'current_complete':sum(x['status']=='COMPLETE' for x in combined),'current_admitted':sum(bool(x['admitted']) for x in combined),'transport_bytes':sum(x['transport_bytes'] for x in allattempts),'reserved_bytes':sum(x['reserved_bytes'] for x in allattempts),'neural_arrays':0,'real_model_fits':0,'Final_neural_access':0,'sessions':combined})
if __name__=='__main__':main()
