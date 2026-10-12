import json
from datetime import datetime,timezone
from register import HERE,sha,verify
if __name__=='__main__':
    verify()
    paths=['CLOCK_AMENDMENT1.json','metadata/extractor_NpxExtractor3a_cpp.receipt',
           'metadata/extractor_NpxExtractorPXI_cpp.receipt','results/digital/766640955.json','results/digital_code1/766640955.json']
    with (HERE/'amendment1_registration.json').open('x') as out:
        json.dump({'utc':datetime.now(timezone.utc).isoformat(),'sha256':{p:sha(HERE/p) for p in paths}},out,indent=2)
    print('Source-defined digital schema correction registered before full cohort.')
