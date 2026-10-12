import unittest
import register as r
import transport1


class SavedSecurityTests(unittest.TestCase):
    def test_old_evidence_and_locks_immutable(self):
        record=r.verify()
        self.assertEqual(len(record['prior_sha256']),13186)
        old=r.ROOT/'paper12_curated_v1'
        self.assertEqual(r.load(old/'results/M1/gate_result.json')['gate'],'PASS')
        self.assertEqual(r.load(old/'results/M2/gate_result.json')['gate'],'FAIL')
        self.assertEqual(len(r.load(old/'locks/animals.json')),26)

    def test_tool_sandbox_failures_never_reclassified(self):
        for name in ('analysis.json','analysis_retry.json'):
            proof=r.load(r.HERE/'results/isolation'/name)
            self.assertFalse(proof['isolation_probe_pass'])
            self.assertFalse(proof['source_read_denied'])
            self.assertFalse(proof['key_read_denied'])
            self.assertFalse(proof['dacl_regrant_denied'])

    def test_native_runtime_actual_negatives(self):
        proof=r.load(r.HERE/'results/isolation/native_profile_runtime2.json')
        self.assertTrue(proof['mandatory_isolation_pass'])
        self.assertTrue(proof['python_runtime_probe']['child_appcontainer'])
        self.assertEqual(proof['python_runtime_probe']['exit_code'],0)
        data=proof['runtime_canary']
        for field in ('key_read_denied','source_read_denied','dacl_regrant_denied','network_denied','custodian_memory_access_denied'):
            self.assertTrue(data[field])
        self.assertEqual(data['network_status_code'],10013)
        self.assertEqual(proof['profile_cleanup_hresult'],'0x00000000')

    def test_bad_runtime_attempts_preserved(self):
        for name in ('native_profile.json','native_profile_runtime1.json'):
            self.assertFalse(r.load(r.HERE/'results/isolation'/name)['mandatory_isolation_pass'])

    def test_registered_role_code_unchanged(self):
        reg=r.load(r.HERE/'role_registration.json')
        for path,value in reg['sha256'].items():
            self.assertEqual(r.sha(r.HERE/path),value)
        self.assertFalse(reg['source_full_session_decoded_by_custodian'])

    def test_transport_overlay_storage_only(self):
        function=transport1.session_callable()
        self.assertIn('.private/real_transport1',function.__code__.co_consts)
        self.assertNotIn('.private/real',function.__code__.co_consts)
        record=r.load(r.HERE/'transport_registration1.json')
        for path,value in record['sha256'].items():
            self.assertEqual(r.sha(r.HERE/path),value)
        self.assertEqual(r.load(r.HERE/'results/M2/failures/766640955.json')['error_code'],'SOURCE_RESPONSE_LENGTH_INVALID')


if __name__=='__main__':unittest.main()
