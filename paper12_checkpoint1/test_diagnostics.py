import unittest
from native_tests import error


class DiagnosticTests(unittest.TestCase):
    def test_child_failure_survives_receipt(self):
        exc=RuntimeError('INTERRUPTION_NOT_EXECUTED');exc.child_diagnostic='synthetic trace'
        exc.child_exit_code=1;exc.child_stdout='synthetic stdout'
        receipt=error(exc)
        self.assertEqual(receipt['child_diagnostic'],'synthetic trace')
        self.assertEqual(receipt['child_exit_code'],1);self.assertEqual(receipt['child_stdout'],'synthetic stdout')
    def test_native_events_survive(self):
        exc=RuntimeError('ATOMIC_COMMIT_SAFE_STOP');exc.events=[dict(attempt=3,native_success=False,winerror=5)]
        self.assertEqual(error(exc)['events'],exc.events)


if __name__=='__main__':unittest.main()
