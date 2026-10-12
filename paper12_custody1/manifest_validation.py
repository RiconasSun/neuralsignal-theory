"""Exact public development roster/provenance binding; no neural-value reads."""
def validate_manifest(manifest, animals, qc_receipts, gate_hash, registration_hash):
    if manifest.get('group') != 'development' or manifest.get('compartments') != ['A', 'B']:
        raise ValueError('DEVELOPMENT_PARTITION_BOUNDARY_INVALID')
    if manifest.get('M2_gate_sha256') != gate_hash or manifest.get('development_registration_sha256') != registration_hash:
        raise ValueError('DEVELOPMENT_PROVENANCE_BINDING_INVALID')
    expected = {}
    for animal in animals:
        if animal['group'] == 'development':
            qc = qc_receipts[animal['session_id']]
            if qc['mouse_id'] != animal['mouse_id'] or qc['group'] != 'development':
                raise ValueError('FROZEN_DEVELOPMENT_IDENTITY_INVALID')
            if qc['eligible_mouse'] is True:
                expected[animal['session_id']] = animal['mouse_id']
    actual = manifest.get('sessions', [])
    sessions = [x['session_id'] for x in actual]
    mice = [x['mouse_id'] for x in actual]
    if len(set(sessions)) != len(sessions) or len(set(mice)) != len(mice):
        raise ValueError('DUPLICATED_DEVELOPMENT_SUBJECT')
    if len(mice) < 8 or {x['session_id']: x['mouse_id'] for x in actual} != expected:
        raise ValueError('EXACT_ELIGIBLE_DEVELOPMENT_ROSTER_REQUIRED')
    if any(x['file'] != x['session_id'] + '.npz' for x in actual):
        raise ValueError('DEVELOPMENT_INPUT_FILENAME_INVALID')
    return True
