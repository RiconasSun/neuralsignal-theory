"""Seal exactly the independently approved candidate; never opens neural data."""
from paper15_final1.source import P,R,E,read,dump,sha


def seal(candidate,approvals):
    assert not (P/'D_BATCH_CLAIM.json').exists() and not (P/'PRE_D_GATE.json').exists()
    hashes=candidate['hashes'];assert len(hashes)>400
    assert {p.name for p in P.glob('*.py')}<=set(hashes)
    state=read(P/'FINAL_C_STATE_SEAL.json');spec=read(P/'ONE_SHOT_D_SPECIFICATION.json')
    assert candidate['subjects']==state['primary_subjects']==spec['primary_subjects']
    assert state['complete_calibration_state'] and state['main_attempts']==72 and state['sensitivity_attempts']==320
    assert spec['D_batches']==1 and spec['mandatory_descriptive_only'] and len(candidate['subjects'])==6
    assert all(x['path'] in hashes and hashes[x['path']]==x['sha256'] for x in state['artifacts'])
    assert set(approvals)=={'scientific','numerical'}
    for item in approvals.values():
        receipt=read(R/item['path']);assert sha(R/item['path'])==item['sha256']
        assert receipt['decision']=='ACCEPTED_FROZEN_ONE_SHOT_D' and receipt['approved_one_D_batch'] is True
        assert type(receipt['open_P0']) is int and receipt['open_P0']==0
        assert type(receipt['open_P1']) is int and receipt['open_P1']==0
        assert receipt['hashes']==hashes and sha(R/receipt['report_path'])==receipt['report_sha256']
    for rel,h in hashes.items():assert sha(P/rel)==h,rel
    gate=dict(approved_one_D_batch=True,D_batches=1,subjects=candidate['subjects'],hashes=hashes,
              independent_reviews=approvals,candidate_sha256=sha(P/'PRE_D_CANDIDATE.json'),
              scope='One original frozen descriptive Final D batch; no retuning or reassessment',
              no_cryptographic_or_third_party_custody_claim=True)
    dump(P/'PRE_D_GATE.json',gate)
    from paper15_final1.admission import verify_pre_D_gate
    verify_pre_D_gate()
    print('Complete prospective six-mouse descriptive D gate sealed; no D source opened')


if __name__=='__main__':
    seal(read(P/'PRE_D_CANDIDATE.json'),read(E/'PRE_D_REVIEW_BINDINGS.json'))
