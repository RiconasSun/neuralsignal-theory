"""Seal two independently accepted actual predecessor reviews before one E batch."""
import datetime
from pathlib import Path
from paper15_r1.source import P, R, load_json, dump
from paper15_r1.training import sha, admitted
from paper15_r1.evaluation import verify_E_gate

E = Path(__file__).parent
REVIEWS = {
    'engineering': ('E_BATCH_ADMISSION_REVIEW_1.md','E_BATCH_ADMISSION_REVIEW_RECEIPT_1.json'),
    'mathematics': ('E_NUMERICAL_READINESS_REVIEW_1.md','E_NUMERICAL_READINESS_REVIEW_RECEIPT_1.json'),
}

def validate_review(approval, hashes, report_sha256):
    assert approval['decision'] == 'ACCEPTED_E_BATCH_GATE'
    assert type(approval['open_P0']) is int and approval['open_P0'] == 0
    assert type(approval['open_P1']) is int and approval['open_P1'] == 0
    assert approval['approved_for_one_frozen_E_batch'] is True
    assert approval['hashes'] == hashes
    assert approval['review_sha256'] == report_sha256

def payload_hashes():
    production = load_json((P/'PRODUCTION_GATE.json').read_text())
    paths = set(production['hashes']) | {
        'PRODUCTION_GATE.json','SELECTION_FREEZE.json','results/B_CANDIDATE_SCORES.json',
        'results/BASELINE_ATTEMPTS_COMPLETE.json','results/DYNAMIC_ATTEMPTS_COMPLETE.json',
        'results/MAIN_SAVED_VERIFICATION.json','results/B_SELECTION_SAVED_VERIFICATION.json',
        'REFERENCE_METADATA_FREEZE.json','SENSITIVITY_FIT_PLAN.json','SENSITIVITY_GATE.json',
        'results/SENSITIVITY_PREPARATION.json','results/SENSITIVITY_ATTEMPTS_COMPLETE.json',
        'results/SENSITIVITY_SAVED_VERIFICATION.json',
        'evaluation.py','evaluation_support.py','controls.py','statistics.py','sensitivities.py',
        'sensitivity_fits.py','models.py','features.py','independent_ad.py','training.py','selection.py',
        'source.py','reader.py','source_integrity.py','SOURCE_FILE_FREEZE.json','NEURAL_HEADER_FREEZE.json',
        'READER_GATE.json','results/M2_PHYSIOLOGY_GATE.json','metadata_access.py','cached_source.py',
        'native_table.py','physiology.py','production_admission.py','requirements.txt'}
    preparation = load_json((P/'results/SENSITIVITY_PREPARATION.json').read_text())
    assert len(preparation['records']) == 11*len(admitted())
    paths.update(f"sensitivity_states/{row['subject']}/{row['case']}.json" for row in preparation['records'])
    for subject in admitted():
        paths.update([f'states/{subject}_A_PREPROCESSING.json',f'metadata/{subject}_task.json',f'results/{subject}_A_QC.json'])
    complete = load_json((P/'results/SENSITIVITY_ATTEMPTS_COMPLETE.json').read_text())
    plan = load_json((P/'SENSITIVITY_FIT_PLAN.json').read_text())
    assert complete['attempted'] == complete['completed'] == plan['expected_attempts'] <= 550
    assert not (P/'E_BATCH_CLAIM.json').exists(), 'No second E batch or prefix replacement'
    return {rel:sha(P/rel) for rel in sorted(paths)}

def run():
    target = P/'E_EXPLORATORY_GATE.json'
    assert not target.exists()
    hashes = payload_hashes()
    accepted = {}
    for role,(report_name,receipt_name) in REVIEWS.items():
        report,receipt = E/report_name,E/receipt_name
        approval = load_json(receipt.read_text())
        validate_review(approval,hashes,sha(report))
        accepted[role] = dict(path=report.relative_to(R).as_posix(),sha256=sha(report),
            receipt_path=receipt.relative_to(R).as_posix(),receipt_sha256=sha(receipt))
    limitation = E/'PRE_E_COVERAGE_LIMITATIONS.md'
    assert limitation.exists()
    dump(target,dict(frozen_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        approved_for_one_frozen_E_batch=True,subjects=admitted(),E_batches=1,
        reference_suites=['N1','N2','N3','N4'],replicates=999,reference_refits=0,
        Final_access=False,hashes=hashes,independent_review_evidence=accepted,
        pre_E_coverage_limitations=dict(path=limitation.relative_to(R).as_posix(),sha256=sha(limitation))))
    verify_E_gate()  # Hash/JSON verification only. No E extraction, scoring or claim.
    print('Verified frozen E gate',sha(target),'E batches=0; Final access=false')

if __name__=='__main__':
    run()
