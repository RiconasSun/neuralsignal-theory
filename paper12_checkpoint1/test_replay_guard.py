import unittest
import isolation
from isolation_replay2 import adapted
from history_guard import verify


class ReplayGuardTests(unittest.TestCase):
    def test_nested_guard_bound_without_code_change(self):
        clone=adapted()
        self.assertEqual(clone.__code__.co_code,isolation.main.__code__.co_code)
        self.assertIs(clone.__globals__['r'].verify,verify)
        self.assertEqual(set(clone.__globals__),set(isolation.main.__globals__))


if __name__=='__main__':unittest.main()
