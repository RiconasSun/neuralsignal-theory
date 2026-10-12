import json
from datetime import datetime, timezone
from register import HERE, sha, verify

if __name__=='__main__':
    verify()
    files=[HERE/'CLOCK_POLICY.json',HERE/'source_pins.json']+[HERE/'metadata'/name for name in
           ('sdk_source_0.receipt','sdk_source_1.receipt','sdk_source_2.receipt','sdk_source_3.receipt','sdk_extra_0.receipt','sdk_extra_1.receipt','sdk_extra_2.receipt')]
    record={'utc':datetime.now(timezone.utc).isoformat(),
            'sha256':{p.relative_to(HERE).as_posix():sha(p) for p in files}}
    with (HERE/'clock_registration.json').open('x') as out:json.dump(record,out,indent=2,sort_keys=True)
    print('Prospective decoder policy and source definitions frozen.')
