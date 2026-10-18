"""Seal reviewed, actual A-only case states and the original fixed fit plan."""
import datetime
from pathlib import Path
from paper15_r1.source import P, R, load_json, dump
from paper15_r1.training import sha, admitted
from paper15_r1.sensitivity_fits import verify_plan

E = Path(__file__).parent

def run():
    review = E / 'SENSITIVITY_ADMISSION_REVIEW_1.md'
    receipt = E / 'SENSITIVITY_ADMISSION_REVIEW_RECEIPT_1.json'
    assert review.exists() and receipt.exists(), 'Actual case/plan independent review required'
    selection = load_json((P/'SELECTION_FREEZE.json').read_text())
    candidates = load_json((P/'results/B_CANDIDATE_SCORES.json').read_text())
    preparation = load_json((P/'results/SENSITIVITY_PREPARATION.json').read_text())
    plan = load_json((P/'SENSITIVITY_FIT_PLAN.json').read_text())
    verify_plan(plan, selection, candidates, preparation, admitted())
    assert not list((P/'sensitivity_fits').glob('*/*/*.json'))
    paths = {'SENSITIVITY_FIT_PLAN.json','SELECTION_FREEZE.json','results/B_CANDIDATE_SCORES.json',
        'results/SENSITIVITY_PREPARATION.json','models.py','independent_ad.py','features.py',
        'sensitivities.py','sensitivity_fits.py','PRODUCTION_GATE.json','results/MAIN_SAVED_VERIFICATION.json'}
    for row in preparation['records']:
        rel = f"sensitivity_states/{row['subject']}/{row['case']}.json"
        state = load_json((P/rel).read_text())
        assert state['status'] == row['status']
        if state['status'] == 'A_PREPROCESSING_SEALED':
            assert sha(P/rel) == row['state_sha256']
            assert sha(P/'work/sensitivity_A'/row['subject']/(row['case']+'.npz')) == state['A_features_sha256']
        else:
            assert state['unavailability_reasons'] == row['reasons'] and row['reasons']
        paths.add(rel)
    target = P/'SENSITIVITY_GATE.json'
    assert not target.exists()
    dump(target, dict(frozen_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        approved_for_fixed_A_sensitivity_refits=True, expected_attempts=plan['expected_attempts'],
        original_cases=11, original_baseline_families=5, max_retries=0, Final_access=False, E_neural_access=False,
        hashes={rel:sha(P/rel) for rel in sorted(paths)},
        independent_review_evidence={p.name:dict(path=p.relative_to(R).as_posix(),sha256=sha(p)) for p in [review,receipt]}))
    print('Sealed actual sensitivity gate', sha(target), plan['expected_attempts'])

if __name__ == '__main__':
    run()
