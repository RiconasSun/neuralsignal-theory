"""Stopped-track reports from public receipts only; no data/keys/fit access."""
from collections import Counter
from datetime import datetime, timezone
import register as r


def main():
    r.verify()
    gate = r.load(r.HERE / 'results/M2/aggregate4/gate_result.json')
    animals = r.load(r.ROOT / 'paper12_curated_v1/locks/animals.json')
    totals = Counter(); completed = []; failed = []; pending = []
    for animal in animals:
        sid = animal['session_id']
        good = r.HERE / 'results/M2/index2/sessions' / (sid + '.json')
        bad = r.HERE / 'results/M2/index2/failures' / (sid + '.json')
        if bad.exists():
            failed.append(dict(**animal, failure=r.load(bad), failure_sha256=r.sha(bad)))
        elif good.exists():
            record = r.load(good); completed.append(record)
            for region, value in record['eligible_unit_counts'].items():
                totals[animal['group'] + '_' + region] += value
        else:
            pending.append(dict(mouse_id=animal['mouse_id'], session_id=sid, group=animal['group']))
    if gate['gate'] != 'FAIL' or len(failed) != 1 or failed[0]['session_id'] != '779839471' or len(completed) != 8:
        raise RuntimeError('STOPPED_EVIDENCE_DENOMINATOR_CHANGED')
    report = dict(utc=datetime.now(timezone.utc).isoformat(), mission=r.ID,
                  scientific_M2_gate='FAIL', scientific_verdict='INCONCLUSIVE',
                  reason='LOCKED_SOURCE_READ_TIMEOUT; not evidence of biological insufficiency or source corruption',
                  frozen_mouse_denominator=26, completed_QC=gate['completed_QC'],
                  eligible_mice=gate['eligible_mice'], completed_sessions=len(completed),
                  failed_sessions=1, not_executed_sessions=len(pending),
                  eligible_units_in_completed_sessions=dict(totals),
                  failure_records=failed, not_executed_roster=pending,
                  source_full_session_decoded_by_custodian=True,
                  source_decoding_scope='Complete time vectors of processed locked target units,including units processed before the aborted session;not a claim all26 sessions or every target unit were decoded',
                  final_values_exposed_to_analysis=False, final_holdout_evaluated=False,
                  real_AB_analysis_exported=False, real_model_fits_executed=0,
                  M3='NOT_EXECUTED;synthetic implementation preparation only', M4='NOT_EXECUTED',
                  M5='NOT_EXECUTED', M6='NOT_EXECUTED', M7='NOT_EXECUTED',
                  original_evidence_reclassified=False,
                  source_failure_sha256=failed[0]['failure_sha256'],
                  M2_aggregate_sha256=r.sha(r.HERE / 'results/M2/aggregate4/gate_result.json'),
                  recovery_requires='Separate human authorization for a bounded prospective same-source transport recovery; no automatic retry,threshold relaxation,cohort substitution or gate bypass')
    r.save(r.HERE / 'results/closeout.json', report)
    claims = [
        dict(id='C01', claim='Original study gates/splits/locks remain unchanged',
             evidence='registration.json;register.py --verify', scope='Immutable prior files and operations history'),
        dict(id='C02', claim='Specified native no-capability role passed live isolation probes',
             evidence='results/isolation/native_profile_runtime2.json;results/M3/synthetic_native1/role_proof.json',
             scope='Actual synthetic native processes,not the failed tool sandbox;no malicious-host/admin or independent-human isolation claim'),
        dict(id='C03', claim='Four development and four final mice passed completed physiological QC',
             evidence='results/M2/aggregate4/mouse_denominator.csv;results/M2/index2/sessions/',
             scope='8of26 completed;no full-cohort admission;finalQC calibration only;unit details remain private'),
        dict(id='C04', claim='Locked source779839471 aborted on ReadTimeoutError',
             evidence='results/M2/index2/failures/779839471.json;results/closeout.json',
             scope='No partial public partition;network read failure,not proven source corruption'),
        dict(id='C05', claim='No real predictive comparison,nulls or final evaluation executed',
             evidence='MILESTONE_STATUS.md;results/closeout.json',
             scope='Synthetic numerical tests are implementation evidence,not experimental findings'),
        dict(id='C06', claim='Human-authorized method decisions registered prospectively',
             evidence='METHOD_AMBIGUITY_AUDIT.md;method_registration1.json;offset_registration1.json',
             scope='No retroactive gate repair;all57configs/holdouts remain frozen;shared offset does not eliminate all task effects'),
        dict(id='C07', claim='PowerShell reproduction is saved-evidence-only',
             evidence='reproduce.ps1;reproduce_saved.py;results/reproduction_binding.json',
             scope='Does not repeat source extraction,liveOSprobes or unexecuted experiments'),
    ]
    r.save(r.HERE / 'CLAIM_AUDIT.json', dict(claims=claims, preferred_regime='NOT_ASSESSED',
               NAP_validated=False, CWP_validated=False, biological_mechanism_proven=False,
               manuscript_complete=False, scientific_validation_pass=False))
    table = ['| Session | Group | Eligible CA1 | Eligible DG | Status |',
             '| --- | --- | ---: | ---: | --- |']
    for x in completed:
        table.append('| %s | %s | %s | %s | QC completed |' % (x['session_id'], x['group'],
                     x['eligible_unit_counts']['CA1'], x['eligible_unit_counts']['DG']))
    table.append('| 779839471 | final | Not assessed | Not assessed | ReadTimeoutError |')
    text = '\n'.join(table)
    (r.HERE / 'QC_REPORT.md').write_text(
        '# Stopped Physiological QC\n\nNew M2 gate:FAIL / INCONCLUSIVE. Original M2FAIL remains immutable.\n'
        '26frozen candidates:13development/13final.8completed,1failed,17not executed.\n'
        'Actually admitted so far:4development and4final,not the required >=8pergroup.\n'
        'Unknown remaining eligibility is NOT_ASSESSED,not DATA_INSUFFICIENT.\n\n' + text + '\n\n'
        'Completed sessions contain4921eligible session-local units:development CA1=2009,DG=569;'
        'final-calibration CA1=1833,DG=510. These are not primary-model selected-unit counts.\n'
        'Allunit physiological detail and calibration rates remain custody-private.\n'
        'Full26denominator:results/M2/aggregate4/mouse_denominator.csv.\n\n'
        'SOURCE_READ_TIMEOUT aborted9th session without a success receipt or public partition.\n'
        'No source corruption,checksum mismatch or anatomical insufficiency is inferred.\n'
        'No automatic retry or later-milestone execution is permitted by the failed gate.\n', encoding='utf-8')
    (r.HERE / 'MILESTONE_STATUS.md').write_text(
        '# P12 Custody Track - Stopped\n\nMission:P12-M2-ISOLATED-CUSTODY-1.\n'
        'Original M0INCONCLUSIVE,curated M1PASS and original M2FAIL preserved.\n\n'
        '| Stage | Actual status |\n| --- | --- |\n'
        '| Prospective custody registration | PASS |\n'
        '| Provided tool-sandbox isolation | FAIL,preserved;not analysis role |\n'
        '| Native role / synthetic extraction verification | PASS,scope-limited |\n'
        '| Source identity/raw-index audits | 26verified;not physiology |\n'
        '| New M2 real physiology | FAIL / INCONCLUSIVE;8completed,1failed,17notexecuted |\n'
        '| M3 | NOT_EXECUTED;79synthetic/regressiontests include preparation only |\n'
        '| M4 | NOT_EXECUTED;authorized offset registered,not fitted |\n'
        '| M5-M7 | NOT_EXECUTED |\n\n'
        'Critical stop:source779839471 ReadTimeoutError.4development/4final mice admitted sofar.\n'
        'Source vectors decoded bycustodian=true;final analysis exposure=false;final evaluation=false.\n'
        'No real A/B analysis export,real model fit,null test,preferred regime or manuscript.\n'
        'Next requires separate prospective same-source transport recovery authorization.\n', encoding='utf-8')
    print(dict(gate='FAIL', verdict='INCONCLUSIVE', completed=8, failed=1, not_executed=17))


if __name__ == '__main__':
    main()
