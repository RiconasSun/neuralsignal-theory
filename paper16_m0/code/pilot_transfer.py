"""Frozen Development-only, no-retry NWB transfer with a durable payload ceiling."""
import datetime, os, urllib.request
from pathlib import Path
from .core import *
from .access_gate import verify_access_approval
from .http_metadata import sanitize_headers
P=Path(__file__).resolve().parents[1]; R=P.parent
E=R/'ops/evidence/2026-10-18/p16-visual-cortex-data-first-m0'

def utc(): return datetime.datetime.now(datetime.timezone.utc).isoformat()

def approved_pilots():
    pilots=read_json(P/'results/PILOT_METADATA_SELECTION.json')
    roles=read_json(P/'results/ROLE_ALLOCATION.json')
    if not 0<len(pilots)<=2: raise ValueError('Pilot bound')
    for p in pilots:
        role=[r for r in roles if r['mouse_id']==p['mouse_id']]
        if len(role)!=1 or role[0]['group']!='Development' or p['group']!='Development': raise ValueError('Final denied')
        if role[0]['session_id']!=p['session_id'] or role[0]['probe_id']!=p['probe_id']: raise ValueError('Role identity mismatch')
    return pilots

def pin_objects():
    target=P/'results/PILOT_OBJECT_FREEZE.json'
    if target.exists(): raise FileExistsError('Object freeze immutable')
    pinned=[]
    for p in approved_pilots():
        req=urllib.request.Request(p['download_url'], method='HEAD')
        with urllib.request.urlopen(req,timeout=90) as res:
            h=sanitize_headers(res.headers); size=int(res.headers['Content-Length']); etag=res.headers.get('ETag')
            if size!=p['declared_bytes'] or etag!=p['prior_etag']: raise ValueError('Current object differs from historical descriptor')
            pinned.append({**p,'resolved_url':res.url,'headers':h,'etag':etag,'content_length':size,'pinned_at':utc()})
    dump_json(target,{'objects':pinned,'roles_sha256':sha256(P/'results/ROLE_ALLOCATION.json'),'metadata_selection_sha256':sha256(P/'results/PILOT_METADATA_SELECTION.json'),'registration_sha256':sha256(P/'FEASIBILITY_REGISTRATION.json'),'metadata_only':True,'spike_arrays_opened':0})

def claim_attempt(path,value):
    import json
    fd=os.open(path,os.O_CREAT|os.O_EXCL|os.O_WRONLY)
    with os.fdopen(fd,'wb') as out:
        out.write((json.dumps(value,indent=2)+'\n').encode()); out.flush(); os.fsync(out.fileno())

def download():
    freeze=read_json(P/'results/PILOT_OBJECT_FREEZE.json')
    verify_access_approval(R)
    if freeze['roles_sha256']!=sha256(P/'results/ROLE_ALLOCATION.json'): raise ValueError('Roles altered')
    budget=TransferBudget(P/'results/PAYLOAD_LEDGER.json')
    # Metadata is a separately capped20MB allowance; all body requests including failed ones count.
    if not budget.path.exists():
        metadata_bytes=sum(read_json(f).get('bytes',0) for f in (P/'metadata').glob('*.json') if read_json(f).get('url'))
        budget.charge(max(20_000_000,metadata_bytes),'actual newly acquired metadata bodies or20MB floor')
    for p in freeze['objects']:
        if p['session_id'] not in {x['session_id'] for x in approved_pilots()}: raise ValueError('Unapproved session')
        dest=P/'work'/f"session_{p['session_id']}.nwb"; receipt=P/'results'/f"TRANSFER_{p['session_id']}.json"
        if receipt.exists() or dest.exists() or dest.with_suffix('.partial').exists(): raise FileExistsError('Attempt already exists; no silent retry')
        if read_json(budget.path)['bytes']+p['content_length']>budget.ceiling: raise ValueError('Remaining ceiling insufficient')
        claim_attempt(receipt,{'status':'STARTED','time':utc(),'session_id':p['session_id'],'bytes_written':0,'object_freeze_sha256':sha256(P/'results/PILOT_OBJECT_FREEZE.json')})
        budget.charge(p['content_length'],f"full-object conservative reservation BEFORE GET {p['session_id']}")
        part=dest.with_suffix('.partial'); received=0
        try:
            req=urllib.request.Request(p['resolved_url'],headers={'If-Match':p['etag']})
            with urllib.request.urlopen(req,timeout=90) as res, part.open('xb') as out:
                if int(res.headers['Content-Length'])!=p['content_length'] or res.headers.get('ETag')!=p['etag']: raise ValueError('GET identity mismatch')
                while True:
                    block=res.read(min(4*1024*1024,p['content_length']-received+1))
                    if not block: break
                    out.write(block); received+=len(block)
                    if received>p['content_length']: raise ValueError('Overlong source object')
                out.flush(); os.fsync(out.fileno())
            if received!=p['content_length']: raise ValueError('Truncated source object')
            os.replace(part,dest)
            dump_json(receipt,{'status':'COMPLETE','time':utc(),'session_id':p['session_id'],'bytes_written':received,'sha256':sha256(dest),'object_freeze_sha256':sha256(P/'results/PILOT_OBJECT_FREEZE.json'),'spike_arrays_decoded':False})
            print('TRANSFER COMPLETE',p['session_id'],received,flush=True)
        except Exception as exc:
            dump_json(receipt,{'status':'FAILED','time':utc(),'session_id':p['session_id'],'bytes_written':received,'error_type':type(exc).__name__,'error':str(exc),'partial_preserved':part.exists()})
            raise

if __name__=='__main__':
    import sys
    {'pin':pin_objects,'download':download}[sys.argv[1]]()
