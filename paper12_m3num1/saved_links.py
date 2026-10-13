"""Revalidate every public native child link without neural or runtime access."""
import study as r
from transitions import completed


def validate_links(gate,receipt,check):
    links=gate.get('native_proofs',[])
    if len(links)!=13 or len({x['phase'] for x in links})!=13 or receipt.get('native_proofs')!=links:
        raise RuntimeError('NATIVE_LINK_DENOMINATOR_OR_RECEIPT_CHANGED')
    for link in links:
        phase=link['phase']
        if phase!='smoke' and not (phase.startswith('cohort_') and phase[7:].isdigit()):
            raise RuntimeError('UNAUTHORIZED_PUBLIC_PROOF_PATH')
        if check(phase)!=link['sha256']:raise RuntimeError('NATIVE_CHILD_LINK_CHANGED:'+phase)
    return len(links)


def verify():
    completed(r,'full',1638)
    return validate_links(r.load(r.HERE/'results/full/gate_result.json'),
                          r.load(r.HERE/'results/full_launch_receipt.json'),
                          lambda phase:completed(r,phase,126))
