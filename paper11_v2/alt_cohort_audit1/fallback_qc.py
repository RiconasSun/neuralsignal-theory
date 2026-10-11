"""Evaluate only the next candidate's public archive-level metadata."""
from datetime import datetime, timezone
from audit import verdict
from register import OUT, read, save, sha

article = read(OUT / 'figshare/inventory.json')['article']
version = read(OUT / 'figshare_document/000.receipt')
assert article['version'] == version['version'] == 1
assert article['files'] == version['files']
qc = {'candidate': 'Figshare14905317.v1', 'version_doi': version['doi'],
      'complete_inventory': True, 'inventory_scope': 'Top-level public article files only; NOT archive contents',
      'pinned_version': True, 'license_established': version['license']['name'] == 'CC BY 4.0',
      'canonical_patient_mapping': False, 'independence_supported': True,
      'independence_scope': 'Published Birmingham/Erlangen source sites, no private identity proof',
      'native_recording_support': False, 'gaps_verified': False, 'clock_mapping_verified': False,
      'documented_eligible_patients': 0, 'cohort_eligibility_complete': False,
      'authoritative_incompatibility': False, 'files': version['files'],
      'archive_opened': False, 'candidate_spike_values_accessed': False,
      'candidate_outcome_values_accessed': False, 'eligible_count_not_established': True}
save(OUT / 'figshare_QC.json', qc)
save(OUT / 'figshare_gate_result.json', {'candidate': qc['candidate'],
     'scientific_verdict': verdict(qc), 'QC_sha256': sha(OUT / 'figshare_QC.json'),
     'evaluated_utc': datetime.now(timezone.utc).isoformat(), 'stop': True,
     'new_validation_arm_admitted': False, 'interpretation': 'Archive-level feasibility only, no completed physiological admission'})
print('Figshare next-candidate gate:', verdict(qc))
