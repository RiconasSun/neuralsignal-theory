import unittest
from stage_gate import assess


class StageGateTests(unittest.TestCase):
    def records(self):
        result = []
        for sid in ('s0', 's1'):
            for region in ('CA1', 'DG'):
                for kind in ('stationary', 'history', 'population', 'event', 'drift', 'combined'):
                    for ridge in ([None] if kind == 'stationary' else [.001, .01, .1, 1.]):
                        for seed in (11, 23, 37):
                            result.append(dict(session_id=sid, region=region, kind=kind, ridge=ridge, seed=seed, converged=True))
        return result

    def test_all_seeds_and_mice(self):
        self.assertEqual(assess(self.records(), ['s0', 's1'])['gate'], 'PASS')

    def test_missing_fit(self):
        self.assertEqual(assess(self.records()[1:], ['s0', 's1'])['gate'], 'FAIL')

    def test_not_all_failed_configurations_mandatory(self):
        data = self.records()
        for r in data:
            if r['ridge'] == .001:
                r['converged'] = False
        self.assertEqual(assess(data, ['s0', 's1'])['gate'], 'PASS')

    def test_mandatory_baseline_unavailable(self):
        data = self.records()
        for r in data:
            if r['session_id'] == 's1' and r['kind'] == 'combined':
                r['converged'] = False
        self.assertEqual(assess(data, ['s0', 's1'])['gate'], 'FAIL')

    def test_duplicate_seed_does_not_satisfy_denominator(self):
        data = self.records(); data[0]['seed'] = data[1]['seed']
        self.assertEqual(assess(data, ['s0', 's1'])['gate'], 'FAIL')
