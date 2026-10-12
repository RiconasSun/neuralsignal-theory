import unittest
from aggregate4 import summarize


class AggregationTests(unittest.TestCase):
    def setUp(self):
        self.animals = [dict(mouse_id=str(i), session_id=str(i),
                             group='development' if i < 13 else 'final') for i in range(26)]
        self.records = {a['session_id']: dict(**a, eligible_unit_counts=dict(CA1=5, DG=5),
                       eligible_mouse=True, final_values_exposed_to_analysis=False,
                       final_holdout_evaluated=False,
                       source_full_session_decoded_by_custodian=True) for a in self.animals}

    def test_full_denominator(self):
        result, rows = summarize(self.animals, self.records)
        self.assertEqual(result['gate'], 'PASS')
        self.assertEqual(result['eligible_mice'], dict(development=13, final=13))
        self.assertEqual(len(rows), 26)
        self.assertFalse(result['full_study_validated'])

    def test_pending_not_insufficient(self):
        result, rows = summarize(self.animals, {})
        self.assertEqual(result['scientific_verdict'], 'NOT_ASSESSED')
        self.assertTrue(all(x['eligible_mouse'] is None for x in rows))

    def test_insufficient_not_dropped(self):
        for i in range(6):
            self.records[str(i)].update(eligible_unit_counts=dict(CA1=4, DG=5), eligible_mouse=False)
        result, rows = summarize(self.animals, self.records)
        self.assertEqual(result['scientific_verdict'], 'DATA_INSUFFICIENT')
        self.assertEqual(len(rows), 26)

    def test_failure_stops(self):
        self.records['0'].update(error_code='SOURCE_VERSION_OR_RANGE_INVALID')
        self.assertEqual(summarize(self.animals, self.records)[0]['gate'], 'FAIL')

    def test_access_violation(self):
        self.records['0']['final_holdout_evaluated'] = True
        with self.assertRaisesRegex(ValueError, 'HOLDOUT'):
            summarize(self.animals, self.records)

    def test_wrong_identity(self):
        self.records['0']['mouse_id'] = '999'
        with self.assertRaisesRegex(ValueError, 'MOUSE_IDENTITY'):
            summarize(self.animals, self.records)

    def test_wrong_threshold(self):
        self.records['0']['eligible_unit_counts']['DG'] = 4
        with self.assertRaisesRegex(ValueError, 'THRESHOLD'):
            summarize(self.animals, self.records)

    def test_duplicate_mouse_denominator(self):
        self.animals[0]['mouse_id'] = '1'
        with self.assertRaisesRegex(ValueError, 'MOUSE_DENOMINATOR'):
            summarize(self.animals, {})


if __name__ == '__main__':
    unittest.main()
