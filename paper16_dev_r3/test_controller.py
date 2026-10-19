"""Actual Windows child/grandchild and frozen-phase denial regressions. Synthetic only."""
from pathlib import Path
import json
import os
import subprocess
import sys
import tempfile
import time
import unittest
from concurrent.futures import ThreadPoolExecutor
import threading
import datetime
import copy
from unittest.mock import patch
from .core import P, E, load, SourceStop, ResourceStop, once
from .run_m2 import phase_name, worker, supervise, supervise_child, verify_preaccess
from .windows_job import Job, require_job
from .clock_bound import make_stage, guard, verify_stage_environment, conservative_deadline


class ControllerTests(unittest.TestCase):
    def setUp(self): self.temp = tempfile.TemporaryDirectory(dir=P/'work', prefix='synthetic-control-'); self.root = Path(self.temp.name)
    def tearDown(self): self.temp.cleanup()

    def test_unknown_phase_denied_before_review_or_sources(self):
        with patch('paper16_dev_r3.run_m2.verify_preaccess', side_effect=AssertionError('Must not inspect/open')):
            for fn in [worker, supervise]:
                for value in ['', 'other', 'FIRST', '../remaining']:
                    with self.assertRaises(SourceStop): fn(value)

    def test_expired_wall_deadline_cannot_reuse_valid_monotonic_epoch(self):
        now = datetime.datetime.now(datetime.timezone.utc)
        stage = dict(start_monotonic=100., deadline_monotonic=172900., no_reset=True,
                     start_UTC=(now-datetime.timedelta(hours=49)).isoformat(),
                     deadline_UTC=(now-datetime.timedelta(hours=1)).isoformat())
        with patch('paper16_dev_r3.clock_bound.time.monotonic', return_value=200.):
            with self.assertRaises(ResourceStop): guard(stage)

    def test_boot_mismatch_or_missing_epoch_denied_before_launch(self):
        stage = make_stage(60)
        for value in ['different boot', None]:
            bad = dict(stage, windows_boot_UTC=value)
            with patch('subprocess.Popen', side_effect=AssertionError('No child may launch')):
                with self.assertRaises(ResourceStop):
                    supervise_child([], stage['deadline_monotonic'], self.root/'denied.log', stage=bad)
        self.assertFalse((self.root/'denied.log').exists())

    def test_same_boot_stage_unchanged_no_deadline_extension(self):
        stage = make_stage(60); original = copy.deepcopy(stage)
        verify_stage_environment(stage); guard(stage)
        self.assertLessEqual(conservative_deadline(stage), stage['deadline_monotonic'])
        self.assertEqual(stage, original)
        result = supervise_child([sys.executable, '-c', "print('same boot synthetic')"],
            stage['deadline_monotonic'], self.root/'sameboot.log', stage=stage)
        self.assertEqual(result['returncode'], 0); self.assertTrue(result['completed_before_deadline'])

    def test_malformed_intervals_clock_rollback_and_unavailable_epoch_fail_closed(self):
        stage = make_stage(60)
        for key, value in [('start_monotonic', float('nan')), ('deadline_monotonic', float('inf')),
                           ('deadline_UTC', 'bad'), ('start_UTC', '2026-01-01T00:00:00'),
                           ('no_reset', False), ('deadline_monotonic', stage['start_monotonic']+172801)]:
            with self.subTest(key=key, value=value):
                with self.assertRaises(ResourceStop): guard(dict(stage, **{key: value}))
        with patch('paper16_dev_r3.clock_bound.utc_now', return_value=datetime.datetime(2000, 1, 1, tzinfo=datetime.timezone.utc)):
            with self.assertRaises(ResourceStop): guard(stage)
        with patch('paper16_dev_r3.clock_bound.boot_identity', side_effect=ResourceStop('Unavailable epoch')):
            with self.assertRaises(ResourceStop): verify_stage_environment(stage)

    def test_missing_review_fail_closed_and_once_claim_is_atomic(self):
        def missing_review(path):
            if path == E/'PREACCESS_APPROVAL.json': raise FileNotFoundError('Synthetic missing approval')
            return load(path)
        with patch('paper16_dev_r3.run_m2.load', side_effect=missing_review):
            with self.assertRaises(FileNotFoundError): verify_preaccess()
        p = self.root/'claim.json'; once(p, {'attempt': 1})
        with self.assertRaises(FileExistsError): once(p, {'attempt': 2})
        self.assertEqual(json.loads(p.read_text())['attempt'], 1)

    def test_simultaneous_claims_have_exactly_one_winner(self):
        barrier = threading.Barrier(2); p = self.root/'concurrent.json'
        def claim(i):
            barrier.wait()
            try: once(p, {'writer': i}); return True
            except FileExistsError: return False
        with ThreadPoolExecutor(max_workers=2) as pool: outcomes = list(pool.map(claim, [1, 2]))
        self.assertEqual(sum(outcomes), 1)
        self.assertIn(json.loads(p.read_text())['writer'], [1, 2])

    def test_real_venv_worker_belongs_to_exact_named_job(self):
        name = f'Local\\P16_R3_TEST_{os.getpid()}_{time.time_ns()}'
        script = "from paper16_dev_r3.windows_job import require_job; import sys,os,json; require_job(sys.argv[1]);print(json.dumps({'worker_pid':os.getpid(),'membership':True}))"
        log = self.root/'normal.log'
        result = supervise_child([sys.executable, '-c', script, name], time.monotonic()+15, log, name)
        self.assertEqual(result['returncode'], 0)
        self.assertTrue(result['native_job_tree_enforced']); self.assertTrue(result['assigned_before_resume'])
        self.assertTrue(json.loads(log.read_text())['membership'])
        self.assertFalse(result['killed_at_deadline'])

    def test_real_job_kills_grandchild_at_deadline(self):
        name = f'Local\\P16_R3_KILLTEST_{os.getpid()}_{time.time_ns()}'
        witness, late = self.root/'grandchild_started', self.root/'unauthorized_late_write'
        grandchild = "from pathlib import Path;import sys,time;Path(sys.argv[1]).write_text('started');time.sleep(4);Path(sys.argv[2]).write_text('MUST_NOT_HAPPEN')"
        child = "import subprocess,sys,time;from paper16_dev_r3.windows_job import require_job;require_job(sys.argv[1]);subprocess.Popen([sys.executable,'-c',sys.argv[2],sys.argv[3],sys.argv[4]]);time.sleep(30)"
        result = supervise_child([sys.executable, '-c', child, name, grandchild, str(witness), str(late)],
                                 time.monotonic()+2.5, self.root/'timeout.log', name)
        self.assertTrue(witness.exists(), 'Grandchild must actually start before deadline test is meaningful')
        self.assertTrue(result['killed_at_deadline']); self.assertFalse(result['completed_before_deadline'])
        time.sleep(2)
        self.assertFalse(late.exists(), 'Descendant continued after supervised deadline')

    def test_named_job_reuse_and_membership_forgery_denied(self):
        name = f'Local\\P16_R3_COLLISION_{os.getpid()}_{time.time_ns()}'
        with Job(name):
            with self.assertRaises(RuntimeError): Job(name)
            with self.assertRaises(RuntimeError): require_job(name)
        with self.assertRaises(OSError): require_job(name)

    def test_expired_deadline_denied_before_process_creation(self):
        with patch('subprocess.Popen', side_effect=AssertionError('Must not create child')):
            with self.assertRaises(ResourceStop): supervise_child([], time.monotonic()-1, self.root/'no.log')
        self.assertFalse((self.root/'no.log').exists())


if __name__ == '__main__': unittest.main(verbosity=2)
