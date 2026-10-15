"""Public-only prerelease audit. Contains no neural loader or release capability."""
import json
from pathlib import Path
from register_audit import BASE, EVIDENCE, HERE, MISSION, ROOT, load, save, sha

LABEL = 'INCONCLUSIVE DUE TO FAILED REQUIRED GATE'
PRIMARY = ('own', 'population', 'stimulus_time', 'combined')


def release_allowed(gates):
    return bool(gates) and all(g['status'] == 'PASS' for g in gates)


def outcome(gates):
    allowed = release_allowed(gates)
    return {'mission': MISSION, 'base': BASE, 'stage_1': 'PASS' if allowed else 'CRITICAL_GATE_FAILED_STOP',
            'scientific_validation': 'NOT_EXECUTED', 'C_calibration_fits': 0, 'D_assessments': 0,
            'release_allowed': allowed,
            'contrasts': {k: {'classification': LABEL, 'effect': None, 'holm_p': None, 'CI95': None,
                              'null_verdict': 'NOT_EXECUTED'} for k in PRIMARY},
            'interpretation': 'No held-out effect, significance, equivalence or absence-of-effect conclusion is available.'}


def build():
    reg = load(HERE / 'registration.json')
    if reg['base'] != BASE or sha(HERE / 'mission.json') != reg['mission_sha256']:
        raise RuntimeError('REGISTRATION_CHANGED')
    for name, digest in reg['source_sha256'].items():
        if sha(ROOT / name) != digest:
            raise RuntimeError('FROZEN_SOURCE_CHANGED:' + name)
    animals = load(ROOT / 'paper12_curated_v1/locks/animals.json')
    trials = load(ROOT / 'paper12_curated_v1/locks/trials.json')
    final = [a for a in animals if a['group'] == 'final']
    if len(animals) != 26 or len(final) != 13 or len({a['mouse_id'] for a in final}) != 13:
        raise RuntimeError('COHORT_CHANGED')
    if any(a['group'] not in ('development', 'final') for a in animals):
        raise RuntimeError('UNKNOWN_ALLOCATION')
    expected = sorted(animals, key=lambda a: __import__('hashlib').sha256(
        ('P12-CURATED-EXPLORATORY-V1|animal|' + a['mouse_id']).encode()).hexdigest())
    if any(a['group'] != ('development' if i < 13 else 'final') for i, a in enumerate(expected)):
        raise RuntimeError('ALLOCATION_ALGORITHM_CHANGED')
    gate = load(ROOT / 'paper12_resume1/results/M2/gate_result.json')
    if gate['gate'] != 'PASS':
        raise RuntimeError('HISTORICAL_M2_GATE')
    rows = []
    for animal in final:
        sid = animal['session_id']
        relative = 'results/M2/sessions/' + sid + '.json'
        p = ROOT / 'paper12_resume1' / relative
        if sha(p) != gate['receipt_sha256'][relative]:
            raise RuntimeError('FROZEN_RECEIPT_CHANGED')
        receipt = load(p)
        for key in ('session_id', 'mouse_id', 'group'):
            if receipt[key] != animal[key]:
                raise RuntimeError('RECEIPT_IDENTITY')
        if set(receipt['ciphertext_receipts']) != {'C', 'D'} or receipt['qc_partition'] != 'calibration':
            raise RuntimeError('PARTITION_BOUNDARY')
        if any(receipt[k] is not False for k in ('final_values_exposed_to_analysis', 'final_holdout_evaluated', 'raw_vectors_exported')):
            raise RuntimeError('HISTORICAL_EXPOSURE_FAILURE')
        local = [t for t in trials if t['session_id'] == sid]
        parts = {}
        if len(local) != 600 or len({t['trial_id'] for t in local}) != 600:
            raise RuntimeError('TRIAL_IDENTITY')
        for part, minimum in (('calibration', 24), ('locked_evaluation', 16)):
            selected = [t for t in local if t['partition'] == part and t['metadata_admitted']]
            conditions = sorted({t['condition'] for t in local})
            counts = [sum(t['condition'] == c for t in selected) for c in conditions]
            if len(conditions) != 8 or min(counts) < minimum:
                raise RuntimeError('METADATA_TRIAL_COVERAGE')
            if len(selected) != animal['partition_counts_after_metadata_mask'][part]:
                raise RuntimeError('MASK_COUNT_CHANGED')
            parts[part] = {'trials': len(selected), 'per_condition_counts': counts}
        counts = receipt['eligible_unit_counts']
        rows.append({'mouse_id': animal['mouse_id'], 'session_id': sid, 'receipt_sha256': sha(p),
                     'partitions': parts, 'public_C_QC_eligible_counts': counts,
                     'public_primary_cap32_possible': min(counts.values()) >= 32,
                     'historical_D_scientific_exposure': False, 'historical_D_evaluated': False})
    reviews = []
    for name in ('independent_scientific_review.md', 'independent_custody_review.md'):
        p = EVIDENCE / name
        content = p.read_text(encoding='utf-8')
        if 'P1' not in content or 'HOLD' not in content:
            raise RuntimeError('INDEPENDENT_REVIEW_INCOMPLETE')
        reviews.append({'file': str(p.relative_to(ROOT)).replace('\\', '/'), 'sha256': sha(p), 'release_decision': 'HOLD'})
    gates = [
        {'id': 'G01', 'requirement': 'Exact development manuscript/protocol/model/source freeze', 'status': 'PASS', 'evidence': 'registration.json/source_sha256'},
        {'id': 'G02', 'requirement': 'Four original hypotheses and every frozen acceptance rule', 'status': 'PASS', 'evidence': 'Unchanged FINAL_VALIDATION_PLAN.md and final_validation_freeze.json'},
        {'id': 'G03', 'requirement': '13 final identities and metadata-only trial coverage/partitions', 'status': 'PASS', 'evidence': 'final_mouse_metadata rows'},
        {'id': 'G04', 'requirement': 'Independent scientific/numerical and custody plan review', 'status': 'HOLD', 'evidence': reviews},
        {'id': 'G05', 'requirement': 'Historical D non-exposure to restricted scientific role', 'status': 'SUPPORTED_WITHIN_REGISTERED_THREAT_MODEL', 'evidence': 'Frozen M2 receipts, AB-only exports and independent custody source audit; no claim of malicious-controller protection'},
        {'id': 'G06', 'requirement': 'Fresh final actual-principal isolation and manifest verification', 'status': 'UNVERIFIED', 'evidence': 'Historical native proofs cannot certify a nonexistent final release runner'},
        {'id': 'G07', 'requirement': 'Protected C-only fitting runner and full sensitivity-state freeze', 'status': 'NOT_IMPLEMENTED', 'evidence': 'Development worker reads A/B together, bypasses accepted_fit and saves only primary states'},
        {'id': 'G08', 'requirement': 'Independent artifact-bound exactly-once D authorization', 'status': 'FAIL', 'evidence': 'amendment.json release contract; native launcher relies on caller and no final controller exists'},
        {'id': 'G09', 'requirement': 'Exclusive durable append-only D entitlement consumption', 'status': 'FAIL', 'evidence': 'No final entitlement/issuer ledger or duplicate/concurrent/interrupted/tamper denial proof'},
    ]
    result = outcome(gates)
    if result['release_allowed']:
        raise RuntimeError('UNEXPECTED_RELEASE_PERMISSION')
    result.update(gates=gates, final_mouse_metadata=rows, independent_reviews=reviews,
                  historical_numerical_failures_reclassified=False,
                  protected_payloads_opened_by_audit=0, protected_keys_opened_by_audit=0,
                  final_scientific_model_states_produced=0,
                  scope='Source, frozen public metadata and public saved receipts only')
    return result


def main():
    result = build()
    save(HERE / 'pre_release_audit.json', result)
    print(json.dumps({k: result[k] for k in ('mission', 'base', 'stage_1', 'C_calibration_fits', 'D_assessments', 'release_allowed')}))


if __name__ == '__main__':
    main()
