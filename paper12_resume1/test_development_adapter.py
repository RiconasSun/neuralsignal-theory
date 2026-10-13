import ast
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import study as r
import fingerprints as f
import register_m3 as m


class AdapterTests(unittest.TestCase):
    def test_native_grant_clone_preserves_readonly_default(self):
        from launch_m3 import archived,a
        copied=a.clone(archived.grant,dict(archived.grant.__globals__))
        self.assertIs(copied.__code__,archived.grant.__code__)
        self.assertEqual(copied.__defaults__,(False,))
        self.assertEqual(copied.__defaults__,archived.grant.__defaults__)
        for name in ('launch_m3.py','launch_m4.py'):
            self.assertIn('a.clone(archived.grant,',(r.HERE/name).read_text())

    def test_exact_public_lock_paths_allowed(self):
        from launch_m3 import mapped
        for name in ('animals.json','units.json','trials.json'):
            path=r.ROOT/'paper12_curated_v1/locks'/name
            self.assertEqual(mapped(path),path)

    def test_other_old_paths_still_denied(self):
        from launch_m3 import mapped
        with self.assertRaises(RuntimeError):mapped(r.OLD/'.private/forbidden.key')
        with self.assertRaises(RuntimeError):mapped(r.ROOT/'paper12_curated_v1/unregistered.json')

    def test_both_entrypoints_enforce_registration(self):
        for name in ('development.py','launch_m3.py'):
            tree=ast.parse((r.HERE/name).read_text())
            main=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='main')
            calls=[n.func.id for n in ast.walk(main) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name)]
            self.assertIn('guard_adapter',calls);self.assertIn('check_fingerprints',calls)

    def test_unknown_storage_rejected(self):
        with self.assertRaisesRegex(RuntimeError,'UNKNOWN_ARTIFACT_STUDY'):
            f.check(dict(session_id='fixture',custody_artifact_namespace='sessions/run_fixture',artifact_study='unknown'),{'reuse':{}})

    def test_old_route_must_be_one_of_eight(self):
        with self.assertRaisesRegex(RuntimeError,'UNAUTHORIZED_OLD_RECEIPT_ROUTE'):
            f.check(dict(session_id='fixture',custody_artifact_namespace='real_index2',artifact_study='paper12_custody1'),{'reuse':{}})

    def test_new_route_traversal_rejected(self):
        with self.assertRaisesRegex(RuntimeError,'NEW_NAMESPACE_INVALID'):
            f.check(dict(session_id='fixture',custody_artifact_namespace='sessions/run_../escape',artifact_study='paper12_resume1'),{'reuse':{}})

    def test_binding_checks_include_gate_and_method(self):
        source=(r.HERE/'register_m3.py').read_text()
        self.assertIn('M3_NEW_M2_GATE_BINDING_CHANGED',source)
        self.assertIn('M3_ORIGINAL_POLICY_BINDING_CHANGED',source)
        self.assertIn('M3_ADAPTER_CHANGED',source)

    def test_exports_development_only(self):
        source=(r.HERE/'development.py').read_text()
        self.assertIn("if animal['group']!='development':continue",source)
        tree=ast.parse(source)
        constants={n.value for n in ast.walk(tree) if isinstance(n,ast.Constant) and isinstance(n.value,str)}
        self.assertNotIn('C',constants);self.assertNotIn('D',constants)


if __name__=='__main__':unittest.main()
