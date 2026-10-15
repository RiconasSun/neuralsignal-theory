"""Archive public receipts and synthetic ledgers; never raw input, state, key or private roster."""
import hashlib
import shutil
import zipfile
from pathlib import Path
import study as r
from archive_evidence import archive

def main():
    # Reuse an already verified lossless journal archive where available, avoiding rereads.
    adopted={}
    for package in sorted((r.HERE/'jobs').glob('*/exports/saved')):
        manifest=package/'C_state_manifest.json'
        if not manifest.exists():continue
        value=r.load(manifest)
        if value.get('version')!=2 or not value.get('synthetic'):continue
        identity=r.load(package/'provenance_launch_receipt.json')
        prior=r.load(package/'provenance_calibration_states.json')
        adopted[prior['state_sha256']]=package
    for job in sorted((r.HERE/'jobs').iterdir()):
        for output in sorted((job/'exports').glob('P12Analysis.*/output')):
            if not list(output.glob('*.json')):continue
            name='receipts_'+job.name
            if (r.HERE/'results'/(name+'_archive.json')).exists():continue
            state=output/'calibration_states.json';package=None
            if state.exists():
                report=r.load(state);candidate=adopted.get(report['state_sha256'])
                if candidate is not None:
                    # Source launch/role/input provenance can differ despite equal coefficients.
                    index=r.load(candidate/'attempt_journals_index.json')
                    if index.get('calibration_states.json')==r.sha(state) and index.get('role_proof.json')==r.sha(output/'role_proof.json'):package=candidate
            if package:
                target=r.HERE/'results'/(name+'.zip');shutil.copy2(package/'attempt_journals.zip',target)
                r.save(r.HERE/'results'/(name+'_archive.json'),{'archive':target.name,'archive_sha256':r.sha(target),
                    'member_sha256':r.load(package/'attempt_journals_index.json'),'source_directory':str(output.relative_to(r.HERE)),
                    'scope':'Exact original public JSON journals; adopted verified lossless seal archive; no arrays/keys/private roster'})
            else:archive(name,output)
    for job in sorted((r.HERE/'jobs').glob('controller_*')):
        data=job/'exports/security'
        if not data.exists():continue
        target=r.HERE/'results'/('ledgers_'+job.name+'.zip')
        if target.exists():continue
        members={}
        with zipfile.ZipFile(target,'x',zipfile.ZIP_DEFLATED) as z:
            for fixture in sorted(data.iterdir()):
                if not (fixture/'ledger').is_dir():continue
                files=[fixture/n for n in ('anchor.json','approval.json')]+list((fixture/'ledger').glob('*'))
                for p in files:
                    if not p.is_file() or p.suffix not in ('.json','.jsonl','.lock'):continue
                    name=p.relative_to(data).as_posix();raw=p.read_bytes();members[name]=hashlib.sha256(raw).hexdigest();z.writestr(name,raw)
        r.save(target.with_name(target.stem+'_archive.json'),{'archive':target.name,'archive_sha256':r.sha(target),'member_sha256':members,
            'scope':'Synthetic-only issued approvals and exact durable ledger bytes; no issuer private keys or real entitlement'})
    print({'public_receipt_archives':len(list((r.HERE/'results').glob('*_archive.json'))),'protected_inputs_copied':False})
if __name__=='__main__':main()
