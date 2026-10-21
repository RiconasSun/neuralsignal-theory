"""Metadata-only negative tests of append-only closed-state inventory union."""
import contextlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from paper16_development_r4 import reproduce_saved as saved

@contextlib.contextmanager
def fixture():
    short=saved.R/'.r4t';short.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(dir=short) as directory:
        root=Path(directory);p=root/'p';(p/'work').mkdir(parents=True);(p/'results').mkdir()
        def write(path,data):path.write_text(json.dumps(data),encoding='utf8')
        def ref(path):return dict(path=path.relative_to(root).as_posix(),sha256=saved.sha(path),bytes=path.stat().st_size)
        a=p/'work/a.txt';a.write_text('preserved')
        flag=p/'results/EXTERNAL_INTERRUPTION_CLOSEOUT.json';write(flag,{})
        first=p/'PROTECTED_STATE_MANIFEST.json';write(first,dict(files=[ref(a),ref(flag)]))
        b=p/'work/b.txt';b.write_text('append-only review derivative')
        supplement=p/'PROTECTED_STATE_MANIFEST_SUPPLEMENT_1.json'
        write(supplement,dict(original_manifest_sha256=saved.sha(first),files=[ref(b)]))
        with patch.object(saved,'R',root),patch.object(saved,'P',p):yield p,write,ref

class InventoryTests(unittest.TestCase):
    def test_exact_union_accepts_both_immutable_manifests(self):
        with fixture():saved.protected_inventory()
    def test_extra_unlisted_file_rejected(self):
        with fixture() as (p,write,ref):
            (p/'work/extra.txt').write_text('unlisted')
            with self.assertRaises(RuntimeError):saved.protected_inventory()
    def test_duplicate_file_across_manifests_rejected(self):
        with fixture() as (p,write,ref):
            path=p/'PROTECTED_STATE_MANIFEST_SUPPLEMENT_1.json';data=saved.load(path)
            data['files'].append(ref(p/'work/a.txt'));write(path,data)
            with self.assertRaises(RuntimeError):saved.protected_inventory()
    def test_wrong_original_manifest_binding_rejected(self):
        with fixture() as (p,write,ref):
            path=p/'PROTECTED_STATE_MANIFEST_SUPPLEMENT_1.json';data=saved.load(path)
            data['original_manifest_sha256']='0'*64;write(path,data)
            with self.assertRaises(RuntimeError):saved.protected_inventory()
    def test_missing_supplement_rejected(self):
        with fixture() as (p,write,ref):
            (p/'PROTECTED_STATE_MANIFEST_SUPPLEMENT_1.json').unlink()
            with self.assertRaises(FileNotFoundError):saved.protected_inventory()
    def test_missing_or_corrupt_listed_file_rejected(self):
        for target in ['work/a.txt','work/b.txt']:
            for operation in ['missing','corrupt']:
                with fixture() as (p,write,ref),self.subTest(target=target,operation=operation):
                    if operation=='missing':(p/target).unlink()
                    else:(p/target).write_text('altered')
                    with self.assertRaises(RuntimeError):saved.protected_inventory()
    def test_omitted_supplement_file_rejected(self):
        with fixture() as (p,write,ref):
            path=p/'PROTECTED_STATE_MANIFEST_SUPPLEMENT_1.json';data=saved.load(path)
            data['files']=[];write(path,data)
            with self.assertRaises(RuntimeError):saved.protected_inventory()

if __name__=='__main__':unittest.main()
