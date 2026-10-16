"""Saved audit and synthetic regression only; never resumes real C or D."""
import json
import socket
import unittest
from unittest.mock import patch
from .common import P,ROOT,identities
from . import final_C,final_D
from .audit_saved import audit_C,audit_D
from paper13_ki_execution1 import baseline_A as b


def main():
    identities()
    if (P/'CLOSEOUT_FREEZE.json').is_file():
        for name,digest in b.read(P/'CLOSEOUT_FREEZE.json')['hashes'].items():
            if b.sha((ROOT/name).read_bytes())!=digest:raise RuntimeError('Saved closeout hash mismatch: '+name)
    old=['test_models','test_fit_engine','test_families','test_animal_stats','test_predictive','test_sensitivity_plan','test_sensitivity_scores','test_calibration_state']
    new=['test_final_C','test_final_D','test_final_D_prior','test_final_D_integration','test_seal_final_C','test_route','test_source_journal','test_reporting','test_failure_retention.FailureRetentionTests']
    names=['paper13_ki_execution1.'+n for n in old]+['paper13_descriptive_final1.'+n for n in new]
    suite=unittest.defaultTestLoader.loadTestsFromNames(names)
    with patch.object(socket.socket,'connect',side_effect=AssertionError('Saved reproduction denies network')):
        result=unittest.TextTestRunner(verbosity=2).run(suite)
        if not result.wasSuccessful():raise RuntimeError('Saved/synthetic regression failed')
        # The real execution entrypoints are never called, even when markers exist.
        with patch.object(final_C,'run',side_effect=AssertionError('No real C fitting')),patch.object(final_D,'run',side_effect=AssertionError('No D assessment')):
            c=audit_C()
            d=audit_D() if (P/'results/FINAL_D_RESULTS.json').is_file() else {'FINAL_D_ASSESSMENT_EXECUTED':False,'FINAL_MICE_EVALUATED':0,'status':'NOT_COMPLETE; inspect original gates/partial failure evidence'}
    identities()
    print(json.dumps({'unique_synthetic_tests':result.testsRun,'C_saved_audit':{k:v for k,v in c.items() if k!='C_request_sha256s'},'D_saved_audit':d,
        'original_M6':'FAIL_RETAINED','conditional_Bstar':'FAILED_UNAVAILABLE','broad_confirmatory_claims':'INCONCLUSIVE',
        'new_real_fits':0,'new_D_scores':0,'new_real_control_draws':0,'reproduction_scope':'SAVED_RESULTS_AND_SYNTHETIC_ONLY'},sort_keys=True))


if __name__=='__main__':main()
