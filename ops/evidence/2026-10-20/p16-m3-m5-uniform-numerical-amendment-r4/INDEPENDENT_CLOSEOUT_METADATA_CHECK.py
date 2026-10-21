"""Independent JSON-only closeout accounting; no scientific modules or arrays."""
import collections
import datetime
import hashlib
import json
import re
from pathlib import Path

E = Path(__file__).resolve().parent
R = E.parents[3]
P = R / 'paper16_development_r4'

def load(path):
    return json.loads(path.read_bytes())

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    baseline = load(E / 'REQUIREMENT_BASELINE.json')
    trace = load(E / 'REQUIREMENT_OUTCOMES.json')
    assert len(baseline['items']) == len(trace['items']) == 254
    assert len({row['id'] for row in trace['items']}) == 254
    for original, outcome in zip(baseline['items'], trace['items']):
        for key in ['id', 'owner_line', 'section', 'requirement']:
            assert original[key] == outcome[key], (original['id'], key)
    assert trace['all_scientific_requirements_verified'] is False
    by_id = {row['id']: row for row in trace['items']}
    for key in [9,114,116,137,138,139,140,141,142,143,144,145,146,148,149,
                152,153,154,155,156,157,158,159,160,161,162,163,164,165,196,199]:
        assert by_id[f'R-{key:03d}']['status'] == 'OPEN'
    assert by_id['R-207']['status'] == 'BLOCKED_HUMAN_INPUT'
    tasks = load(P / 'TASK_OUTCOMES.json')
    plan = load(P / 'NEW_TASK_PLAN_CANDIDATE.json')
    assert tasks['planned'] == plan['optimizer_attempt_count'] == 5519
    assert [row['task'] for row in tasks['tasks']] == plan['tasks']
    counts = collections.Counter(row['status'] for row in tasks['tasks'])
    assert counts == {'NUMERICAL_PASS':3040,'INTERRUPTED_INCOMPLETE':1,'UNATTEMPTED':2478}
    complete = tasks['tasks'][:3040]
    assert all(row['status'] == 'NUMERICAL_PASS' and row['numerical_pass'] is True for row in complete)
    partial = tasks['tasks'][3040]
    assert partial['status'] == 'INTERRUPTED_INCOMPLETE'
    assert partial['task']['id'] == '763236014:S02:S:None:11:GLOBAL'
    assert partial['numerical_pass'] is None and partial['endpoint_missing_not_reconstructed'] is True
    assert all(row['status'] == 'UNATTEMPTED' for row in tasks['tasks'][3041:])
    facts = load(P / 'EXECUTION_FACTS.json')
    assert digest(P / 'EXECUTION_FACTS.json') == tasks['facts_sha256']
    assert sum(row['FG_calls'] for row in complete) == 707125
    assert sum(row['iterations'] for row in complete) == 664219
    assert facts['FG_completed'] == 707125+485 == 707610
    assert facts['accepted_iterations'] == 664219+465 == 664684
    assert max(row['PG'] for row in complete) == 1.999980498137462e-6
    for key in ['Final_C_access','Final_D_access','E_claimed','E_complete','M4_seal_candidate','M4_complete']:
        assert facts[key] is False
    assert facts['E_exports'] == 0 and facts['scientific_stop'] is None
    supplement = load(P / 'PROTECTED_STATE_MANIFEST_SUPPLEMENT_1.json')
    assert supplement['original_manifest_sha256'] == digest(P / 'PROTECTED_STATE_MANIFEST.json')
    assert len(supplement['files']) == 1
    row = supplement['files'][0]
    assert row['path'] == 'paper16_development_r4/work/INDEPENDENT_INTERRUPTION_FILE_HASHES.json'
    assert digest(R / row['path']) == row['sha256']
    assert (R / row['path']).stat().st_size == row['bytes']
    prescreen = load(E / 'PUBLICATION_LOCAL/PUBLIC_PRESCREEN.json')
    normalized = collections.Counter((row['path'],re.sub(r'\[\d+\]','[]',row['json_path'])) for row in prescreen['numeric_json_lists_requiring_review'])
    assert len(normalized) == 14
    allowed = {
        ('paper16_development_r4/ACCESS_REGISTRATION.json','$.objects[].candidate_unit_ids'),
        ('paper16_development_r4/ACCESS_REGISTRATION.json','$.denied_final_session_ids'),
        *[('paper16_development_r4/STATE_COMPATIBILITY_MATRIX.json',f'$.states[].{s}') for s in ['feature_identity.shape','scaler_identities.mean.shape','scaler_identities.scale.shape','scaler_identities.active.shape','unit_identity.shape','original_source.candidate_unit_ids']],
        *[('paper16_development_r4/UNIFORM_NUMERICAL_AMENDMENT.json',f'$.policy.{s}') for s in ['bounds.PSTH_and_B0','bounds.nonPSTH','FD_steps','DS_seeds','C_fixed_kernels_seconds','maximum_parameters.main_B0_B1_B2_B3_B4']],
    }
    assert set(normalized) == allowed
    out = {
        'reviewer':'/root/r4_interruption_review',
        'recorded_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'scope':'JSON metadata, task order/arithmetic and appended audit inventory only; no model, source neural array, gradient, scoring or network calls',
        'baseline_exact_statements_checked':254,
        'baseline_statement_mutations':0,
        'trace_status_counts_at_review':dict(collections.Counter(row['status'] for row in trace['items'])),
        'task_identity_and_order_checked':5519,
        'outcome_counts':dict(counts),
        'complete_FG_calls':707125,'complete_accepted_iterations':664219,
        'total_FG_calls_including_partial':707610,'total_accepted_iterations_including_partial':664684,
        'facts_sha256':digest(P / 'EXECUTION_FACTS.json'),
        'task_outcomes_sha256':digest(P / 'TASK_OUTCOMES.json'),
        'protected_supplement_sha256':digest(P / 'PROTECTED_STATE_MANIFEST_SUPPLEMENT_1.json'),
        'numeric_public_array_schema_classes_checked':14,
        'numeric_public_array_meaning':'candidate unit IDs, denied final-session IDs, shape descriptors and frozen numerical policy constants only',
        'prescreen_limit':'Finite regex and type/magic checks are not a guarantee of arbitrary-secret absence; final exact public bytes still require independent manifest review and owner authorization',
        'scientific_pass':False,'public_push_authorized':False,
    }
    with (E / 'INDEPENDENT_CLOSEOUT_METADATA_CHECK_1.json').open('x',encoding='utf8') as handle:
        json.dump(out,handle,indent=2);handle.write('\n')
    print(json.dumps(out,indent=2))

if __name__ == '__main__':
    main()
