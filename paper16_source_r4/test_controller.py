"""Real Windows Job/clock and exact R4 phase-claim tests; no source HTTP."""
import datetime
import os
from pathlib import Path
import sys
import tempfile
import time
import unittest
from unittest.mock import patch
from .core import P,SourceStop,ResourceStop,make_stage,once,supervise_child
from .run_sources import worker,supervise,verify_preaccess


class ControllerTests(unittest.TestCase):
    def setUp(self):self.temp=tempfile.TemporaryDirectory(dir=P/'work',prefix='synthetic-control-');self.root=Path(self.temp.name)
    def tearDown(self):self.temp.cleanup()
    def test_unknown_phase_denied_before_approval_or_source(self):
        with patch('paper16_source_r4.run_sources.verify_preaccess',side_effect=AssertionError('No access')):
            for fn in [worker,supervise]:
                for value in ['', 'first', 'FOURTH','../remaining']:
                    with self.assertRaises(SourceStop):fn(value)
    def test_no_approval_denies_before_any_claim_or_HTTP(self):
        with patch('paper16_source_r4.run_sources.load',side_effect=FileNotFoundError('Synthetic missing approval')):
            with self.assertRaises(FileNotFoundError):verify_preaccess()
        claim=self.root/'claim.json';once(claim,{'stage':1})
        with self.assertRaises(FileExistsError):once(claim,{'stage':2})
    def test_actual_R4_child_same_boot_job_and_original_deadline_preserved(self):
        stage=make_stage(20);original=dict(stage);name=f'Local\\P16_R4_TEST_{os.getpid()}_{time.time_ns()}'
        script='from paper16_source_r4.core import require_job;import sys;require_job(sys.argv[1]);print("owned R4 Job test")'
        result=supervise_child([sys.executable,'-c',script,name],stage['deadline_monotonic'],self.root/'child.log',name,stage)
        self.assertEqual(result['returncode'],0);self.assertTrue(result['assigned_before_resume']);self.assertTrue(result['completed_before_deadline'])
        self.assertEqual(stage,original)
    def test_expired_UTC_and_changed_boot_denied_before_child_launch(self):
        good=make_stage(60);wall=datetime.datetime.now(datetime.timezone.utc)-datetime.timedelta(hours=49)
        expired=dict(good,start_UTC=wall.isoformat(),deadline_UTC=(wall+datetime.timedelta(seconds=60)).isoformat())
        for bad in [expired,dict(good,windows_boot_UTC='other boot')]:
            with patch('subprocess.Popen',side_effect=AssertionError('No child')):
                with self.assertRaises(ResourceStop):supervise_child([],bad['deadline_monotonic'],self.root/'no.log',stage=bad)
    def test_actual_grandchild_cannot_continue_after_R4_deadline(self):
        stage=make_stage(2.5);name=f'Local\\P16_R4_KILL_{os.getpid()}_{time.time_ns()}'
        witness,late=self.root/'started',self.root/'late'
        grandchild='from pathlib import Path;import sys,time;Path(sys.argv[1]).write_text("started");time.sleep(4);Path(sys.argv[2]).write_text("MUST_NOT_HAPPEN")'
        child='import sys,subprocess,time;from paper16_source_r4.core import require_job;require_job(sys.argv[1]);subprocess.Popen([sys.executable,"-c",sys.argv[2],sys.argv[3],sys.argv[4]]);time.sleep(30)'
        result=supervise_child([sys.executable,'-c',child,name,grandchild,str(witness),str(late)],stage['deadline_monotonic'],self.root/'kill.log',name,stage)
        self.assertTrue(witness.exists());self.assertTrue(result['killed_at_deadline']);time.sleep(2);self.assertFalse(late.exists())


if __name__=='__main__':unittest.main(verbosity=2)
