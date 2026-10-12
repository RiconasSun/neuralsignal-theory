"""Saved negative-evidence regressions; no private access or real requests."""
import csv
import unittest
import common as r


class ReportTests(unittest.TestCase):
    def test_frozen_original_timeout(self):
        registered=r.load(r.HERE/'registration.json')
        self.assertEqual(r.sha(r.OLD/'results/M2/index2/failures/779839471.json'),registered['original_timeout_sha256'])

    def test_current_gate_stays_inconclusive(self):
        gate=r.load(r.HERE/'results/M2/gate_result.json')
        self.assertEqual(gate['gate'],'FAIL');self.assertEqual(gate['scientific_verdict'],'INCONCLUSIVE')
        self.assertEqual(gate['eligible_mice'],dict(development=4,final=4))
        self.assertFalse(gate['original_M2_reclassified']);self.assertFalse(gate['final_holdout_evaluated'])

    def test_all26_unknowns_retained(self):
        with (r.HERE/'results/M2/mouse_disposition.csv').open(newline='',encoding='utf-8') as stream:
            rows=list(csv.DictReader(stream))
        self.assertEqual(len(rows),26);self.assertEqual(len({x['mouse_id'] for x in rows}),26)
        self.assertEqual(sum(x['status']=='QC_COMPLETED' for x in rows),8)
        self.assertEqual(sum(x['status']=='EXTRACTION_FAILED' for x in rows),1)
        unknown=[x for x in rows if x['status']=='NOT_EXECUTED'];self.assertEqual(len(unknown),17)
        self.assertTrue(all(x['eligible_CA1']==x['eligible_DG']=='' for x in unknown))

    def test_public_failure_redacted_not_cleared(self):
        receipt=r.load(r.HERE/'results/M2/failures/779839471.json')
        self.assertEqual(receipt['winerror'],5)
        self.assertEqual(receipt['error_code'],'TRANSPORT_CHECKPOINT_COMMIT_PERMISSION_DENIED')
        self.assertNotIn('chunk_',str(receipt));self.assertNotIn('.private',str(receipt))
        self.assertTrue(receipt['source_full_session_decoded_by_custodian'])
        self.assertFalse(receipt['final_values_exposed_to_analysis'])

    def test_all_synthetic_rename_failures_preserved(self):
        audit=r.load(r.HERE/'results/checkpoint_audit.json')
        trials=audit['synthetic_commit_trials'];self.assertEqual(len(trials),20)
        self.assertEqual(sum(not x['rename_pass'] for x in trials),1)
        corrected=r.load(r.HERE/'results/checkpoint_audit_verified2.json')
        self.assertEqual(corrected['original_audit_sha256'],r.sha(r.HERE/'results/checkpoint_audit.json'))
        self.assertFalse(corrected['actual_commit_retried']);self.assertEqual(corrected['source_requests_added'],0)

    def test_aggregate_QC_not_unit_details(self):
        rows=r.load(r.HERE/'results/M2/aggregate_QC_reasons.json')['rows']
        self.assertEqual(len(rows),8)
        self.assertEqual(sum(sum(x['eligible_unit_counts'].values()) for x in rows),4921)
        self.assertTrue(all(not x['unit_level_details_exported'] and not x['final_evaluation_values_read'] for x in rows))


if __name__=='__main__':unittest.main()
