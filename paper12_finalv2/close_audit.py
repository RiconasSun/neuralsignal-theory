"""Write the stopped requirement matrix and exact historical daily suffix."""
from datetime import datetime, timezone
from register_audit import BASE, EVIDENCE, HERE, MISSION, ROOT, load, save, sha


def main():
    mission = load(HERE / 'mission.json')
    verified = set(range(1, 15)) | {19, 43, 44} | set(range(51, 60))
    blocked = {15, 16, 17, 18}
    rows = []
    for item in mission['requirements']:
        row = dict(item)
        number = int(item['id'][4:])
        if number in verified:
            row.update(status='VERIFIED', evidence='pre_release_audit.json; CLOSEOUT.md; independent reviews; reproduction_receipts.json; review.md',
                       meaning='Verification of this audit/STOP/preservation requirement only, never final scientific release approval')
        elif number in blocked:
            row.update(status='BLOCKED_HUMAN_INPUT', evidence='G06-G09; independent custody/scientific HOLD reviews',
                       gap='Critical prerelease enforcement prerequisite absent/unverified; current mission explicitly STOPs before repair')
        else:
            row.update(status='OPEN', evidence='No C/D scientific execution; prerelease critical STOP',
                       gap='Conditional downstream stage not entered; not waived, substituted or marked N/A')
        if number == 60:
            row.update(status='OPEN', evidence='External post-commit receipt required',
                       gap='Exact origin/test commit/readback/manifest/clean gate completed outside the committed tree to avoid recursive SHA')
        rows.append(row)
    save(HERE / 'requirement_status.json', {'mission': MISSION, 'base': BASE, 'baseline_requirement_count': 60,
         'verified_baseline_count_before_external_git_closure': sum(z['status'] == 'VERIFIED' for z in rows),
         'requirements': rows, 'scientific_validation_pass': False,
         'required_items_omitted': 0, 'required_behaviors_silently_reduced': 0,
         'unapproved_existing_behaviors_removed': 0, 'required_tests_silently_removed': 0,
         'unresolved_shrink_risk': 0, 'temporary_substitutes_remaining': 0,
         'coverage_reductions_without_approval': 0})
    text = ['# Requirement preservation matrix', '',
            'The immutable 60-item baseline is not rewritten to fit a stopped run. All downstream OPEN requirements remain unmet; no full-mission or scientific PASS is claimed.', '',
            '| ID | Requirement | Status | Evidence / remaining gap |', '|---|---|---|---|']
    for row in rows:
        text.append(f"| {row['id']} | {row['requirement']} | {row['status']} | {row.get('gap', row['evidence'])} |")
    (EVIDENCE / 'preservation_matrix.md').write_text('\n'.join(text) + '\n', encoding='utf-8')
    archive = HERE / 'historical_daily_operations.bin'
    preserved = load(HERE / 'preservation_manifest.json')['tracked_working_bytes_sha256']
    if sha(archive) != preserved['ops/daily-operations.md']:
        raise RuntimeError('DAILY_HISTORY_CHANGED')
    prefix = (f'# Current mission: {MISSION}\n\n'
        f'BASE {BASE}. WAIT_FOR_HUMAN_INPUT after critical Stage 1 prerelease failure. '
        'Independent custody/scientific reviews HOLD: no independently enforceable exactly-once D controller/ledger, '
        'and no C-only/full-sensitivity-state calibration runner. STOP honored; no repair after the failed critical gate, '
        'C exports/fits 0, D release/assessment 0. All four final contrasts INCONCLUSIVE DUE TO FAILED REQUIRED GATE; '
        'effects/p-values/intervals/nulls not computed. Historical M4 failures, development paper, source/models and '
        'all scientific thresholds unchanged. Public-only audit/reproduction and archive-only origin/test Git closure; '
        'external receipt binds exact commit/readback/clean state. Next requires separately authorized pre-release '
        'enforcement engineering without consuming D. Evidence paper12_finalv2/CLOSEOUT.md and '
        'ops/evidence/2026-10-14/p12-predictive-v2-final-validation-1. All historical bytes follow unchanged.\n\n---\n').encode()
    (ROOT / 'ops/daily-operations.md').write_bytes(prefix + archive.read_bytes())
    save(HERE / 'reproduction_receipts.json', {
        'recorded_utc': datetime.now(timezone.utc).isoformat(),
        'original_development_saved_reproduction': {
            'command': '& ./paper12_predictive_v2/reproduce.ps1', 'tool_session_id': 75739, 'exit_code': 0,
            'tests': 43, 'sealed_files': 3389, 'preserved_files': 18763, 'new_fits': 0, 'final_access': False,
            'when': 'Before the new daily status prefix; unchanged prior candidate surface',
            'reproduce_source_sha256': sha(ROOT / 'paper12_predictive_v2/reproduce_saved.py')},
        'initial_public_audit_reproduction': {
            'command': '& ./paper12_finalv2/reproduce.ps1', 'tool_session_id': 31939, 'exit_code': 0,
            'tests': 7, 'preserved_files': 22152, 'new_fits': 0, 'D_assessments': 0,
            'scope': 'Executable public-only audit, not neural/scientific reproduction'},
        'final_sealed_public_reproduction': 'Fresh execution required after final seal; result in external closure receipt',
        'C_D_executable_reproduction': 'NOT_RUN; Stage1 critical STOP; no second final evaluation authorization consumed'})


if __name__ == '__main__':
    main()
