"""Repeat-safe append-only replay; original registration/gate/receipt immutable."""
import sys
import audit
import register_sources as prov

OUT,HERE,ROOT=prov.OUT,prov.HERE,prov.ROOT


def register():
    audit.verify()
    reg=OUT/'saved_verifier_registration.json'
    if reg.exists():return verify()
    prov.save(reg,{'before_replay_tests':True,'scope':'Saved-only repeatability; no scientific rule changes',
        'source_sha256':{str(p.relative_to(ROOT)).replace('\\','/'):prov.sha(p) for p in [HERE/'verify_saved.py',HERE/'reproduce-safe.ps1']},
        'preserved_one_time_replay_sha256':prov.sha(OUT/'replay_receipt.json'),
        'original_artifact_lock_sha256':prov.sha(OUT/'artifact_lock.json')})


def verify():
    audit.verify()
    reg=prov.load(OUT/'saved_verifier_registration.json')
    for path,digest in reg['source_sha256'].items():
        if prov.sha(ROOT/path)!=digest:raise RuntimeError('Saved verifier changed')
    if prov.sha(OUT/'replay_receipt.json')!=reg['preserved_one_time_replay_sha256']:
        raise RuntimeError('Original replay receipt changed')
    if prov.sha(OUT/'artifact_lock.json')!=reg['original_artifact_lock_sha256']:
        raise RuntimeError('Original artifact lock changed')
    for path,digest in prov.load(OUT/'artifact_lock.json')['sha256'].items():
        if prov.sha(ROOT/path)!=digest:raise RuntimeError('Original saved output changed')


def replay():
    verify()
    lock=prov.load(ROOT/'paper11_v2/results/R0_schema1/final_validation_lock.json')
    old={s['asset_id']:s for s in prov.load(ROOT/'paper11_v2/results/R2_external_support_code2/support_audit.json')['sessions']}
    ids={s['asset_id'] for s in lock['eligible_sessions']}
    actual={p.stem for p in (OUT/'sessions').glob('*.json')}
    if len(ids)!=52 or ids!=actual or ids!=set(old):raise RuntimeError('Full52identity mismatch')
    counts={v:0 for v in ['PASS','FAIL','INCONCLUSIVE']}
    for s in lock['eligible_sessions']:
        row=prov.load(OUT/'sessions'/(s['asset_id']+'.json'))
        for field in ['asset_id','path','patient','size','published_sha256']:
            if row[field]!=s[field]:raise RuntimeError('Pinned asset identity mismatch')
        if 'metadata' not in row:raise RuntimeError('Cannot certify replay without saved metadata')
        result=audit.assess(row['metadata'],old[s['asset_id']],s['valid_recognition_trials'])
        if any(row[k]!=v for k,v in result.items()):raise RuntimeError('Replayed verdict mismatch')
        for entry in row['metadata']['decode_ledger']:
            p,i=entry['path'],entry['index']
            ok=(p in audit.ROOT_TEXT|audit.EVENT_TEXT and i=='scalar') or (p=='acquisition/events/data' and i==0) or (p=='acquisition/events/timestamps' and i in [0,-1])
            if not ok:raise RuntimeError('Unexpected saved decode path/index')
        counts[row['verdict']]+=1
    gate=prov.load(OUT/'gate_result.json')
    if [counts['PASS'],counts['INCONCLUSIVE'],counts['FAIL']]!=[gate['supported'],gate['inconclusive'],gate['contradictions']]:
        raise RuntimeError('Gate denominator mismatch')
    test=audit.tests()
    receipt={'tests_exit_code':test.returncode,'controlled_tests':18,'sessions_verified':52,
             'counts':counts,'original_R2':'FAIL','audit_verdict':gate['audit_verdict'],
             'no_network_neural_holdout_or_fitting':True,
             'preserved_tracked_files':len(prov.verify()['preserved_tracked_sha256']),
             'original_gate_sha256':prov.sha(OUT/'gate_result.json')}
    path=OUT/'saved_verifier_receipt.json'
    if path.exists():
        if prov.load(path)!=receipt:raise RuntimeError('Replay not reproducible')
    else:prov.save(path,receipt)
    print(receipt)
    return test.returncode


if __name__=='__main__':sys.exit({'register':register,'replay':replay,'verify':verify}[sys.argv[1]]() or 0)
