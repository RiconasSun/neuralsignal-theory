"""Public, identity-bound M2 aggregation; never opens private neural artifacts."""
from collections import Counter
import csv
import register as r
import index3
from cache_binding3 import validate


def summarize(animals, records):
    completed = Counter(); eligible = Counter(); rows = []
    critical = False
    for animal in animals:
        sid = animal['session_id']
        receipt = records.get(sid)
        row = {k: animal[k] for k in ('mouse_id', 'session_id', 'group')}
        row.update(status='NOT_EXECUTED', eligible_CA1=None, eligible_DG=None,
                   eligible_mouse=None)
        if receipt is not None:
            if receipt.get('session_id') != sid or receipt.get('group') != animal['group']:
                raise ValueError('RECEIPT_IDENTITY_MISMATCH')
            if receipt.get('final_values_exposed_to_analysis') is not False or receipt.get('final_holdout_evaluated') is not False:
                raise ValueError('HOLDOUT_BOUNDARY_VIOLATION')
            if 'error_code' in receipt:
                row['status'] = 'EXTRACTION_FAILED'
                critical = True
            else:
                if receipt.get('mouse_id') != animal['mouse_id']:
                    raise ValueError('MOUSE_IDENTITY_MISMATCH')
                counts = receipt['eligible_unit_counts']
                if any(type(counts.get(k)) is not int or counts[k] < 0 for k in ('CA1', 'DG')):
                    raise ValueError('INVALID_ELIGIBILITY_COUNTS')
                actual = min(counts.values()) >= 5
                if receipt.get('eligible_mouse') is not actual:
                    raise ValueError('ELIGIBILITY_THRESHOLD_MISMATCH')
                completed[animal['group']] += 1
                eligible[animal['group']] += actual
                row.update(status='QC_COMPLETED', eligible_CA1=counts['CA1'],
                           eligible_DG=counts['DG'], eligible_mouse=actual)
        rows.append(row)
    expected = Counter(a['group'] for a in animals)
    if expected != Counter(development=13, final=13) or len({a['mouse_id'] for a in animals}) != 26:
        raise ValueError('FROZEN_MOUSE_DENOMINATOR_INVALID')
    if critical:
        gate, verdict = 'FAIL', 'INCONCLUSIVE'
    elif completed == expected:
        passed = eligible['development'] >= 8 and eligible['final'] >= 8
        gate, verdict = ('PASS', 'COHORT_ADMISSION_PASS') if passed else ('FAIL', 'DATA_INSUFFICIENT')
    else:
        gate, verdict = 'NOT_COMPLETE', 'NOT_ASSESSED'
    result = dict(gate=gate, scientific_verdict=verdict,
                  completed_QC=dict(completed), eligible_mice=dict(eligible),
                  frozen_candidates=dict(expected), full_study_validated=False,
                  final_values_exposed_to_analysis=False, final_holdout_evaluated=False,
                  original_M2_reclassified=False,
                  source_full_session_decoded_by_custodian=any(
                      x.get('source_full_session_decoded_by_custodian') is True for x in records.values()))
    return result, rows


def main():
    r.verify()
    old, animals, items = index3.inputs()
    attestation = r.load(r.HERE / 'audit_completion_binding3.json')
    records = {}; fingerprints = {}
    for animal in animals:
        sid = animal['session_id']
        audit = r.HERE / 'results/index2/audit' / (sid + '.json')
        previous = r.HERE / 'results/M2/transport1/sessions' / (sid + '.json')
        validate(r.load(audit), attestation['bindings'][sid], index3.expected(animal, items[sid]),
                 r.sha(audit), r.load(previous) if previous.exists() else None,
                 r.sha(previous) if previous.exists() else None)
        good = r.HERE / 'results/M2/index2/sessions' / (sid + '.json')
        bad = r.HERE / 'results/M2/index2/failures' / (sid + '.json')
        if bad.exists():
            path = bad
        elif good.exists():
            path = good
        else:
            continue
        record = r.load(path)
        if path == good:
            if record.get('source_etag') != items[sid]['etag']:
                raise ValueError('SOURCE_ETAG_MISMATCH')
            if previous.exists() and (record.get('prior_output_sha256') != r.sha(previous) or
                                     record.get('audit_attestation_sha256') != r.sha(r.HERE / 'audit_completion_binding3.json')):
                raise ValueError('REUSED_RECEIPT_HASH_MISMATCH')
        records[sid] = record
        fingerprints[str(path.relative_to(r.HERE))] = r.sha(path)
    result, rows = summarize(animals, records)
    result.update(receipt_sha256=fingerprints,
                  animal_lock_sha256=r.sha(old / 'locks/animals.json'),
                  audit_attestation_sha256=r.sha(r.HERE / 'audit_completion_binding3.json'),
                  aggregate_implementation_sha256=r.sha(r.HERE / 'aggregate4.py'),
                  QC_detail_access='PRIVATE_CUSTODY_ONLY; aggregate eligibility is not a selection input')
    output = r.HERE / 'results/M2/aggregate4'
    output.mkdir(parents=True, exist_ok=True)
    r.save(output / 'gate_result.json', result)
    with (output / 'mouse_denominator.csv').open('w', newline='', encoding='utf-8') as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader(); writer.writerows(rows)
    print({k: v for k, v in result.items() if k != 'receipt_sha256'})


if __name__ == '__main__':
    main()
