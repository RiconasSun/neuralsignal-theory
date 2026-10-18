"""Prospective actual corrected-input production gate and readback; zero fits."""
import datetime
from paper15_r1.source import P,R,dump,load_json
from paper15_r1.training import sha,admitted
from paper15_r1.production_admission import required_hashes,verify

E=R/'ops/evidence/2026-10-17/p15-dev-exact-native-repair-r1'
subjects=admitted();assert len(subjects)==10
paths=required_hashes(subjects)
paths|={'source_snapshots/training_A_preparation.py','results/A_PREPARATION_SOURCE_CONTINUITY.json',
    'results/PRODUCTION_GRADIENT_SYNTHETIC.json','test_native_table.py','test_production_admission.py','test_models.py','test_worker.py','test_features.py'}
paths|={f'metadata/{p.name}' for p in (P/'metadata').glob('*_task.json')}
reviews={name:dict(path=(E/file).relative_to(R).as_posix(),sha256=sha(E/file)) for name,file in
    [('full_native_input','FULL_NATIVE_INPUT_REVIEW_1.md'),('production','PRODUCTION_REVIEW_2.md')]}
gate=dict(mission='P15-DEV-EXACT-NATIVE-REPAIR-R1',frozen_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
    PRODUCTION_NUMERICAL_PASS=True,scope='Complete independently accepted corrected original-native input and actual production worker; prospective fresh A fits only. No convergence/B/E/final scientific result implied.',
    hashes={rel:sha(P/rel) for rel in sorted(paths)},independent_review_evidence=reviews,
    corrected_development_mice=10,corrected_development_labs=8,historical_attempts_preserved=359,
    new_main_cap=610,new_sensitivity_cap=550,absolute_main_cap=732,absolute_sensitivity_cap=660,
    solver_amendment=False,scientific_threshold_amendment=False,old_coefficients_reused=False,Final_access=False)
target=P/'PRODUCTION_GATE.json';assert not target.exists();dump(target,gate)
restored=load_json(target.read_text());assert restored==gate
for rel,h in gate['hashes'].items():assert sha(P/rel)==h
verify(restored,load_json((P/'A_FIT_PLAN.json').read_text()))
dump(E/'ACTUAL_PRODUCTION_GATE_READBACK.json',dict(time=datetime.datetime.now(datetime.timezone.utc).isoformat(),
    gate_sha256=sha(target),source_and_input_files_verified=len(paths),reviews=reviews,
    exact_plan=True,native_and_production_gates_pass=True,new_main_attempts=0,new_sensitivity_attempts=0,
    historical_attempts=359,no_old_coefficients=True,Final_access=False))
print('Actual gate sealed/readback',sha(target),'inputs',len(paths),'new attempts0')
