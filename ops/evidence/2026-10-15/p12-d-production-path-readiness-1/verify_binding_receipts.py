"""Independent saved SYN public signature, source/output and durable-chain audit."""
import hashlib
import json
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

E=Path(__file__).resolve().parent;ROOT=E.parents[3];ARCHIVE=E/'synthetic_2_integrity';SAVED=ROOT/'paper12_controls1/jobs/saved_v2_9546086888504515998/exports/saved'

def require(value,label):
    if not value:raise RuntimeError(label)
def pairs(items):
    out={}
    for k,v in items:
        require(k not in out,'DUPLICATE_JSON_KEY');out[k]=v
    return out
def read(p):return json.loads(Path(p).read_text(),object_pairs_hook=pairs,parse_constant=lambda x:(_ for _ in ()).throw(ValueError('NONFINITE_JSON')))
def canonical(v):return json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
def digest(v):return hashlib.sha256(v).hexdigest()
def sha(p):return digest(Path(p).read_bytes())

def main():
    for name,value in read(ARCHIVE/'inventory.json').items():require(sha(ARCHIVE/name)==value,'ARCHIVED_PUBLIC_BINDING:'+name)
    anchor=read(ARCHIVE/'anchor.json');approval=read(ARCHIVE/'approval.json');body=approval['body'];authority=read(ARCHIVE/'synthetic_authority_public.json')
    require(body['realm']==anchor['realm']==authority['realm']=='SYNTHETIC_D','SYN_ONLY_SIGNATURE')
    require(authority['public_key_hex']==anchor['authority_public'] and body['mission']==authority['mission']==anchor['mission']=='P12-D-PRODUCTION-PATH-READINESS-1' and body['base']==authority['base']==anchor['base']=='76b19508a5a0728e500ff2e5f9c959309fbf967e','PUBLIC_SYN_AUTHORITY_BINDING')
    Ed25519PublicKey.from_public_bytes(bytes.fromhex(authority['public_key_hex'])).verify(bytes.fromhex(approval['signature']),canonical(body))
    c=read(ARCHIVE/'C_state_manifest.json');require(c['synthetic'] is True and c['cohort']==body['cohort'] and len(c['cohort'])==13 and digest(canonical(c))==body['C_manifest_sha256'],'GENUINE_SYN_C_MANIFEST')
    require(c['artifact_sha256']['complete_states.npz']=='abb9f7537ff1b03210487227d3b23e6b44200d19f4d2bf56d73bfe67b241135a','EXACT_ORIGINAL_SYN_MODEL_BUNDLE')
    for name,value in body['artifacts'].items():
        require(Path(name).name==name,'BASENAME_ARTIFACT_ROSTER')
        path=ARCHIVE/name if (ARCHIVE/name).is_file() else SAVED/name
        require(path.parent==ARCHIVE or name in c['artifact_sha256'],'EXACT_SAVED_SYN_DEPENDENCY')
        require(sha(path)==value,'SIGNED_ARTIFACT:'+name)
    bound=digest(canonical(body));genesis=read(ARCHIVE/'ledger/genesis.json');previous=digest(canonical(genesis));require(previous==anchor['genesis_sha256'],'GENESIS_HASH')
    raw=(ARCHIVE/'ledger/events.jsonl').read_bytes();require(raw.endswith(b'\n'),'COMPLETE_LEDGER_LINE');events=[json.loads(line) for line in raw.splitlines()];require(len(events)==3,'EXACT_THREE_LEDGER_STATES')
    for index,(event,state) in enumerate(zip(events,('GENESIS','INTENT','CONSUMED'))):
        require(event['sequence']==index and event['state']==state and event['previous']==previous and event['authorization_id']==body['authorization_id'] and event['binding']==(anchor['genesis_sha256'] if index==0 else bound),'HASH_CHAIN_STATE:'+state);previous=digest(canonical(event))
    for path in ('ledger/intent.json','ledger/consumed.json','independent_consumption_fence.json','ledger/delivery_started.json','ledger/delivery_complete.json'):
        value=read(ARCHIVE/path);require(value['binding']==bound and value['authorization_id']==body['authorization_id'],'DURABLE_BINDING:'+path)
    require(read(ARCHIVE/'ledger/consumed.json')['ledger_tail']==previous,'CONSUMED_CHAIN_TAIL')
    delivery=read(ARCHIVE/'delivery_manifest.json');completion=read(ARCHIVE/'ledger/delivery_complete.json');require(sha(ARCHIVE/'delivery_manifest.json')==completion['delivery_manifest_sha256'],'COMPLETE_EXPORTED_MANIFEST_HASH')
    require(delivery['realm']=='SYNTHETIC_D' and delivery['binding']==bound and delivery['principal']==body['principal'] and delivery['keys_exported'] is False and delivery['unrestricted_vectors_exported'] is False and delivery['complete'] is True and set(delivery['sessions'])==set(c['cohort']),'EXACT_SELECTED_UNIT_DELIVERY')
    partition=read(ARCHIVE/'partition_manifest.json');catalog=read(ARCHIVE/'source_catalog.json')
    for mouse in c['cohort']:
        d=delivery['sessions'][mouse];require(d['trial_ids']==partition['D_trial_ids'][mouse] and len(d['trial_ids'])==240 and d['source_ciphertext_sha256']==catalog['sessions'][mouse]['ciphertext_sha256'],'EXACT_SOURCE_D_MASK_HASH:'+mouse)
        for region in ('CA1','DG'):
            case=next(v for v in c['cases'] if v['mouse_id']==mouse and v['region']==region and v['view']=='primary');require(d['unit_ids'][region]==case['unit_ids'] and len(d['unit_ids'][region])==32,'SEALED_C_UNIT_ORDER:'+mouse+region)
    print(json.dumps({'saved_SYN_signature_artifacts_ledger_source_output':'PASS','signed_artifacts':len(body['artifacts']),'mice':13,'public_metadata_only_plus_saved_SYN_model_hashes':True,'count_arrays_or_private_keys_read':False,'D_RELEASE_CONSUMED':False,'D_EVALUATION_EXECUTED':False},sort_keys=True))

if __name__=='__main__':main()
