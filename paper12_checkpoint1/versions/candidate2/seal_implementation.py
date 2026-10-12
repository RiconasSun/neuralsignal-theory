from datetime import datetime,timezone
import study as r
from history_guard import verify as verify_history


def main():
    verify_history()
    names=['custody_security.py','envelope.py','atomic_checkpoint.py','native_tests.py','isolation.py','test_envelope.py','test_scope.py','test_diagnostics.py','seal_implementation.py','history_guard.py','METADATA_AMENDMENT2.json','implementation_registration.json','implementation_registration2.json','CANDIDATE2_AMENDMENT.json','DIAGNOSTIC_REGISTRATION3.json','replacement_probe.py','results/native.json','results/candidate1_gate_result.json']
    previous=r.load(r.HERE/'implementation_registration2.json')
    for path in (r.HERE/'versions/candidate1').iterdir():
        if r.sha(path)!=previous['sha256'][path.name]:raise RuntimeError('CANDIDATE1_CODE_SNAPSHOT_MISMATCH')
    r.save(r.HERE/'implementation_registration4.json',dict(utc=datetime.now(timezone.utc).isoformat(),
        registration_sha256=r.sha(r.HERE/'registration.json'),sha256={name:r.sha(r.HERE/name) for name in names},
        neural_source_requests=0,mandatory_native_evaluation_started=False),True)
    print('SYNTHETIC_IMPLEMENTATION_SEALED_BEFORE_NATIVE_EVALUATION')


if __name__=='__main__':main()
