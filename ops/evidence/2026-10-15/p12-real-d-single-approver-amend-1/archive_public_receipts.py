"""Archive a fixed public SYN metadata roster; never arrays, ciphertext or keys."""
import hashlib
import json
from pathlib import Path
import shutil

E=Path(__file__).resolve().parent;ROOT=E.parents[3];job=ROOT/'paper12_singleowner1/jobs/synthetic_2'

def main():
    if not any((p/'assessment_started.json').exists() for p in (job/'exports').glob('P12Production.*/output')):raise RuntimeError('SYN_ASSESSMENT_NOT_YET_STARTED')
    binding=job/'exports/security/binding';success=job/'exports/security/success';archive=E/'synthetic_2_integrity';archive.mkdir(exist_ok=False)
    names=('C_state_manifest.json','partition_manifest.json','source_catalog.json','source_units.json','source_roots.json','code_identity.json','runtime_identity.json','analysis_spec.json','PROTOCOL.md','FINAL_VALIDATION_PLAN.md','engineering_review.md','scientific_review.md','SECURITY_AMENDMENT.md','human_authorization.bin','PUBLIC_KEY_VALIDITY_AMENDMENT.md','human_fix_authorization.txt','owner_setup.json','owner_challenge.json','owner_proof.json','owner_confirmation.json','owner_provisioning_receipt.json')
    for name in names:shutil.copyfile(binding/name,archive/name)
    for name in ('anchor.json','approval.json'):shutil.copyfile(success/name,archive/name)
    shutil.copyfile(job/'.private/synthetic_authority/synthetic_authority.json',archive/'synthetic_authority_public.json')
    shutil.copyfile(job/'exports/target/payload/delivery_manifest.json',archive/'delivery_manifest.json')
    (archive/'ledger').mkdir()
    for name in ('genesis.json','events.jsonl','intent.json','consumed.json','delivery_started.json','delivery_complete.json'):shutil.copyfile(success/'ledger'/name,archive/'ledger'/name)
    body=json.loads((success/'approval.json').read_text())['body']
    if body['realm']!='SYNTHETIC_D':raise PermissionError('SYN_PUBLIC_ARCHIVE_ONLY')
    shutil.copyfile(job/'exports/security/fence_success'/(body['authorization_id']+'.json'),archive/'independent_consumption_fence.json')
    inventory={p.relative_to(archive).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(archive.rglob('*')) if p.is_file()}
    with (archive/'inventory.json').open('x',encoding='utf-8') as f:json.dump(inventory,f,indent=2,sort_keys=True);f.write('\n')
    print(json.dumps({'public_SYN_receipts_archived':len(inventory),'no_count_arrays_ciphertext_or_private_keys':True,'path':str(archive)},sort_keys=True))

if __name__=='__main__':main()
