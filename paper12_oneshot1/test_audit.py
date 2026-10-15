import copy
import hashlib
from pathlib import Path
import uuid
import unittest
from . import audit as a

class AuditRegressions(unittest.TestCase):
    def test_source_drift_is_failure(self):
        d=a.ROOT/'paper12_oneshot1/jobs'/uuid.uuid4().hex;d.mkdir(parents=True)
        p=d/'public.txt';p.write_bytes(b'changed')
        with self.assertRaisesRegex(ValueError,'FROZEN_HASH_MISMATCH'):a.verify_hashes({'public.txt':hashlib.sha256(b'frozen').hexdigest()},d)
    def test_missing_producer_stops_release(self):
        r=a.decide({'pinned_producer':False,'scientific_evaluator':True,'independent_REAL_D_authority':True})
        self.assertEqual(r['PRE_RELEASE_GATE'],'FAIL');self.assertFalse(r['release_permitted'])
    def test_synthetic_target_does_not_count_as_evaluator(self):
        r=a.decide({'pinned_producer':True,'scientific_evaluator':False,'independent_REAL_D_authority':True})
        self.assertIn('P1-02_MISSING_FROZEN_REAL_D_SCIENTIFIC_EVALUATOR',r['critical_findings'])
    def test_human_permission_is_not_REAL_signature(self):
        r=a.decide({'pinned_producer':True,'scientific_evaluator':True,'independent_REAL_D_authority':False})
        self.assertEqual(r['PRE_RELEASE_GATE'],'FAIL')
    def test_no_implicit_release_even_other_fields_true(self):
        self.assertFalse(a.decide(dict.fromkeys(['pinned_producer','scientific_evaluator','independent_REAL_D_authority'],True))['release_permitted'])
    def test_all_four_contrasts_uncomputed(self):
        contrasts=a.empty_contrasts();self.assertEqual(len(contrasts),4)
        for value in contrasts.values():
            for name in ('CA1_gain','DG_gain','CA1_minus_DG','CI95','raw_p','Holm_p'):self.assertIsNone(value[name])
            self.assertEqual(value['classification'],'INCONCLUSIVE DUE TO FAILED REQUIRED GATE')
    def test_partition_tamper_rejected(self):
        animals=a.read(a.ROOT/'paper12_curated_v1/locks/animals.json');trials=a.read(a.ROOT/'paper12_curated_v1/locks/trials.json');partition=a.read(a.ROOT/'paper12_controls1/final_D_partition_manifest.json');manifest=a.read(a.C/'complete_C_state_manifest.json')
        partition['D_trial_ids'][manifest['cohort'][0]].pop()
        with self.assertRaisesRegex(ValueError,'ORIGINAL_PARTITIONS_REQUIRED'):a.identity_checks(animals,trials,partition,manifest)
    def test_sealed_C_mask_tamper_rejected(self):
        animals=a.read(a.ROOT/'paper12_curated_v1/locks/animals.json');trials=a.read(a.ROOT/'paper12_curated_v1/locks/trials.json');partition=a.read(a.ROOT/'paper12_controls1/final_D_partition_manifest.json');manifest=a.read(a.C/'complete_C_state_manifest.json')
        manifest['cases'][0]['trial_ids'].pop()
        with self.assertRaisesRegex(ValueError,'SEALED_C_TRIAL_METADATA'):a.identity_checks(animals,trials,partition,manifest)
    def test_C_public_PASS_cannot_clear_D_fail(self):
        result=a.compute();self.assertEqual(result['prerelease_public_evidence']['prior_C_public_manifest_hashes'],'PASS');self.assertEqual(result['PRE_RELEASE_GATE'],'FAIL');self.assertFalse(result['D_RELEASE_CONSUMED'])
    def test_exact_frozen_admitted_counts_include_existing_exclusions(self):
        result=a.compute();rows=result['identities'];self.assertEqual(len(rows),13)
        self.assertEqual(sum(r['C_metadata_trials'] for r in rows),4677)
        self.assertEqual(sum(r['D_metadata_trials'] for r in rows),3120)
        self.assertEqual({r['mouse_id'] for r in rows if r['C_metadata_trials']==359},{'760946813','791857608','795770036'})

if __name__=='__main__':unittest.main()
