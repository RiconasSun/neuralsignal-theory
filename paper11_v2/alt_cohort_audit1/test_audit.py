import unittest
from audit import classify_file, permitted, verdict


class SafetyGateTests(unittest.TestCase):
    def test_public_osf_api(self):
        self.assertTrue(permitted('https://api.osf.io/v2/nodes/vh5kq/files/', 'api'))

    def test_public_figshare_api(self):
        self.assertTrue(permitted('https://api.figshare.com/v2/articles/14905317', 'api'))

    def test_no_download_host(self):
        self.assertFalse(permitted('https://files.osf.io/data.mat', 'api'))

    def test_no_document_download(self):
        self.assertFalse(permitted('https://figshare.com/ndownloader/files/1', 'document'))

    def test_no_http(self):
        self.assertFalse(permitted('http://api.osf.io/v2/nodes/vh5kq/', 'api'))

    def test_no_credentials(self):
        self.assertFalse(permitted('https://token@api.osf.io/v2/nodes/vh5kq/', 'api'))

    def test_no_false_host(self):
        self.assertFalse(permitted('https://api.osf.io.evil/v2/nodes/vh5kq/', 'api'))

    def test_no_values_endpoint(self):
        self.assertFalse(permitted('https://osf.io/vh5kq/download', 'document'))

    def test_archive_closed(self):
        self.assertEqual(classify_file('RawData.zip'), 'MIXED_ARCHIVE_NOT_OPENED')

    def test_raw_signal_closed(self):
        self.assertEqual(classify_file('channel.ncs'), 'BINARY_DATA_NOT_OPENED')

    def test_mat_closed(self):
        self.assertEqual(classify_file('ImageNet_Spikes.mat'), 'BINARY_DATA_NOT_OPENED')

    def test_spike_text_closed(self):
        self.assertEqual(classify_file('TimeStamps_1.txt'), 'POTENTIALLY_PROTECTED_VALUES_NOT_OPENED')

    def test_readme_not_automatically_opened(self):
        self.assertEqual(classify_file('readme.rtf'), 'DOCUMENT_CANDIDATE_REQUIRES_ACCESS_PLAN')

    def test_published_total_not_eligibility(self):
        self.assertEqual(verdict({'published_patients': 16}), 'INCONCLUSIVE')

    def test_missing_support_not_fail(self):
        self.assertEqual(verdict({'documented_eligible_patients': 0}), 'INCONCLUSIVE')

    def test_positive_incompatibility_fail(self):
        self.assertEqual(verdict({'authoritative_incompatibility': True}), 'FAIL')

    def test_all_mandatory_for_pass(self):
        qc = {k: True for k in ['complete_inventory', 'pinned_version', 'license_established',
              'canonical_patient_mapping', 'independence_supported', 'native_recording_support',
              'gaps_verified', 'clock_mapping_verified']}
        qc['documented_eligible_patients'] = 8
        self.assertEqual(verdict(qc), 'PASS')
        for key in list(qc):
            if key != 'documented_eligible_patients':
                changed = dict(qc, **{key: False})
                self.assertEqual(verdict(changed), 'INCONCLUSIVE')

    def test_complete_low_cohort_fail(self):
        qc = {k: True for k in ['complete_inventory', 'pinned_version', 'license_established',
              'canonical_patient_mapping', 'independence_supported', 'native_recording_support',
              'gaps_verified', 'clock_mapping_verified', 'cohort_eligibility_complete']}
        qc['documented_eligible_patients'] = 7
        self.assertEqual(verdict(qc), 'FAIL')


if __name__ == '__main__':
    unittest.main(verbosity=2)
