"""Saved synthetic evidence admission; never reclassify scientific gates."""
from collections import Counter
import study as r
from history_guard import verify


def assess(native,isolation,regressions):
    rows=native['noninjected_commits'];tests=native['injected_tests']
    contexts=Counter(x['context'] for x in rows)
    failures=sum(not x['passed'] for x in rows)
    checks=dict(exact_registered_noninjected_denominator=len(rows)==200,
        two_registered_native_contexts=contexts==Counter(trusted_host_main=100,fresh_trusted_host_child=100),
        zero_unexpected_operation_failures=failures==0,
        all18_injection_oracles=len(tests)==18 and all(x['test_pass'] for x in tests),
        all200_original_diagnostics_retained=len(native['original_directory_rename_trials'])==200,
        candidate_end_hash_verified=native.get('end_implementation_verified') is True,
        native_security=isolation.get('mandatory_isolation_pass') is True,
        old_saved_regressions=regressions.get('saved_checks_pass') is True,
        no_neural_access=native['neural_source_requests']==0 and native['protected_neural_contents_read'] is False)
    return dict(gate='PASS' if all(checks.values()) else 'FAIL',
        verdict='SYNTHETIC_CHECKPOINT_REPAIR_VERIFIED' if all(checks.values()) else 'INCONCLUSIVE/CHECKPOINT_REPAIR_UNVERIFIED',
        checks=checks,noninjected_operation_count=len(rows),unexpected_operation_failures=failures,
        native_retry_denial_events=sum(not event['native_success'] for row in rows if row['passed'] for event in row['receipt']['events']),
        injection_tests_pass=sum(x['test_pass'] for x in tests),injection_test_count=len(tests),
        original_directory_failures=sum(not x['rename_pass'] for x in native['original_directory_rename_trials']),
        scope='Synthetic-only this Windows machine/volume; no real transport integration,science admission,neural validation or power-loss guarantee',
        original_M2_reclassified=False,real_extraction_restarted=False,neural_source_requests=0,
        protected_neural_contents_read=False,final_evaluation_unlocked=False,M3_M7_executed=False,
        separate_human_authorization_required_for_real_continuation=True)


def main():
    verify();native=r.load(r.HERE/'results/native3.json')
    isolation=r.load(r.HERE/'results/isolation3.json') if (r.HERE/'results/isolation3.json').exists() else {}
    regressions=r.load(r.HERE/'results/prior_regressions/receipt.json') if (r.HERE/'results/prior_regressions/receipt.json').exists() else {}
    result=assess(native,isolation,regressions)
    seal=r.load(r.HERE/'implementation_registration5.json')
    result['checks']['actual_code_and_seal_binding']=native['implementation_registration_sha256']==r.sha(r.HERE/'implementation_registration5.json') and all(r.sha(r.HERE/name)==digest for name,digest in seal['sha256'].items())
    tests=r.load(r.HERE/'results/focused_tests.json') if (r.HERE/'results/focused_tests.json').exists() else {}
    result['checks']['focused_tests_bound']=tests.get('passed') is True and all(r.sha(r.HERE/name)==digest for name,digest in tests.get('test_sha256',{}).items())
    boundary=r.load(r.HERE/'results/boundaries.json')
    result['checks']['synthetic_maximum_size_boundaries']=boundary['passed'] is True and boundary['code_sha256']==r.sha(r.HERE/'boundary_cases.py')
    if not all(result['checks'].values()):result.update(gate='FAIL',verdict='INCONCLUSIVE/CHECKPOINT_REPAIR_UNVERIFIED')
    result['input_sha256']={name:r.sha(r.HERE/name) for name in ('results/native3.json','implementation_registration5.json')}
    for name in ('results/isolation3.json','results/prior_regressions/receipt.json'):
        if (r.HERE/name).exists():result['input_sha256'][name]=r.sha(r.HERE/name)
    r.save(r.HERE/'results/gate_result.json',result);print(result)


if __name__=='__main__':main()
