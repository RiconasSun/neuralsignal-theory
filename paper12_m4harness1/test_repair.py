import ast
import hashlib
import unittest
from register import OLD_LINE,NEW_LINE,candidate,IDENTITIES


class RepairScope(unittest.TestCase):
    def test_one_character_only(self):
        original=b'prefix\r\n'+OLD_LINE+b'\r\nsuffix'
        repaired=candidate(original)
        self.assertEqual(len(repaired)-len(original),1)
        self.assertEqual(repaired.replace(NEW_LINE,OLD_LINE,1),original)
        self.assertEqual(repaired,b'prefix\r\n'+NEW_LINE+b'\r\nsuffix')

    def test_fail_closed_other_or_duplicate_location(self):
        for value in (b'other',OLD_LINE+OLD_LINE):
            with self.assertRaises(RuntimeError):candidate(value)

    def test_five_exact_frozen_identities(self):
        self.assertEqual(len(IDENTITIES),5)
        self.assertEqual(len(set(IDENTITIES)),5)
        self.assertEqual(set(IDENTITIES),{'test_poisson_analytic','test_exhaustive_states',
            'test_all_gradients_and_ridge_exposure','test_causal_future_and_batch_reset','test_archived_batch_sequential_parity'})

    def test_original_copy_and_repaired_ast(self):
        from pathlib import Path
        root=Path(__file__).resolve().parent
        original=(root/'original/m4_numerical_tests.py.txt').read_bytes()
        repaired=(root/'patched/m4_numerical_tests.py').read_bytes()
        self.assertEqual(candidate(original),repaired)
        self.assertEqual(ast.dump(ast.parse(candidate(original))),ast.dump(ast.parse(repaired)))
        with self.assertRaises(SyntaxError):compile(original,'immutable_original','exec')
