"""Synthetic input tests for the new transport adapter, without real source opens."""
import copy
import tempfile
from pathlib import Path
import unittest
import numpy as np
from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from .trusted_host import canonical, decode_selected, digest, reserve, source_files

TEST_ROOT = Path(__file__).resolve().parent / 'work/test_tmp'


class TransportTests(unittest.TestCase):
    def setUp(self):
        TEST_ROOT.mkdir(parents=True, exist_ok=True)
        self.counts = np.arange(2 * 20 * 6, dtype='<u4').reshape(2, 20, 6)
        self.part = {'trial_ids': ['x', 'y'], 'conditions': [0, 1], 'orders': [1, 3]}
        self.cases = [{'region': r, 'view': 'primary', 'unit_ids': ids}
                      for r, ids in [('CA1', ['u4', 'u1']), ('DG', ['u5', 'u0'])]]
        self.context = {'compartment': 'D', 'shape': [2, 20, 6], 'dtype': '<u4'}
        self.key = bytes(range(32)); self.nonce = bytes(range(12))
        self.envelope = b'P12GCM1\0' + self.nonce + AESGCM(self.key).encrypt(self.nonce, self.counts.tobytes(), canonical(self.context))
        self.item = {'source_unit_ids': ['u' + str(i) for i in range(6)], 'context': self.context,
                     'ciphertext_sha256': digest(self.envelope), 'cipher_file': 'x/D.gcm', 'key_file': 'x/D.key'}

    def test_exact_selected_order_and_context(self):
        f = decode_selected(self.envelope, self.key, self.item, self.cases, self.part)
        np.testing.assert_array_equal(f['CA1_D'], self.counts[:, :, [4, 1]])
        np.testing.assert_array_equal(f['DG_D'], self.counts[:, :, [5, 0]])
        self.assertEqual(f['trial_ids_D'].tolist(), ['x', 'y'])
        self.assertEqual(f['orders_D'].tolist(), [1, 3])
        self.assertEqual(set(f), {'CA1_D', 'DG_D', 'CA1_unit_ids', 'DG_unit_ids', 'trial_ids_D', 'conditions_D', 'orders_D'})

    def test_ciphertext_hash_tamper(self):
        with self.assertRaisesRegex(PermissionError, 'INTEGRITY'):
            decode_selected(self.envelope[:-1] + b'0', self.key, self.item, self.cases, self.part)

    def test_wrong_key(self):
        with self.assertRaises(InvalidTag):
            decode_selected(self.envelope, b'X' * 32, self.item, self.cases, self.part)

    def test_incorrect_key_length(self):
        with self.assertRaisesRegex(PermissionError, 'KEY_LENGTH'):
            decode_selected(self.envelope, b'X', self.item, self.cases, self.part)

    def test_authenticated_context(self):
        item = copy.deepcopy(self.item); item['context']['compartment'] = 'C'
        with self.assertRaises(InvalidTag):
            decode_selected(self.envelope, self.key, item, self.cases, self.part)

    def test_authenticated_wrong_shape(self):
        item = copy.deepcopy(self.item); item['context']['shape'] = [2, 20, 7]
        e = b'P12GCM1\0' + self.nonce + AESGCM(self.key).encrypt(self.nonce, self.counts.tobytes(), canonical(item['context']))
        item['ciphertext_sha256'] = digest(e)
        with self.assertRaisesRegex(PermissionError, 'PAYLOAD_LENGTH'):
            decode_selected(e, self.key, item, self.cases, self.part)

    def test_trial_shape_mismatch(self):
        part = copy.deepcopy(self.part); part['trial_ids'].append('z')
        with self.assertRaisesRegex(PermissionError, 'PAYLOAD_LENGTH'):
            decode_selected(self.envelope, self.key, self.item, self.cases, part)

    def test_missing_selected_unit(self):
        cases = copy.deepcopy(self.cases); cases[0]['unit_ids'].append('absent')
        with self.assertRaises(ValueError):
            decode_selected(self.envelope, self.key, self.item, cases, self.part)

    def test_reservation_never_resets_after_interruption(self):
        with tempfile.TemporaryDirectory(dir=TEST_ROOT) as t:
            p = Path(t) / 'reservation.json'; reserve(p, {'started': True})
            old = p.read_bytes()
            with self.assertRaises(FileExistsError): reserve(p, {'restarted': True})
            self.assertEqual(p.read_bytes(), old)

    def test_synthetic_cannot_use_original_root(self):
        with tempfile.TemporaryDirectory(dir=TEST_ROOT) as t:
            with self.assertRaisesRegex(PermissionError, 'SYNTHETIC_SOURCE_BOUNDARY'):
                source_files(Path(t), self.item, 'SYNTHETIC', Path(t) / 'run')

    def test_synthetic_path_traversal_denied(self):
        with tempfile.TemporaryDirectory(dir=TEST_ROOT) as t:
            run = Path(t); root = run / 'private/synthetic_sources'; root.mkdir(parents=True)
            item = dict(self.item, cipher_file='../other.gcm')
            with self.assertRaises(PermissionError): source_files(root, item, 'SYNTHETIC', run)

    def test_mode_required(self):
        with tempfile.TemporaryDirectory(dir=TEST_ROOT) as t:
            with self.assertRaisesRegex(PermissionError, 'EXPLICIT_MODE'):
                source_files(t, self.item, 'unknown', t)


if __name__ == '__main__':
    unittest.main()
