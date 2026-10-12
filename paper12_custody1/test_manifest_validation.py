import copy
import unittest
from manifest_validation import validate_manifest


class ManifestTests(unittest.TestCase):
    def setUp(self):
        self.animals = [dict(session_id=str(i), mouse_id=str(i), group='development' if i < 13 else 'final') for i in range(26)]
        self.qc = {a['session_id']: dict(**a, eligible_mouse=True) for a in self.animals}
        self.manifest = dict(group='development', compartments=['A', 'B'], M2_gate_sha256='gate',
                             development_registration_sha256='registration',
                             sessions=[dict(mouse_id=str(i), session_id=str(i), file=str(i)+'.npz') for i in range(13)])

    def check(self):
        return validate_manifest(self.manifest, self.animals, self.qc, 'gate', 'registration')

    def test_exact_roster(self):
        self.assertTrue(self.check())

    def test_duplicate_mice(self):
        self.manifest['sessions'][0]['mouse_id'] = '1'
        with self.assertRaisesRegex(ValueError, 'DUPLICATED'):
            self.check()

    def test_duplicate_session(self):
        self.manifest['sessions'].append(copy.deepcopy(self.manifest['sessions'][0]))
        with self.assertRaisesRegex(ValueError, 'DUPLICATED'):
            self.check()

    def test_missing_eligible_mouse(self):
        self.manifest['sessions'].pop()
        with self.assertRaisesRegex(ValueError, 'EXACT_ELIGIBLE'):
            self.check()

    def test_final_mouse_injection(self):
        self.manifest['sessions'][0].update(mouse_id='13', session_id='13', file='13.npz')
        with self.assertRaisesRegex(ValueError, 'EXACT_ELIGIBLE'):
            self.check()

    def test_stale_gate(self):
        self.manifest['M2_gate_sha256'] = 'stale'
        with self.assertRaisesRegex(ValueError, 'PROVENANCE'):
            self.check()

    def test_stale_registration(self):
        self.manifest['development_registration_sha256'] = 'stale'
        with self.assertRaisesRegex(ValueError, 'PROVENANCE'):
            self.check()

    def test_path_escape(self):
        self.manifest['sessions'][0]['file'] = '../0.npz'
        with self.assertRaisesRegex(ValueError, 'FILENAME'):
            self.check()

    def test_final_partition_rejected(self):
        self.manifest['compartments'] = ['A', 'D']
        with self.assertRaisesRegex(ValueError, 'PARTITION'):
            self.check()


if __name__ == '__main__':
    unittest.main()
