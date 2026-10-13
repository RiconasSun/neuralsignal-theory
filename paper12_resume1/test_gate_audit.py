import ast
import unittest
import tempfile
from unittest.mock import patch
from pathlib import Path
import study as r


class AuditTests(unittest.TestCase):
    def test_missing_completed_cache_rejected(self):
        import finalize_m2 as audit
        root=r.HERE/'replay';root.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=root) as path:
            base=Path(path);r.save(base/'results/M2/sessions/fixture.json',{})
            with patch.object(r,'HERE',base):
                with self.assertRaisesRegex(RuntimeError,'COMPLETED_SESSION_CACHE_MISSING'):
                    audit.audit_transport({'sources':{'fixture':{'file_id':'fixture','etag':'e','bytes':9}},'reuse':{}})

    def test_empty_completed_cache_rejected(self):
        import finalize_m2 as audit
        root=r.HERE/'replay';root.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=root) as path:
            base=Path(path);r.save(base/'results/M2/sessions/fixture.json',{});(base/'.private/cache/fixture').mkdir(parents=True)
            with patch.object(r,'HERE',base):
                with self.assertRaisesRegex(RuntimeError,'COMPLETED_SESSION_NO_VERIFIED_BLOCKS'):
                    audit.audit_transport({'sources':{'fixture':{'file_id':'fixture','etag':'e','bytes':9}},'reuse':{}})

    def test_complete_cache_required(self):
        source=(r.HERE/'finalize_m2.py').read_text()
        self.assertIn('COMPLETED_SESSION_CACHE_MISSING',source)
        self.assertIn('SOURCE_AUDIT_COMPLETION_DENOMINATOR_MISMATCH',source)
        self.assertIn('CHECKPOINT_DESCRIPTOR_DENOMINATOR_MISMATCH',source)
        self.assertIn('COMPLETION_WITH_TRANSPORT_STOP',source)

    def test_no_intermediate_authoritative_publication(self):
        source=(r.HERE/'finalize_m2.py').read_text()
        self.assertIn("path=r.HERE/'replay/M2_gate_candidate.json'",source)
        self.assertLess(source.index("if gate['gate']=='PASS' and len(verified)!=26"),source.rindex("r.save(r.HERE/'results/M2/gate_result.json',gate)"))

    def test_m4_numerical_evidence_bound(self):
        source=(r.HERE/'launch_m4.py').read_text()
        self.assertIn("numerical['registered_sources_sha256']",source)
        self.assertIn("numerical['log_sha256']",source)
        self.assertIn("numerical['exit_code']",source)

    def test_matched_baseline_inputs_bound(self):
        source=(r.HERE/'model_worker.py').read_text()
        self.assertIn('M3_M4_MATCHED_INPUT_BINDING_FAILED',source)
        self.assertIn("baseline['training_unit_bins']!=y.size",source)
        self.assertIn("baseline['validation_unit_bins']!=valid.size",source)
        self.assertIn("baseline['data_sha256']!=session['sha256']",source)


if __name__=='__main__':unittest.main()
