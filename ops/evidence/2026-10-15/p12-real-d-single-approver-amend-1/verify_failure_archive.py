"""Saved public archive only: preserve the invalid old self-entry and verify its supplement."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import unittest

E = Path(__file__).resolve().parent
ARCHIVE = E / 'failed_synthetic_attempt_1'
MANIFEST = E / 'failed_attempt1_byte_manifest_v2.json'
OLD_SHA = 'e6043ed4293962d93b3a9a92fc56b2f39496944a55471d32814ebe2b44c75b50'


def require(value, label):
    if not value:
        raise RuntimeError(label)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def verify(document):
    require(not MANIFEST.resolve().is_relative_to(ARCHIVE.resolve()), 'MANIFEST_OUTSIDE_SOURCE_TREE')
    require(document['source_tree'] == ARCHIVE.name and document['self_not_included'] is True, 'NONRECURSIVE_DECLARATION')
    files = document['files']
    for name in files:
        require(not Path(name).is_absolute() and '..' not in Path(name).parts, 'NO_SELF_REFERENCE_OR_TRAVERSAL')
        require((ARCHIVE / name).resolve().is_relative_to(ARCHIVE.resolve()), 'ARCHIVE_BOUNDARY')
    actual = {p.relative_to(ARCHIVE).as_posix(): p for p in ARCHIVE.rglob('*') if p.is_file()}
    require(set(files) == set(actual) and len(files) == document['file_count'] == 73, 'COMPLETE_EXACT_ROSTER')
    for name, path in actual.items():
        require(digest(path.read_bytes()) == files[name], 'ACTUAL_FILE_HASH:' + name)
    raw = (ARCHIVE / 'inventory.json').read_bytes()
    old = json.loads(raw)
    require(digest(raw) == document['old_inventory_sha256'] == OLD_SHA, 'PRESERVED_INVALID_OLD_INVENTORY')
    require(set(old) == set(files) and old['inventory.json'] == digest(b''), 'EXPLICIT_OLD_INVALID_SELF_ENTRY')
    require(all(old[n] == files[n] for n in files if n != 'inventory.json'), 'ORIGINAL_72_PAYLOADS')
    require(old['inventory.json'] != files['inventory.json'], 'NEVER_RETROSPECTIVE_OLD_73_PASS')
    return {'failed_attempt_archive_integrity': 'PASS', 'actual_files': 73,
            'old_inventory_claim': 'INVALID_SELF_ENTRY_PRESERVED', 'original_other_payloads': 72,
            'no_neural_arrays_keys_fits_or_releases': True}


class ArchiveIntegrityTests(unittest.TestCase):
    def setUp(self):
        self.document = json.loads(MANIFEST.read_text())

    def test_actual_nonrecursive_manifest(self):
        self.assertEqual(verify(self.document)['actual_files'], 73)

    def test_missing_entry_denied(self):
        document = copy.deepcopy(self.document)
        del document['files'][next(n for n in document['files'] if n != 'inventory.json')]
        with self.assertRaisesRegex(RuntimeError, 'COMPLETE_EXACT_ROSTER'):
            verify(document)

    def test_corrupted_hash_denied(self):
        document = copy.deepcopy(self.document)
        document['files'][next(n for n in document['files'] if n != 'inventory.json')] = '0' * 64
        with self.assertRaisesRegex(RuntimeError, 'ACTUAL_FILE_HASH'):
            verify(document)

    def test_self_reference_traversal_denied(self):
        document = copy.deepcopy(self.document)
        document['files']['../' + MANIFEST.name] = digest(MANIFEST.read_bytes())
        with self.assertRaisesRegex(RuntimeError, 'NO_SELF_REFERENCE_OR_TRAVERSAL'):
            verify(document)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--self-test', action='store_true')
    args = parser.parse_args()
    if args.self_test:
        result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(ArchiveIntegrityTests))
        require(result.wasSuccessful() and result.testsRun == 4 and not result.skipped, 'FOUR_ARCHIVAL_REGRESSIONS')
    value = verify(json.loads(MANIFEST.read_text()))
    value['regressions'] = 4 if args.self_test else 0
    print(json.dumps(value, sort_keys=True))


if __name__ == '__main__':
    main()
