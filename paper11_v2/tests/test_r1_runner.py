"""Runner-only regressions; fixtures and exceptions never invoke model code."""
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import run_r1 as runner


class RunnerTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.out = self.root / 'results' / 'R1'
        self.out.mkdir(parents=True)
        for target, name, value in [
            (runner, 'OUT', self.out),
            (runner, 'PROGRESS', []),
            (runner.base, 'ROOT', self.root),
            (runner.base, 'STUDY', self.root / 'paper11_v2'),
        ]:
            mock = patch.object(target, name, value)
            mock.start()
            self.addCleanup(mock.stop)
        verify = patch.object(runner, 'verify', return_value={})
        verify.start()
        self.addCleanup(verify.stop)

    def save(self, name, data):
        runner.base.save(self.out / name, data, immutable=True)

    def read(self, name):
        return json.loads((self.out / name).read_text(encoding='utf-8'))

    def lock(self):
        hashes = {
            str(p.relative_to(self.root)).replace('\\', '/'): runner.base.digest(p)
            for p in self.out.iterdir()
            if p.is_file() and p.name != 'artifact_lock.json'
        }
        self.save('artifact_lock.json', {'sha256': hashes})

    def test_changed_preceding_output_refused_before_registration(self):
        with patch.object(runner, 'load', return_value={'sha256': {'prior.json': 'expected'}}), \
                patch.object(runner.base, 'digest', return_value='changed'), \
                patch.object(runner.subprocess, 'run') as subprocess_run, \
                patch.object(runner.base, 'save') as save:
            with self.assertRaises(RuntimeError):
                runner.register()
        subprocess_run.assert_not_called()
        save.assert_not_called()

    def test_archive_hashes_come_from_original_registration_and_are_verified(self):
        prior = runner.base.STUDY / 'results' / 'R0_amendment1_code1'
        original = runner.base.STUDY / 'results' / 'R0' / 'registration.json'
        responses = {
            prior / 'artifact_lock.json': {'sha256': {'prior.json': 'expected'}},
            prior / 'gate_result.json': {'gate_verdict': 'PASS'},
            original: {'archive_sha256': {'protected.json': 'original'}},
        }
        with patch.object(runner, 'load', side_effect=lambda p: responses[Path(p)]) as load, \
                patch.object(runner.base, 'digest', side_effect=['expected', 'changed']), \
                patch.object(runner.subprocess, 'run'), \
                patch.object(runner.base, 'save') as save:
            with self.assertRaises(RuntimeError):
                runner.register()
        self.assertIn(original, [call.args[0] for call in load.call_args_list])
        save.assert_not_called()

    def test_started_namespace_refused_without_execution_or_overwrite(self):
        self.save('execution_started.json', {'preserve': 'original'})
        before = (self.out / 'execution_started.json').read_bytes()
        with patch.object(runner, '_execute') as execute:
            with self.assertRaises(RuntimeError):
                runner.execute()
        execute.assert_not_called()
        self.assertEqual((self.out / 'execution_started.json').read_bytes(), before)

    def test_fatal_exception_preserves_progress_and_failed_replay(self):
        runner.PROGRESS.append({'family': 'fixture', 'converged': True})
        with patch.object(runner, '_execute', side_effect=ValueError('fixture constructor failed')):
            self.assertEqual(runner.execute(), 1)
        self.assertEqual(self.read('fatal_exception.json')['rows'], runner.PROGRESS)
        self.assertEqual(self.read('gate_result.json')['gate_verdict'], 'FAIL')
        self.assertEqual(self.read('QC.json')['gate_verdict'], 'FAIL')
        self.assertEqual(runner.replay(), 1)

    def test_existing_diagnostics_survive_late_failure_with_terminal_evidence(self):
        diagnostics = {'synthetic_only': True, 'rows': [{'family': 'fixture'}]}

        def fail_after_diagnostics():
            self.save('fit_diagnostics.json', diagnostics)
            runner.PROGRESS.extend(diagnostics['rows'])
            raise ValueError('late verification failure')

        with patch.object(runner, '_execute', side_effect=fail_after_diagnostics):
            self.assertEqual(runner.execute(), 1)
        self.assertEqual(self.read('fit_diagnostics.json'), diagnostics)
        self.assertEqual(self.read('gate_result.json')['gate_verdict'], 'FAIL')
        self.assertEqual(self.read('QC.json')['gate_verdict'], 'FAIL')
        self.assertTrue((self.out / 'artifact_lock.json').is_file())
        self.assertEqual(runner.replay(), 1)

    def test_fatal_after_saved_pass_cannot_replay_as_success(self):
        def fail_after_pass():
            self.save('gate_result.json', {'gate_verdict': 'PASS'})
            self.save('QC.json', {'gate_verdict': 'PASS'})
            self.lock()
            raise ValueError('post-gate finalization failure')

        with patch.object(runner, '_execute', side_effect=fail_after_pass):
            self.assertEqual(runner.execute(), 1)
        self.assertTrue((self.out / 'fatal_exception.json').is_file())
        try:
            code = runner.replay()
        except (RuntimeError, ValueError):
            return
        self.assertNotEqual(code, 0, 'Fatal execution must not replay as PASS')

    def test_missing_or_corrupt_locked_artifact_never_falls_back_to_execution(self):
        self.save('gate_result.json', {'gate_verdict': 'PASS'})
        self.save('artifact_lock.json', {'sha256': {'results/R1/missing.json': 'expected'}})
        with patch.object(runner, '_execute') as execute:
            with self.assertRaises(RuntimeError):
                runner.replay()
        execute.assert_not_called()
        (self.out / 'missing.json').write_text('{}', encoding='utf-8')
        with patch.object(runner, '_execute') as execute:
            with self.assertRaises(RuntimeError):
                runner.replay()
        execute.assert_not_called()


if __name__ == '__main__':
    unittest.main()
