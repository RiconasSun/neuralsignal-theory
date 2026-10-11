"""Read-only repeatable audit reproduction; no network or neural reads."""
import json
from audit import replay, verdict
from register import OUT, ROOT, read, sha, verify


def main():
    reg = verify()
    replay()
    for name, digest in read(OUT / 'QC_implementation_registration.json')['source_sha256'].items():
        assert sha(ROOT / name) == digest, name
    for item in read(OUT / 'documents/standalone_document_receipts.json'):
        assert item['verified'] and item['sha256'] == item['provider_sha256']
        assert sha(OUT / 'documents' / item['local']) == item['sha256']
    qc = read(OUT / 'QC.json')
    patients = read(OUT / 'patient_QC.json')
    sessions = read(OUT / 'session_QC.json')
    assert sum(p['session_count'] for p in patients) == len(sessions)
    assert all(p['eligible'] == 'UNKNOWN' and not p['excluded'] for p in patients)
    assert verdict(qc) == 'INCONCLUSIVE'
    assert read(OUT / 'tests_result.json')['exit_code'] == 0
    print(json.dumps({'prior_files_verified': len(reg['preserved_tracked_sha256']),
                      'file_metadata_count': qc['files'], 'session_labels': len(sessions),
                      'patient_file_labels': len(patients), 'science': verdict(qc),
                      'no_network_or_neural_access': True}))


if __name__ == '__main__':
    main()
