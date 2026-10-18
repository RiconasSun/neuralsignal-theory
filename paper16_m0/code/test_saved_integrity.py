"""Independent data-tamper regressions,only saved bytes/memory;no real source replay."""
import copy,unittest
from unittest.mock import patch
from . import evidence_checks as audit

class SavedIntegrityTests(unittest.TestCase):
    def reject(self,name,alter):
        original=audit.read_json
        def read(path):
            value=original(path)
            if path.name==name:return alter(copy.deepcopy(value))
            return value
        with patch.object(audit,'read_json',side_effect=read):
            with self.assertRaises(AssertionError):audit.check_saved()
    def test_empty_manifest_denied(self):self.reject('SAVED_EVIDENCE_MANIFEST.json',lambda d:{**d,'files':{}})
    def test_missing_mandatory_manifest_entry_denied(self):
        def alter(d):d['files'].pop('paper16_m0/results/FINAL_M0_STATUS.json');return d
        self.reject('SAVED_EVIDENCE_MANIFEST.json',alter)
    def test_inconsistent_99999_false_status_denied(self):
        self.reject('FINAL_M0_STATUS.json',lambda d:{**d,'INDEPENDENT_CANDIDATE_MICE':99999,'REAL_SPIKE_PILOT_PASS':False,'STIMULUS_SPIKE_ALIGNMENT_PASS':False})
    def test_forged_metadata_summary_denied(self):self.reject('METADATA_SUMMARY.json',lambda d:{**d,'selected_mice':99999})
    def test_pilot_order_not_rerolled(self):self.reject('PILOT_METADATA_SELECTION.json',lambda d:list(reversed(d)))
    def test_invented_common_support_denied(self):self.reject('COMMON_GRATING_PARAMETER_SUPPORT.json',lambda d:{**d,'shared_parameter_tuples':[]})

if __name__=='__main__':unittest.main()
