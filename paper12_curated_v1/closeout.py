"""Produce stopped-evidence outputs from registered metadata and schema receipts."""
import csv
import json
from collections import Counter
from pathlib import Path
import register as r
from access_audit import classify


def write_csv(path, values):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', newline='', encoding='utf-8') as stream:
        w = csv.DictWriter(stream, fieldnames=list(values[0]))
        w.writeheader()
        w.writerows(values)


def derive():
    reg = r.verify()
    animals = r.load(r.HERE / 'locks/animals.json')
    trials = r.load(r.HERE / 'locks/trials.json')
    units = r.load(r.HERE / 'locks/units.json')
    paths = sorted((r.HERE / 'results/M2/schema_network1').glob('*.json'))
    if {p.stem for p in paths} != {x['session_id'] for x in animals}:
        raise RuntimeError('Full frozen26session schema denominator required')
    schemas = {p.stem: r.load(p) for p in paths}
    items = {x['session_id']: x for x in r.load(r.ROOT / 'paper12/metadata/allen_header_capability.json')}
    report = []
    for animal in animals:
        sid = animal['session_id']
        s = schemas[sid]
        if s['mouse_id'] != animal['mouse_id'] or s['group'] != animal['group'] or s['etag'] != items[sid]['etag']:
            raise RuntimeError('Object/animal identity drift')
        if s['neural_values_decoded'] != 0 or s['final_outcomes_decoded']:
            raise RuntimeError('Neural access boundary violated')
        if s.get('error'):
            raise RuntimeError('Unresolved schema transport error; cannot infer source format')
        if s['temporal_selection'] != classify(s['schema']):
            raise RuntimeError('Stale schema classification')
        if sum(x['bytes'] for x in s['ranges']) != s['transport_bytes']:
            raise RuntimeError('Range receipt bytes mismatch')
        n = animal['partition_counts_after_metadata_mask']
        train = 'train' if animal['group'] == 'development' else 'calibration'
        val = 'validation' if animal['group'] == 'development' else 'locked_evaluation'
        coverage = all(c.get(train, 0) >= 24 and c.get(val, 0) >= 16
                       for c in animal['condition_counts_after_metadata_mask'].values())
        report.append({'mouse_id': animal['mouse_id'], 'session_id': sid, 'group': animal['group'],
                       'candidate_CA1_ids': animal['anatomical_potential_units']['CA1'],
                       'candidate_DG_ids': animal['anatomical_potential_units']['DG'],
                       'all_trials': 600, 'train_or_calibration_metadata_trials': n.get(train, 0),
                       'validation_or_final_metadata_trials': n.get(val, 0),
                       'metadata_trial_coverage_pass': coverage,
                       'actually_eligible_CA1_units': 'NOT_ASSESSED', 'actually_eligible_DG_units': 'NOT_ASSESSED',
                       'actually_eligible_mouse': 'NOT_ASSESSED', 'neural_values_decoded': 0,
                       'verified_calibration_only_reader': s['temporal_selection']['safe_temporal_selection_established'],
                       'schema_receipt_sha256': r.sha(r.HERE / 'results/M2/schema_network1' / (sid + '.json'))})
    if any(s['temporal_selection']['safe_temporal_selection_established'] for s in schemas.values()):
        raise RuntimeError('Do not issue canned stopped verdict for changed evidence')
    reasons = Counter(x for t in trials for x in t['exclusions'])
    gate = {'mission': r.MISSION, 'milestone': 'M2', 'gate': 'FAIL', 'scientific_verdict': 'INCONCLUSIVE',
            'reason': 'CALIBRATION_ONLY_NEURAL_ACCESS_NOT_ESTABLISHED',
            'M1_gate': 'PASS', 'original_M0_reclassified': False, 'native_support_reclassified': False,
            'candidate_mice': 26, 'development_candidates': 13, 'final_candidates': 13,
            'actual_eligible_development_mice': None, 'actual_eligible_final_mice': None,
            'eligibility_status': 'NOT_ASSESSED; not DATA_INSUFFICIENT',
            'required_eligible_each_group': 8, 'neural_values_decoded': 0, 'final_holdout_decoded': False,
            'successful_schema_sessions': 26, 'verified_temporal_readers': 0,
            'model_fits': 0, 'final_evaluations': 0, 'scientific_validation_pass': False,
            'manuscript_complete': False, 'downstream_M3_M7': 'NOT_EXECUTED',
            'registration_sha256': r.sha(r.HERE / 'registration.json'),
            'full_denominator_retained': True,
            'per_session_evidence': {p.relative_to(r.HERE).as_posix(): r.sha(p) for p in paths}}
    summary = {'registered_utc': reg['registered_utc'], 'all_trials': len(trials),
               'metadata_admitted_trials': sum(t['metadata_admitted'] for t in trials),
               'metadata_excluded_trials': sum(not t['metadata_admitted'] for t in trials),
               'exclusion_reason_counts': dict(reasons), 'target_unit_identities': len(units),
               'quarantined_unit_identities': sum(u['metadata_quarantined'] for u in units),
               'all_mice_metadata_trial_coverage_pass': all(x['metadata_trial_coverage_pass'] for x in report),
               'schema_transport_bytes': sum(s['transport_bytes'] for s in schemas.values()),
               'schema_ranges': sum(len(s['ranges']) for s in schemas.values()),
               'registered_source_shape_observed': dict(Counter(s['temporal_selection']['format'] for s in schemas.values())),
               'neural_values_decoded': 0, 'old_files_hash_preserved': len(reg['prior_sha256'])}
    return report, gate, summary


def main(output=None):
    out = Path(output) if output else r.HERE / 'results/closeout'
    out.mkdir(parents=True, exist_ok=True)
    report, gate, summary = derive()
    write_csv(out / 'mouse_evidence.csv', report)
    r.save(out / 'summary.json', summary)
    r.save(out / 'gate_result.json', gate)
    if output is None:
        r.save(r.HERE / 'results/M2/gate_result.json', gate)
    print(json.dumps({'gate': gate['gate'], 'scientific_verdict': gate['scientific_verdict'], **summary}), flush=True)


if __name__ == '__main__':
    import sys
    main(sys.argv[1] if len(sys.argv) > 1 else None)
