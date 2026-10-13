import hashlib
import unittest
from closure_verify import validate_prefix,validate_failure


class ClosurePreservation(unittest.TestCase):
    def test_stop_failure_is_hash_bound(self):
        validate_failure({'gate':'FAIL'},'original','original')
        with self.assertRaises(RuntimeError):validate_failure({'gate':'FAIL'},'changed','original')
        with self.assertRaises(RuntimeError):validate_failure({'gate':'PASS'},'original','original')

    def test_exact_prefix_only(self):
        original=b'IMMUTABLE HISTORICAL STATUS\r\n';prefix=b'NEW STATUS\n\n';current=prefix+original
        old=hashlib.sha256(original).hexdigest();new=hashlib.sha256(current).hexdigest()
        self.assertTrue(validate_prefix(original,current,prefix,old,new))
        self.assertFalse(validate_prefix(original,current+b'x',prefix,old,new))
        self.assertFalse(validate_prefix(original,current.replace(b'HISTORICAL',b'RECLASSIFIED'),prefix,old,new))
        self.assertFalse(validate_prefix(original,current,prefix+b'UNAPPROVED',old,new))
