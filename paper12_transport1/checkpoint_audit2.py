"""Correct marker binding, preserve original overstatement and all synthetic trials."""
import common as r
import custodian as c
from bounded_core import byte_range


def main():
    registration=r.verify();c.require_custodian()
    previous=r.load(r.HERE/'results/checkpoint_audit.json');rows=[]
    if previous['implementation_sha256']!=r.sha(r.HERE/'checkpoint_audit.py'):
        raise RuntimeError('ORIGINAL_AUDIT_CODE_CHANGED')
    for session in sorted((r.OLD/'.private/transport_recovery1/cache').iterdir()):
        frozen=registration['sources'][session.name];committed=pending=0
        for chunk in list(session.glob('chunk_*'))+list(session.glob('pending_*')):
            marker=r.load(chunk/'marker.json');source=marker['source']
            if (source['file_id'],source['etag'],source['size'])!=(frozen['file_id'],frozen['etag'],frozen['bytes']):
                raise RuntimeError('MARKER_SOURCE_IDENTITY_MISMATCH')
            start,end=byte_range(f"bytes={source['start']}-{source['end']}",frozen['bytes'])
            if chunk.name.startswith('chunk_') and chunk.name!='chunk_%016x'%start:
                raise RuntimeError('COMMITTED_DIRECTORY_OFFSET_MISMATCH')
            body=chunk/'body.blob'
            if body.stat().st_size!=end-start+1 or r.sha(body)!=marker['sha256']:
                raise RuntimeError('CHECKPOINT_BODY_MISMATCH')
            ledger=session/('attempts_%016x'%start)
            identities=[r.load(path)['source'] for path in ledger.glob('*.intent.json')]
            if not identities or any(identity!=source for identity in identities):
                raise RuntimeError('MARKER_LEDGER_IDENTITY_MISMATCH')
            if chunk.name.startswith('chunk_'):committed+=1
            else:pending+=1
        rows.append(dict(session_id=session.name,committed_verified_blocks=committed,
            pending_verified_but_unaccepted_blocks=pending,marker_source_identity_range_directory_ledger_and_hash_verified=True))
    r.save(r.HERE/'results/checkpoint_audit_verified2.json',dict(rows=rows,
        original_audit_sha256=r.sha(r.HERE/'results/checkpoint_audit.json'),
        correction='Original marker identity claim overstated ledger-only verification; retained, superseded by this full marker binding audit',
        synthetic_trials_source='results/checkpoint_audit.json; all20retained,19PASS/1WinError5; not rerun or seed-selected',
        source_requests_added=0,neural_values_decoded=False,actual_commit_retried=False,
        implementation_sha256=r.sha(r.HERE/'checkpoint_audit2.py')))
    print(dict(fully_bound_marker_audit_pass=True,source_requests_added=0))


if __name__=='__main__':main()
