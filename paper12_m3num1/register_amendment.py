"""Conditional prospective amendment, never reclassifies any historical failure."""
from datetime import datetime,timezone
import study as r
from transitions import completed


def main():
    r.verify()
    native_bindings=completed(r,'diagnosis',120)
    diagnosis=r.load(r.HERE/'results/diagnosis/diagnosis_summary.json')
    gate=r.load(r.HERE/'results/diagnosis/gate_result.json')
    if gate['gate']!='PASS' or not diagnosis['oracles_pass'] or not diagnosis['premature_relative_stopping_confirmed']:
        raise RuntimeError('AUTHORIZED_AMENDMENT_PRECONDITION_FAILED')
    r.save(r.HERE/'optimizer_amendment.json',dict(utc=datetime.now(timezone.utc).isoformat(),
        diagnostic_gate_sha256=r.sha(r.HERE/'results/diagnosis/gate_result.json'),
        diagnostic_summary_sha256=r.sha(r.HERE/'results/diagnosis/diagnosis_summary.json'),
        native_diagnosis_sha256=native_bindings,
        training_input_receipt_sha256=r.sha(r.HERE/'results/training_export_receipt.json'),
        diagnosis_implementation_sha256=r.sha(r.HERE/'implementation_registration.json'),
        runtime_provenance_sha256=r.sha(r.HERE/'results/runtime_provenance.json'),
        runtime_sha256=r.load(r.HERE/'results/runtime_provenance.json')['runtime_sha256'],
        options=dict(ftol=1e-10,gtol=1e-5,maxiter=2000,maxfun=80000),
        projected_gradient_acceptance=.001,scope='All nonstationary M3 fits only; M4 and shared offset unchanged',
        code_sha256={name:r.sha(r.HERE/name) for name in ('smoke_worker.py','launch_repaired.py','register_amendment.py','numerical.py','test_numerical.py','transitions.py')},
        thresholds_or_splits_changed=False,final_access=False),True)
    print('FIXED_M3_OPTIMIZER_AMENDMENT_REGISTERED_BEFORE_REPAIRED_EVALUATION')


if __name__=='__main__':main()
