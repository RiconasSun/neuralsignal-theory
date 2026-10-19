"""Evidence-only regression: partial/pending work earns no full requirement credit."""
import json
from pathlib import Path
from collections import Counter
import unittest

E = Path(__file__).resolve().parent
R = E.parents[3]
P = R/'paper16_dev_r3'


class RequirementCreditTests(unittest.TestCase):
    def test_full_M2_deliverables_receive_no_completion_credit_from_partial_prefix(self):
        account = json.loads((P/'SOURCE_AND_PHYSIOLOGY_ACCOUNT.json').read_text())
        result = json.loads((E/'REQUIREMENT_RESULTS.json').read_text())
        rows = {r['id']: r for r in result['items']}
        self.assertFalse(account['global_admission_pass'])
        for requirement in ['REQ-273', 'REQ-274', 'REQ-275']:
            self.assertEqual(rows[requirement]['status'], 'BLOCKED_NEED_ENV')
        self.assertEqual(rows['REQ-286']['status'], 'PENDING_ARCHIVE')
        self.assertEqual(result['verified_baseline_count'], 234)

    def test_dispositions_exactly_partition_original_333_rows_without_extra_credit(self):
        original = json.loads((E/'REQUIREMENT_BASELINE.json').read_text())
        result = json.loads((E/'REQUIREMENT_RESULTS.json').read_text())
        self.assertEqual(len(original['items']), len(result['items']))
        self.assertEqual([(r['id'], r['owner_line'], r['requirement']) for r in original['items']],
                         [(r['id'], r['owner_line'], r['requirement']) for r in result['items']])
        counts = dict(Counter(r['status'] for r in result['items']))
        self.assertEqual(counts, result['disposition_counts'])
        self.assertEqual(sum(counts.values()), 333)
        self.assertEqual(counts, {'VERIFIED': 234, 'BLOCKED_NEED_ENV': 7,
                                'CONDITIONAL_NOT_EXECUTED': 88, 'PENDING_ARCHIVE': 4})


if __name__ == '__main__': unittest.main(verbosity=2)
