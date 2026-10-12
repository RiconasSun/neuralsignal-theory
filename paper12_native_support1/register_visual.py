import json
from datetime import datetime,timezone
from register import HERE,sha,verify
if __name__=='__main__':
    verify()
    paths=['VISUAL_CLOCK_PROTOCOL.json','metadata/sdk_stimulus_sync_source.receipt','metadata/sdk_frame_clock_source.receipt']
    with (HERE/'visual_registration.json').open('x') as out:
        json.dump({'utc':datetime.now(timezone.utc).isoformat(),'sha256':{p:sha(HERE/p) for p in paths}},out,indent=2,sort_keys=True)
    print('Visual sync-only protocol/source registered before visual bit decoding.')
