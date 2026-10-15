"""Native principal integration; no real entitlement or protected neural input."""
import concurrent.futures
import json
from pathlib import Path
import subprocess
import sys
import unittest
from release_control import Controller,canonical,read_json,validate_state_manifest,safe,validate_real_bindings
from cryptography.exceptions import InvalidSignature
DATA=None;OUT=None;ARGS=None;WORKER=None

class ControllerTests(unittest.TestCase):
    def controller(self,name):return Controller(DATA/name/'ledger',DATA/name/'anchor.json',DATA/'binding')
    def consume(self,name,approval=None):return self.controller(name).consume(approval or DATA/name/'approval.json')
    def altered(self,name,mutate):
        value=read_json(DATA/name/'approval.json');mutate(value)
        p=OUT/(self._testMethodName+'_'+name+'_altered.json');p.write_bytes(canonical(value));return p
    def test_duplicate(self):
        self.consume('duplicate')
        with self.assertRaises(PermissionError):self.consume('duplicate')
    def test_concurrent(self):
        def attempt(_):
            try:self.consume('concurrent');return True
            except PermissionError:return False
        with concurrent.futures.ThreadPoolExecutor(2) as pool:values=list(pool.map(attempt,range(2)))
        self.assertEqual(sum(values),1)
    def test_replay_different_ledger(self):
        with self.assertRaises(PermissionError):self.consume('replay',DATA/'duplicate/approval.json')
    def test_missing_signature(self):
        p=self.altered('missing_signature',lambda v:v.pop('signature'))
        with self.assertRaises(PermissionError):self.consume('missing_signature',p)
    def test_missing_independent_review(self):
        with self.assertRaises(PermissionError):self.consume('missing_review')
    def test_anchor_readonly(self):
        with self.assertRaises(PermissionError):
            with (DATA/'success/anchor.json').open('ab') as f:f.write(b'FORGE_AUTHORITY')
    def test_wrong_signature(self):
        p=self.altered('wrong_signature',lambda v:v.update(signature='00'*64))
        with self.assertRaises(InvalidSignature):self.consume('wrong_signature',p)
    def test_changed_code_artifact(self):
        with self.assertRaises(PermissionError):self.consume('changed_artifact')
    def test_wrong_principal(self):
        with self.assertRaises(PermissionError):self.consume('wrong_principal')
    def test_real_synthetic_cross_realm(self):
        with self.assertRaises(PermissionError):self.consume('wrong_realm')
    def test_real_mode_cannot_use_engineering_evidence(self):
        body=read_json(DATA/'success/approval.json')['body']
        with self.assertRaises(PermissionError):validate_real_bindings(body,DATA/'binding')
    def test_C_state_realm_cannot_be_relabeled(self):
        from release_control import check_C_realm
        manifest=read_json(DATA/'binding/C_state_manifest.json')
        with self.assertRaisesRegex(PermissionError,'CALIBRATION_REALM_MISMATCH'):check_C_realm('REAL_D',manifest)
        with self.assertRaisesRegex(PermissionError,'CALIBRATION_REALM_MISMATCH'):check_C_realm('SYNTHETIC_D',dict(manifest,synthetic=False))
    def test_missing_ledger(self):
        with self.assertRaises((PermissionError,FileNotFoundError)):self.consume('missing_ledger')
    def test_tampered_ledger(self):
        with self.assertRaises(PermissionError):self.consume('tampered_ledger')
    def test_partial_ledger(self):
        with self.assertRaises(PermissionError):self.consume('partial_ledger')
    def test_malformed_ledger(self):
        with self.assertRaises(ValueError):self.consume('malformed_ledger')
    def test_missing_consumption_records(self):
        for name in ('missing_tombstone','missing_intent'):
            with self.assertRaises(PermissionError):self.consume(name)
    def test_missing_genesis(self):
        with self.assertRaises((PermissionError,FileNotFoundError)):self.consume('missing_genesis')
    def test_unknown_and_duplicate_json(self):
        p=self.altered('unknown_field',lambda v:v['body'].update(extra=True))
        with self.assertRaises(PermissionError):self.consume('unknown_field',p)
        p=OUT/'duplicate_json.json';p.write_text('{"body":{},"body":{},"signature":"x"}')
        with self.assertRaises(ValueError):self.consume('unknown_field',p)
    def test_incomplete_states(self):
        manifest=read_json(DATA/'binding/C_state_manifest.json');manifest['cases'].pop()
        with self.assertRaises(PermissionError):validate_state_manifest(manifest)
    def test_incomplete_N_seeds(self):
        manifest=read_json(DATA/'binding/C_state_manifest.json');manifest['seed_certificates'].pop(next(iter(manifest['seed_certificates'])))
        with self.assertRaises(PermissionError):validate_state_manifest(manifest)
    def test_exact_unit_certificate_cardinality_and_order(self):
        from release_control import check_numerical_rows
        case=read_json(DATA/'binding/C_state_manifest.json')['cases'][0]
        with self.assertRaisesRegex(PermissionError,'EXACT_UNIT_CERTIFICATES'):check_numerical_rows({'passed':True,'records':[]},case,'O')
        cert=read_json(DATA/'binding'/(case['case']+'_O.json'))
        cert['records']=cert['records'][::-1]
        with self.assertRaisesRegex(PermissionError,'ORIGINAL_UNIT_SOLVER'):check_numerical_rows(cert,case,'O')
    def test_incomplete_provenance_rejected(self):
        from release_control import validate_provenance
        manifest=read_json(DATA/'binding/C_state_manifest.json');manifest['artifact_sha256'].pop('provenance_roster.json')
        with self.assertRaisesRegex(PermissionError,'COMPLETE_PROVENANCE'):validate_provenance(manifest,DATA/'binding')
    def test_nonfinite_json(self):
        p=OUT/'nan.json';p.write_text('{"body":NaN,"signature":"x"}')
        with self.assertRaises(ValueError):self.consume('unknown_field',p)
    def test_crash_points(self):
        for point in ('before_intent','after_intent','after_intent_append','after_consumed_append','after_consumed'):
            name='crash_'+point
            result=subprocess.run([sys.executable,'-I','-S',WORKER,*ARGS,point,name],close_fds=True,timeout=60)
            self.assertEqual(result.returncode,73,point)
            if point=='before_intent':
                # No entitlement consumed; injected pre-consumption failure did not grant a capability.
                self.assertFalse((DATA/name/'ledger/intent.json').exists())
            else:
                with self.assertRaises(PermissionError):self.consume(name)
    def test_independent_fence_survives_log_rollback(self):
        self.consume('fence_rollback')
        # Emulate a truncated log while durable fence remains. The controller may append/truncate
        # ledger bytes but cannot clear the independent protected issuance fence.
        path=DATA/'fence_rollback/ledger/events.jsonl';first=path.read_bytes().splitlines()[0];path.write_bytes(first+b'\n')
        with self.assertRaises(PermissionError):self.consume('fence_rollback')
    def test_fence_without_other_records_still_denies(self):
        self.assertFalse((DATA/'restored_log/ledger/intent.json').exists())
        self.assertFalse((DATA/'restored_log/ledger/consumed.json').exists())
        with self.assertRaises(PermissionError):self.consume('restored_log')
    def test_source_artifacts_readonly(self):
        with self.assertRaises(PermissionError):
            with (DATA/'binding/PROTOCOL.md').open('ab') as f:f.write(b'TAMPER')
    def test_path_traversal_hardlink_reparse_denied(self):
        for p in (DATA/'../escape',DATA/'link_tests/hardlinked.bin',DATA/'link_tests/junction'):
            with self.assertRaises(PermissionError):safe(DATA,p)
if __name__=='__main__':unittest.main()
