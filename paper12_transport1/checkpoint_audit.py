"""Post-stop trusted opaque-byte integrity audit, never neural decoding."""
import hashlib
import os
import uuid
from collections import Counter
import common as r
import custodian as c


def main():
    registration=r.verify();c.require_custodian();rows=[]
    for session in sorted((r.OLD/'.private/transport_recovery1/cache').iterdir()):
        frozen=registration['sources'][session.name];histogram=Counter();statuses=Counter();committed=0;pending=0
        for ledger in session.glob('attempts_*'):
            intents=list(ledger.glob('*.intent.json'));histogram[len(intents)]+=1
            if len(intents)>3:raise RuntimeError('TRANSPORT_BUDGET_VIOLATION')
            for intent in intents:
                identity=r.load(intent)['source']
                if (identity['file_id'],identity['etag'],identity['size'])!=(frozen['file_id'],frozen['etag'],frozen['bytes']):
                    raise RuntimeError('ATTEMPT_SOURCE_MISMATCH')
                result=intent.with_name(intent.name.replace('.intent.','.result.'))
                statuses[r.load(result)['status'] if result.exists() else 'INTERRUPTED_INTENT']+=1
        for chunk in list(session.glob('chunk_*'))+list(session.glob('pending_*')):
            marker=r.load(chunk/'marker.json');source=marker['source'];body=chunk/'body.blob'
            if body.stat().st_size!=source['end']-source['start']+1 or r.sha(body)!=marker['sha256']:
                raise RuntimeError('CHECKPOINT_BODY_MISMATCH')
            if chunk.name.startswith('chunk_'):committed+=1
            else:pending+=1
        rows.append(dict(session_id=session.name,attempt_histogram=dict(histogram),result_status_counts=dict(statuses),
            committed_verified_blocks=committed,pending_verified_but_unaccepted_blocks=pending,
            fatal_stop_preserved=(session/'STOP.json').exists(),opaque_bytes_hashed_only=True,neural_values_decoded=False,
            source_requests_added=0,source_ETag_length_identity_verified=True))
    synthetic=[]
    root=r.OLD/'.private/transport_recovery1/synthetic_commit_audit';root.mkdir(exist_ok=True);c.protect(root)
    for number in range(20):
        trial=root/('trial_'+uuid.uuid4().hex);trial.mkdir();c.protect(trial)
        pending=trial/'pending';pending.mkdir();c.protect(pending)
        for name in ('body.blob','marker.json'):
            path=pending/name
            with path.open('xb') as stream:stream.write(os.urandom(256));stream.flush();os.fsync(stream.fileno())
            c.protect(path)
        try:
            pending.rename(trial/'committed');result=dict(trial=number,rename_pass=True)
        except OSError as exc:
            result=dict(trial=number,rename_pass=False,winerror=exc.winerror,error_type=type(exc).__name__)
        synthetic.append(result)
    r.save(r.HERE/'results/checkpoint_audit.json',dict(rows=rows,synthetic_commit_trials=synthetic,
        synthetic_commit_count=20,source_requests_added=0,final_evaluation_performed=False,
        scope='Post-stop opaque checksum/journal and synthetic protected rename audit; no recovery retry or neural decoding',
        implementation_sha256=r.sha(r.HERE/'checkpoint_audit.py')))
    print(dict(audited_sessions=len(rows),synthetic_rename_passes=sum(x['rename_pass'] for x in synthetic),source_requests_added=0))


if __name__=='__main__':main()
