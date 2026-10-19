"""Synthetic original 14/3/10 mouse-floor and complete-denominator checks."""
import unittest
from unittest.mock import patch
from . import run_sources as runner


class CohortTests(unittest.TestCase):
    def evaluate(self, bo, fc, missing=False, invalid=False):
        objects = [{'session_id': i + 1, 'protocol': 'brain_observatory_1.1' if i < 5 else 'functional_connectivity'} for i in range(28)]
        accepted = set(range(1, bo + 1)) | set(range(6, 6 + fc))
        written = []

        def saved(path):
            sid = int(path.parent.name)
            if missing and sid == 28:
                raise FileNotFoundError('Original last source incomplete')
            return {'source_pass': not (invalid and sid == 28), 'A_QC_complete': True,
                    'source': objects[sid - 1], 'selection': {'admitted': sid in accepted}}

        with patch.object(runner, 'registration', return_value={'objects': objects}), \
             patch.object(runner, 'load', side_effect=saved), \
             patch.object(runner, 'once', side_effect=lambda path, value: written.append(value)):
            try:
                result = runner.cohort()
            except BaseException:
                self.assertEqual(written, [], 'Incomplete cohort must not publish a decision')
                raise
        self.assertEqual(len(written), 1)
        self.assertEqual(result['sources_completed'], 28)
        self.assertEqual((result['admitted_BO'], result['admitted_FC']), (bo, fc))
        self.assertFalse(result['model_fits_authorized'])
        self.assertEqual(result['model_fits'], 0)
        return result['verdict']

    def test_exact_fourteen_with_three_BO_eleven_FC_passes(self):
        self.assertEqual(self.evaluate(3, 11), 'M2_SOURCE_AND_PHYSIOLOGY_PASS')

    def test_exact_ten_FC_with_five_BO_passes(self):
        self.assertEqual(self.evaluate(5, 10), 'M2_SOURCE_AND_PHYSIOLOGY_PASS')

    def test_thirteen_overall_fails_despite_protocol_floors(self):
        self.assertEqual(self.evaluate(3, 10), 'DATA_INSUFFICIENT')

    def test_two_BO_fails_despite_fourteen_overall(self):
        self.assertEqual(self.evaluate(2, 12), 'DATA_INSUFFICIENT')

    def test_nine_FC_fails_despite_fourteen_overall(self):
        self.assertEqual(self.evaluate(5, 9), 'DATA_INSUFFICIENT')

    def test_twenty_seven_complete_never_substitutes_for_original_twenty_eight(self):
        with self.assertRaises(FileNotFoundError):
            self.evaluate(5, 23, missing=True)

    def test_required_source_integrity_failure_never_becomes_attrition(self):
        with self.assertRaises(runner.SourceStop):
            self.evaluate(5, 23, invalid=True)


if __name__ == '__main__':
    unittest.main(verbosity=2)
