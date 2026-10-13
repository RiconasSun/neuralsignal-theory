import unittest
import hashlib
from closure_verify import prefix_ok,failure_ok,archive_admission


class ClosureTests(unittest.TestCase):
    def test_archive_requires_exact_stop_registration(self):
        archive_admission({'failed_gate':'results/M4/native/gate_result.json'})
        for record in (None,{}, {'failed_gate':'results/other/gate_result.json'}):
            with self.assertRaises(RuntimeError):archive_admission(record)

    def test_preserve_exact_historical_suffix(self):
        old=b'HISTORICAL FAIL\r\n';prefix=b'NEW TRACK\n';current=prefix+old
        a=hashlib.sha256(old).hexdigest();b=hashlib.sha256(current).hexdigest()
        self.assertTrue(prefix_ok(old,current,prefix,a,b))
        self.assertFalse(prefix_ok(old,current+b'x',prefix,a,b))
        self.assertFalse(prefix_ok(old,current.replace(b'FAIL',b'PASS'),prefix,a,b))

    def test_stop_failure_is_immutable(self):
        failure_ok({'gate':'FAIL'},'same','same')
        with self.assertRaises(RuntimeError):failure_ok({'gate':'PASS'},'same','same')
        with self.assertRaises(RuntimeError):failure_ok({'gate':'FAIL'},'changed','same')
