"""Public stopped-audit reproduction only; deliberately no release execution mode."""
import hashlib
import json
from . import audit as a

def main():
    a.verify_hashes(a.read(a.E/'audit_source_snapshot.json')['sha256'])
    seal=a.E/'final_manifest.json'
    if seal.exists():a.verify_hashes(a.read(seal)['sha256'])
    actual=a.compute();saved=a.read(a.E/'prerelease_audit.json')
    for name in ('host_disk_free_bytes_observed',):actual.pop(name);saved.pop(name)
    if actual!=saved:raise RuntimeError('STOPPED_DECISION_DRIFT')
    print(json.dumps({'audit_reproduction':'PASS','PRE_RELEASE_GATE':actual['PRE_RELEASE_GATE'],'D_RELEASE_CONSUMED':False,'D_EVALUATION_EXECUTED':False,'new_fits':0,'protected_payload_reads':0,'scientific_validation':actual['SCIENTIFIC_VALIDATION_VERDICT']}))

if __name__=='__main__':main()
