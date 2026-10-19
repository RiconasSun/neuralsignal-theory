"""Saved real Development A stop-integrity regressions; no fits/source/Final access."""
import copy
import unittest
from unittest.mock import patch
from .core import P, load, sha
from .saved_m2 import verify
from .verify_stop import verify_stop


class SavedStopTests(unittest.TestCase):
    def test_saved_stop_replays_228_A_states_and_all_679_private_hashes_offline(self):
        with patch('socket.socket.connect', side_effect=AssertionError('No network')):
            value = verify_stop(require_freeze=False)
        self.assertEqual(value['A_candidate_states_replayed'], 228)
        self.assertEqual(value['full_private_stop_inventory_verified'], 679)
        self.assertFalse(value['M2_complete']); self.assertFalse(value['M3_M5_executed'])

    def test_corrupt_private_A_receipt_fails_without_changing_saved_files(self):
        target = (P/'work/private/A/750749662/951877136.npz').resolve()
        def corrupt(path): return '0'*64 if path.resolve() == target else sha(path)
        with patch('paper16_dev_r3.saved_m2.sha', side_effect=corrupt):
            with self.assertRaises(AssertionError): verify()
        self.assertNotEqual(sha(target), '0'*64)

    def test_partial_source_cannot_be_promoted_or_counters_inflated(self):
        def wrong_account(path):
            value = load(path)
            if path == P/'SOURCE_AND_PHYSIOLOGY_ACCOUNT.json':
                value = copy.deepcopy(value); value['complete_sources'] = 4
            return value
        with patch('paper16_dev_r3.verify_stop.load', side_effect=wrong_account):
            with self.assertRaises(AssertionError): verify_stop(require_freeze=False)

    def test_incomplete_private_range_cannot_be_silently_treated_complete(self):
        def wrong_inventory(path):
            value = load(path)
            if path == P/'PRIVATE_STOP_INVENTORY.json':
                value = copy.deepcopy(value)
                for row in value['files']:
                    if row['path'].endswith('/447741952.bin'): row['complete_cache_receipt_present'] = True
            return value
        with patch('paper16_dev_r3.verify_stop.load', side_effect=wrong_inventory):
            with self.assertRaises(AssertionError): verify_stop(require_freeze=False)


if __name__ == '__main__': unittest.main(verbosity=2)
