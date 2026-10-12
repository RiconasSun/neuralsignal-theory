"""Synthetic regression for P1 replay candidate binding; no experimental values."""
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[3] / 'paper12_custody1'))
import register as r
import reproduce_saved2 as replay
import finalize_evidence2 as binder


class FreshnessTests(unittest.TestCase):
    def setUp(self):
        self.workspace_temp = r.HERE / 'replay/freshness_fixtures'
        self.workspace_temp.mkdir(parents=True, exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=self.workspace_temp)
        self.root = Path(self.temp.name)
        self.fixture = self.root / 'fixture.txt'; self.fixture.write_text('synthetic', encoding='utf-8')
        self.manifest = self.root / 'final_source_manifest2.json'
        self.manifest.write_text(json.dumps(dict(sha256={'fixture.txt': r.sha(self.fixture)})), encoding='utf-8')
        self.initial = r.sha(self.manifest)
        self.context = patch.object(r, 'HERE', self.root); self.context.start()

    def tearDown(self):
        self.context.stop()
        if not self.root.resolve().is_relative_to(self.workspace_temp.resolve()):
            raise RuntimeError('FIXTURE_CLEANUP_PATH_OUTSIDE_TEST_ROOT')
        self.temp.cleanup()

    def test_unchanged_candidate(self):
        self.assertEqual(replay.verify_manifest(self.initial), self.initial)

    def test_input_change_rejected(self):
        self.fixture.write_text('changed', encoding='utf-8')
        with self.assertRaisesRegex(RuntimeError, 'INPUT_CHANGED'):
            replay.verify_manifest(self.initial)

    def test_manifest_change_rejected(self):
        self.manifest.write_text('{}', encoding='utf-8')
        with self.assertRaisesRegex(RuntimeError, 'IDENTITY_CHANGED'):
            replay.verify_manifest(self.initial)

    def test_manifest_change_during_verification_rejected(self):
        actual_sha = r.sha; calls = 0
        def changing_sha(path):
            nonlocal calls
            if Path(path) == self.manifest:
                calls += 1
                if calls == 2:
                    self.manifest.write_text('{}', encoding='utf-8')
            return actual_sha(path)
        with patch.object(r, 'sha', changing_sha), self.assertRaisesRegex(RuntimeError, 'DURING_VERIFICATION'):
            replay.verify_manifest(self.initial)

    def test_stale_binding_rejected_without_publishing(self):
        folder = self.root / 'replay/revision2'; folder.mkdir(parents=True)
        receipt = dict(start_manifest_sha256=self.initial, end_manifest_sha256=self.initial,
                       end_inputs_revalidated=True, saved_checks_pass=True, saved_M2_gate='FAIL', checks=[])
        (folder / 'reproduction_receipt.json').write_text(json.dumps(receipt), encoding='utf-8')
        self.fixture.write_text('changed after run', encoding='utf-8')
        with patch.object(sys, 'argv', ['binder', '--bind-reproduction']), self.assertRaisesRegex(RuntimeError, 'INPUT_CHANGED'):
            binder.main()
        self.assertFalse((self.root / 'results/reproduction_binding2.json').exists())


if __name__ == '__main__':
    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(FreshnessTests))
    r.save(HERE / 'freshness_regression_result.json', dict(tests_run=result.testsRun,
           failures=len(result.failures), errors=len(result.errors), passed=result.wasSuccessful(),
           test_source_sha256=r.sha(__file__), synthetic_only=True, final_holdout_accessed=False))
    sys.exit(0 if result.wasSuccessful() else 1)
