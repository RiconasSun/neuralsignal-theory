"""Register the final-validation audit; reads public metadata and source bytes only."""
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
EVIDENCE = ROOT / 'ops/evidence/2026-10-14/p12-predictive-v2-final-validation-1'
MISSION = 'P12-PREDICTIVE-V2-FINAL-VALIDATION-1'
BASE = 'fa32add453326aca87eebe9dc5d237b6e4419f79'


def sha(path):
    value = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1048576), b''):
            value.update(block)
    return value.hexdigest()


def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(value, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write('\n')


REQUIREMENTS = [
    ('pre_release', 'Verify exact authorized BASE, clean tree and origin/test readback'),
    ('pre_release', 'Preserve every historical scientific failure and numerical amendment'),
    ('pre_release', 'Verify exact development manuscript hash'),
    ('pre_release', 'Verify frozen protocol and complete model/source freeze hashes'),
    ('pre_release', 'Freeze own-history primary hypothesis and contrast'),
    ('pre_release', 'Freeze other-unit population-history hypothesis and contrast'),
    ('pre_release', 'Freeze stimulus/time hypothesis and contrast'),
    ('pre_release', 'Freeze combined-feature hypothesis and contrast'),
    ('pre_release', 'Freeze all original positive-claim rules without relaxation'),
    ('pre_release', 'Verify all 13 final mice against unchanged 26-mouse allocation'),
    ('pre_release', 'Verify exact calibration/evaluation trial partitions and masks'),
    ('pre_release', 'Obtain independent complete scientific/numerical plan review'),
    ('pre_release', 'Obtain independent custody and release-control review'),
    ('pre_release', 'Audit historical D non-exposure to restricted scientific analysis role'),
    ('pre_release', 'Verify final access isolation with actual principal evidence'),
    ('pre_release', 'Verify protected C-only calibration and D separation'),
    ('pre_release', 'Verify independently enforceable artifact-bound one-shot release'),
    ('pre_release', 'Verify durable append-only entitlement consumption before D access'),
    ('stop', 'Stop on any critical failed gate before C or D scientific execution'),
    ('calibration', 'Release C only after all Stage 1 gates PASS'),
    ('calibration', 'Apply frozen C-only unit QC and salted unit selection'),
    ('calibration', 'Apply frozen stimulus masks and 100-ms features'),
    ('calibration', 'Fit C-only feature scaling and preserve nested GLM definitions'),
    ('calibration', 'Preserve ridge 0.1, initialization, bounds and solver budgets'),
    ('calibration', 'Refit N on C with all seeds 11/23/37 and coefficient mean'),
    ('calibration', 'Never use development coefficients as final fitted parameters'),
    ('calibration', 'Require original PG <=0.001 and independent error <=1e-5'),
    ('calibration', 'Require all numerical/access/mandatory coverage gates PASS'),
    ('calibration', 'Preserve failed calibration attempts and stop critical failure'),
    ('calibration', 'Freeze every model/scaler/sensitivity/trial/unit state before D'),
    ('evaluation', 'Exactly one D assessment after Stage 1 and 2 PASS'),
    ('evaluation', 'Report own-history CA1-minus-DG effect'),
    ('evaluation', 'Report other-population CA1-minus-DG effect'),
    ('evaluation', 'Report stimulus/time CA1-minus-DG effect'),
    ('evaluation', 'Report combined-feature CA1-minus-DG effect'),
    ('evaluation', 'Equal mouse weighting and paired mouse-level exact sign flips'),
    ('evaluation', 'Holm adjustment across four primary tests'),
    ('evaluation', '10000 whole-mouse bootstrap replicates and frozen 95% intervals'),
    ('evaluation', 'All mandatory sensitivity views and original minimum paired mice'),
    ('evaluation', 'All four frozen 999-replicate final control suites'),
    ('evaluation', 'Apply separate frozen 16-test null correction families'),
    ('verdict', 'Apply all positive-claim interval/direction/LOMO/sensitivity/null rules'),
    ('verdict', 'Classify each of all four contrasts separately with frozen labels'),
    ('verdict', 'Retain null/negative/mixed/inconclusive findings; no equivalence claim'),
    ('manuscript_if_valid_D', 'Update Abstract, Results, Discussion and Conclusion'),
    ('manuscript_if_valid_D', 'Separate exploratory development from held-out evidence'),
    ('manuscript_if_valid_D', 'Update scientific figures and supplementary material'),
    ('manuscript_if_valid_D', 'Complete A1-A10 and claim-to-evidence audit'),
    ('manuscript_if_valid_D', 'Verify saved-results and executable reproduction separately'),
    ('manuscript_if_valid_D', 'Produce final manuscript PDF and supplement with visual QA'),
    ('boundaries', 'Report historical M4 optimization and recording/anatomy limitations'),
    ('boundaries', 'No causal, independent-lab, human, NAP or CWP claims'),
    ('boundaries', 'No second D assessment for retuning'),
    ('boundaries', 'No reshuffling, relaxed thresholds, extra hypotheses or models'),
    ('boundaries', 'No additional recurrent optimization rescue'),
    ('closure', 'Preserve independent unsuccessful reviews and exact STOP evidence'),
    ('closure', 'Provide reproducible public-only audit and honest execution ledger'),
    ('closure', 'Report author-review needs and exact remaining blocker'),
    ('closure', 'Independent stopped-closeout review'),
    ('closure', 'Scoped origin/test commit, remote readback, file hashes and clean tree'),
]


def main():
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    if head != BASE:
        raise RuntimeError('WRONG_BASE')
    paths = subprocess.check_output(['git', 'ls-files', '-z'], cwd=ROOT).decode('utf-8').split('\0')
    preserved = {name: sha(ROOT / name) for name in paths if name}
    EVIDENCE.mkdir(parents=True, exist_ok=False)
    (HERE / 'historical_daily_operations.bin').write_bytes((ROOT / 'ops/daily-operations.md').read_bytes())
    save(HERE / 'preservation_manifest.json', {'base': BASE, 'tracked_working_bytes_sha256': preserved})
    requirements = [{'id': f'REQ-{i:03}', 'stage': stage, 'requirement': description, 'status': 'OPEN'}
                    for i, (stage, description) in enumerate(REQUIREMENTS, 1)]
    mission = {'mission': {'id': MISSION, 'objective': 'Audit frozen final-validation release gates; execute C and one D assessment only if every preceding gate passes; STOP on critical failure.'},
               'base': BASE, 'target': {'workdir': str(ROOT), 'files': ['paper12_finalv2/**', str(EVIDENCE.relative_to(ROOT)), 'ops/daily-operations.md']},
               'requirements': requirements, 'baseline_requirement_count': len(requirements),
               'constraints': ['No source/model/policy repair after critical prerelease failure', 'No C/D neural values or keys in this stopped audit', 'Preserve every historical tracked byte, with original daily text retained as exact suffix'],
               'utc': datetime.now(timezone.utc).isoformat()}
    save(HERE / 'mission.json', mission)
    freeze = load(ROOT / 'paper12_predictive_v2/final_validation_freeze.json')
    binding = dict(freeze['source_configuration_sha256'])
    for name in ('MANUSCRIPT.md', 'A1_A10_CLAIM_AUDIT.md', 'final_manifest.json', 'final_validation_freeze.json'):
        relative = 'paper12_predictive_v2/' + name
        binding[relative] = sha(ROOT / relative)
    save(HERE / 'registration.json', {'mission': MISSION, 'base': BASE, 'utc': mission['utc'],
        'mission_sha256': sha(HERE / 'mission.json'), 'preservation_manifest_sha256': sha(HERE / 'preservation_manifest.json'),
        'source_sha256': binding, 'hypotheses': freeze['hypotheses'], 'all_acceptance_rules_document_sha256': freeze['final_positive_criteria_document_sha256'],
        'no_new_neural_experiments': True, 'C_calibration_fits': 0, 'D_assessments': 0,
        'branch_preflight': {'origin_test': BASE, 'origin_main': None, 'classification': 'ORIGIN_MAIN_ABSENT_TEST_EXACT_BASE', 'working_tree_initial': 'CLEAN'},
        'scope': 'Public source/metadata/saved evidence only; no protected payload/key/array access'})
    lines = ['# Frozen final-validation requirement baseline', '', f'Mission `{MISSION}`; BASE `{BASE}`.',
        '', 'All 60 atomic requirements remain individually traceable. Stages 2-5 are conditional on preceding gates; an audit STOP is not scientific validation or completion of those stages.',
        '', 'No product/model code is changed. Oracle: exact frozen byte hashes, metadata identity/partition equality, independent source reviews, and an explicit fail-closed critical-gate decision.',
        '', 'Review must not read C/D neural payloads or keys. No local mock can certify final access enforcement. Actual final-native principal proof is required for release and remains unverified here.',
        '', '| ID | Stage | Requirement | Initial status |', '|---|---|---|---|']
    lines += [f"| {z['id']} | {z['stage']} | {z['requirement']} | OPEN |" for z in requirements]
    lines += ['', 'Preservation: all pre-existing tracked working bytes sealed; no reset/clean/broad staging. Original M4 INCONCLUSIVE, failed numerical experiments and all amendments remain immutable.',
        '', 'Required checks: saved-byte/metadata audit, focused audit regression tests and independent review; scientific execution requires additional actual native-access and numerical proofs.',
        '', 'Critical STOP exit: no C release/fitting and no D evaluation if a mandatory release requirement fails. No inference about regional effects is permitted from a missing final assessment.']
    (EVIDENCE / 'goldenstandards.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(json.dumps({'registered': MISSION, 'requirements': len(requirements), 'preserved_files': len(preserved), 'C_fits': 0, 'D_assessments': 0}))


if __name__ == '__main__':
    main()
