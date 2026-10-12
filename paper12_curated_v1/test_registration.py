import collections
import unittest
import register as r


class RegistrationTests(unittest.TestCase):
    def test_allocation(self):
        mice = [str(i) for i in range(26)]
        a = r.allocate(mice)
        self.assertEqual(a, r.allocate(list(reversed(mice))))
        self.assertEqual(collections.Counter(a.values()), {'development': 13, 'final': 13})

    def test_duplicate_mouse_rejected(self):
        with self.assertRaises(ValueError):
            r.allocate(['1'] * 26)

    def test_partition_balance_and_final_lock(self):
        trials = [{'trial_index': str(i), 'condition': str(i % 8)} for i in range(600)]
        p = r.partition('x', trials, 'final')
        self.assertEqual(collections.Counter(p.values()), {'calibration': 360, 'locked_evaluation': 240})
        self.assertEqual(p, r.partition('x', list(reversed(trials)), 'final'))
        for condition in range(8):
            self.assertEqual(sum(p[str(i)] == 'calibration' for i in range(condition, 600, 8)), 45)

    def test_no_replenishing(self):
        trials = [{'trial_index': str(i), 'condition': str(i % 8)} for i in range(600)]
        with self.assertRaises(ValueError):
            r.partition('x', trials[:-1], 'development')

    def test_duplicate_trial_rejected(self):
        trials = [{'trial_index': str(i), 'condition': str(i % 8)} for i in range(600)]
        trials[-1] = trials[0]
        with self.assertRaises(ValueError):
            r.partition('x', trials, 'development')

    def test_unknown_invalid_probe_fails_closed(self):
        self.assertIsNone(r.affected(['EcephysProbe', 'unknown'], '1', {'1': 'probeA'}))

    def test_half_open_invalid_overlap(self):
        p = {'probe_id': '1', 'segments': [{'pass': True, 'master_anchor_min_seconds': 0, 'master_anchor_max_seconds': 10}]}
        inv = [{'start': 2, 'stop': 3, 'tags': ['EcephysSession']}]
        self.assertTrue(r.support(p, 0, 2, inv, {'1': 'A'}))
        self.assertFalse(r.support(p, 1, 2.1, inv, {'1': 'A'}))

    def test_no_extrapolation(self):
        p = {'probe_id': '1', 'segments': [{'pass': True, 'master_anchor_min_seconds': 1, 'master_anchor_max_seconds': 2}]}
        self.assertFalse(r.support(p, 0, 2, [], {'1': 'A'}))

    def test_real_inventory_rebuild(self):
        r.verify()
        animals, trials, units = r.build()
        self.assertEqual(animals, r.load(r.HERE / 'locks/animals.json'))
        self.assertEqual(trials, r.load(r.HERE / 'locks/trials.json'))
        self.assertEqual(units, r.load(r.HERE / 'locks/units.json'))
        self.assertEqual(len(animals), 26)
        self.assertEqual(len(trials), 15600)
        self.assertEqual(len({t['trial_id'] for t in trials}), 15600)
        self.assertTrue(all(len(t['nominal_bin_edges']) == 21 for t in trials))


if __name__ == '__main__':
    unittest.main()
