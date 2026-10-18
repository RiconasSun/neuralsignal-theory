"""Archive actual H1 delivery facts; no scientific source or data operations."""
import datetime
from pathlib import Path
import git_closeout as close

E, P, R = close.E, close.P, close.R
archive, original = close.integrity()
receipt = close.read(E / 'H1_REMOTE_READBACK.json')
assert receipt['commit'] == close.git('rev-parse', 'HEAD').decode().strip()
assert receipt['parent'] == close.BASE
assert receipt['remote_readback'] is True and receipt['working_tree_clean'] is True
assert receipt['fetched_origin_test_matches'] is True
assert receipt['changed_file_count'] == 1658
assert receipt['source_archive_sha256'] == close.sha(P / 'ARCHIVE_FREEZE.json')
for item in receipt['changed_files']:
    # H2 may amend only bookkeeping files; all frozen scientific bytes remain unchanged.
    assert close.sha(R / item['path']) == item['sha256'], item['path']
status = close.read(P / 'results/DEVELOPMENT_STATUS.json')
claims = close.read(P / 'results/CLAIM_TO_EVIDENCE_AUDIT.json')
contrasts = {row['contrast']: row for row in claims['contrasts']}
fields = ['EXACT_NATIVE_REPAIR_PASS', 'NATIVE_TIME_BITWISE_VERIFICATION', 'STRICT_PAST_WHEEL_GATE',
          'FULL_A_SOURCE_REVALIDATION', 'CORRECTED_ELIGIBLE_DEVELOPMENT_MICE', 'CORRECTED_DEVELOPMENT_LABS',
          'PRODUCTION_NUMERICAL_PASS', 'ORIGINAL_ATTEMPTS_PRESERVED', 'NEW_MAIN_ATTEMPTS',
          'NEW_SENSITIVITY_ATTEMPTS', 'TOTAL_CUMULATIVE_ATTEMPTS', 'B_SELECTION_FROZEN',
          'DEVELOPMENT_E_COMPLETE', 'FINAL_C_ACCESS', 'FINAL_D_ACCESS', 'PROMPT_4_READY',
          'PROMPT_4_READINESS_SCOPE', 'BUG_COUNT', 'WARN_COUNT']
delivery = {key: status[key] for key in fields}
delivery.update(mission='P15-DEV-EXACT-NATIVE-REPAIR-R1',
    time=datetime.datetime.now(datetime.timezone.utc).isoformat(),
    GIT_COMMIT=receipt['commit'], GIT_COMMIT_SCOPE='Reviewed scientific/source archive H1',
    REMOTE_VERIFICATION={'H1': True, 'receipt': 'H1_REMOTE_READBACK.json',
                         'H2': 'Own post-push verification must pass before terminal return; local ignored work/H2_REMOTE_READBACK.json records actual result'},
    scientific_validation=False, completed_paper=False,
    PRIMARY_DEVELOPMENT_EFFECT=contrasts['B4-B1'],
    SECONDARY_DEVELOPMENT_EFFECTS={k:v for k,v in contrasts.items() if k != 'B4-B1'},
    FALSIFICATION_RESULTS={'primary_N1': claims['primary_N1'], 'primary_N2_gate': claims['primary_N2_gate'],
        'N3': 'B4 wheel-reliance diagnostic only; not a D/C null or all-movement independence test',
        'N4_aggregate_available': False, 'N4_mice': 5, 'N4_required': 6, 'N4_p': 1,
        'valid_reference_suites': 35, 'unavailable_reference_suites': 5, 'reference_bundles': 34965,
        'robust_positive_primary_claim': False,
        'primary_CI_width': 0.09622344576826165, 'original_precision_screen': 0.01,
        'precision_screen_pass': False,
        'full_panels': 'paper15_r1/tables/E_CONTROLS.csv'},
    independent_reviews=['FINAL_SCIENTIFIC_REVIEW_1.md', 'FINAL_NUMERICAL_EVIDENCE_REVIEW_1.md'],
    reproduction={'command': 'powershell -NoProfile -ExecutionPolicy Bypass -File paper15_r1/reproduce.ps1',
                  'native_saved_only_exit_code': 0, 'tests': 126, 'no_real_array_loading': True},
    next_action='STOP. Prompt 4 requires separate explicit human authorization; no Final C/D or next mission.')
close.dump(E / 'FINAL_DELIVERY.json', delivery)
close.matrix_update({'REQ-172', 'REQ-193', 'REQ-195', 'REQ-196'},
                    ['H1_REMOTE_READBACK.json', 'FINAL_DELIVERY.json'], final=True)
matrix = close.read(E / 'PRESERVATION_MATRIX.json')
assert matrix['verified_baseline_count'] == matrix['baseline_requirement_count'] == 196
(E / 'verdict.md').write_text(
    '# Development handoff acceptance and terminal transport gate\n\n'
    'Mission: P15-DEV-EXACT-NATIVE-REPAIR-R1. Development handoff acceptance: PASS. '
    'All196 original baseline obligations are accounted for with unchanged IDs/text, source-bound evidence and actual published H1 Git proof. '
    'bug_count=0; warn_count=0; required_items_omitted=0; required_behaviors_silently_reduced=0; '
    'unapproved_existing_behaviors_removed=0; required_tests_silently_removed=0; unresolved_shrink_risk=0; '
    'temporary_substitutes_remaining=0; coverage_reductions_without_approval=0. '
    'The literal terminal handoff/stop and H2 own live transport checks remain enforced at return; this file does not claim those future checks already ran.\n\n'
    f'H1 scientific archive commit: {receipt["commit"]}. Normal origin/test push, fresh fetch/ls-remote, all1658changed-file blob SHA256s and actual clean tree verified in H1_REMOTE_READBACK.json. '
    'The source archive is unchanged; both complete independent final reviews accepted P0=0/P1=0. '
    'Native saved-only PowerShell reproduction exit0,126 tests; no real fitting, array load or E replay in reproduction or closure.\n\n'
    'Exploratory only:10mice/8labs; old359preserved, new610main+525sensitivity, cumulative1494. '
    'B selection frozen; one E batch,34965reference bundles. Primary mean0.1125291851 nats/unit-bin,95%CI[0.0674581055,0.1636815513],rawp0.0009765625; '
    'primary N1 only7/10<8 and precision width0.09622>0.01 fail their original claim conditions. '
    'N4 aggregate unavailable,5mice<6. Allfive secondary Holm5 p>.05; no demonstrated D/C advantage. '
    'No robust-positive, temporal-dynamics, persistent-state, causal/mechanistic, movement-independent, held-out-validation or completed-paper claim. '
    'Historical failures remain immutable.\n\n'
    'H2 is metadata-only: independent closure review must accept, then normal scoped commit/push, fresh remote SHA/fetched blob checks and clean tree must actually pass. '
    'Actual H2 post-push receipt is written only to ignored paper15_r1/work/H2_REMOTE_READBACK.json to avoid commit-hash self-reference; terminal response supplies the actual commit. '
    'Until these checks pass, internal state is CONTINUE_EXECUTION. No automatic next mission. Final C/D access=false.\n', encoding='utf-8')
(E / 'H2_CLOSURE_CANDIDATE.json').write_text(
    __import__('json').dumps(dict(mission=delivery['mission'], H1_commit=receipt['commit'],
        H1_receipt_sha256=close.sha(E/'H1_REMOTE_READBACK.json'),
        source_archive_sha256=close.sha(P/'ARCHIVE_FREEZE.json'),
        baseline_requirement_count=196, verified_baseline_count=196,
        verified_count_scope='All scientific/reporting obligations and actual H1 archive; literal terminal stop and H2 own transport enforced after commit',
        scientific_validation=False, bug_count=0, warn_count=0,
        final_internal_state='CONTINUE_EXECUTION_UNTIL_H2_REVIEW_PUSH_READBACK_CLEAN_AND_RETURN',
        no_new_scientific_execution=True, Final_C_access=False, Final_D_access=False), indent=2,sort_keys=True)+'\n', encoding='utf-8')
prefix = ('# Current mission: P15-DEV-EXACT-NATIVE-REPAIR-R1\n\n'
          f'Reviewed Development handoff accepted; H1 {receipt["commit"]} published to origin/test and all1658changed files read back with clean tree. '
          'All196 original obligations accounted for. H2 metadata closure review/push/readback/clean and literal terminal handoff remain required before terminal PASS. '
          'Exact-native/source/A/numerical gates PASS;10mice/8labs;historical359preserved;new610main+525sensitivity=1135,cumulative1494; '
          'B frozen,one E complete,126saved-only tests PASS. Exploratory:primaryN1 7/10<8,precisionwidth0.09622>0.01,N4aggregate5<6unavailable,all5secondaryHolm>.05. '
          'No robust-positive/dynamics/mechanism/heldout/completed-paper claim. No Final C/D or automatic Prompt4. '
          f'Evidence: {close.ER}. Original daily bytes unchanged below.\n\n---\n')
(R/'ops/daily-operations.md').write_bytes(prefix.encode()+original)
(E/'NEXT_EXECUTION.md').write_text(
    '# Terminal Development handoff only\n\n'
    'All scientific work is complete and frozen. Do not run further real fits, E predictions, references, Final access or next mission. '
    'H1 actual origin/test SHA/blob readback and clean tree passed. H2 metadata-only independent closure review and live commit/push/readback/clean remain. '
    'After successful H2 transport, return FINAL_DELIVERY facts and actual H2 SHA, then STOP. Prompt4 requires separate explicit human authorization.\n', encoding='utf-8')
close.integrity()
print('H2 metadata candidate:196/196; source archive unchanged; live H2 gates still pending')
