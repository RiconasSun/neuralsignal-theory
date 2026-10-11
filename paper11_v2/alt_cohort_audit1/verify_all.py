"""Verify the complete saved feasibility package, including supplemental outputs."""
from audit import verdict
from register import HERE, OUT, ROOT, read, sha
from verify_saved import main

main()
for name, digest in read(OUT / 'complete_package_lock.json').items():
    assert sha(ROOT / name) == digest, name
fallback = read(OUT / 'figshare_QC.json')
assert verdict(fallback) == read(OUT / 'figshare_gate_result.json')['scientific_verdict'] == 'INCONCLUSIVE'
assert not fallback['archive_opened']
for phase in ('osf_complete', 'documents', 'figshare_document'):
    for receipt in read(OUT / phase / 'receipts.json')['receipts']:
        assert not receipt['data_file_download']
        assert sha(OUT / phase / receipt['local']) == receipt['sha256']
potential = read(OUT / 'published_hippocampal_patient_potential.json')
assert len(potential) == 15
assert sum(p['at_least_one_published_session_ge5'] for p in potential) == 11
assert all(p['full_eligibility'] == 'UNKNOWN' for p in potential)
print('Complete package replay verified: OSF INCONCLUSIVE; Figshare INCONCLUSIVE; no validation arm.')
