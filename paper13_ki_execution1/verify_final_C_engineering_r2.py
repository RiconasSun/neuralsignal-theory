"""Prospective C/sensitivity synthetic implementation checks, no real fitting."""
import json
import socket
import unittest
import zipfile
from unittest.mock import patch
from .source import P,ROOT,sha
from . import baseline_A as b


def main():
    current=b.read(P/'FINAL_C_ENGINEERING_FREEZE_r2.json');original=b.read(ROOT/'paper13_ki_pl_contract1/FREEZE_r2.json')
    for manifest in [current,original]:
        for name,digest in manifest['hashes'].items():
            if sha((ROOT/name).read_bytes())!=digest:raise ValueError('C engineering identity mismatch: '+name)
    with zipfile.ZipFile(ROOT/'ops/evidence/2026-10-16/p13-ki-pl-science-first-execution/FINAL_C_engineering_r1_failed_package.zip') as archive:
        preserved={name:archive.read(name) for name in archive.namelist()}
    for name,digest in b.read(P/'FINAL_C_ENGINEERING_FREEZE.json')['hashes'].items():
        if sha((ROOT/name).read_bytes())==digest:continue
        if name not in preserved or sha(preserved[name])!=digest:raise ValueError('Original failed C source not preserved: '+name)
    names=['test_preaccess','test_models','test_fit_engine','test_qc_journal','test_baseline_A','test_development_B','test_families',
        'test_animal_stats','test_predictive','test_development_bundle','test_exploratory_E','test_control_core','test_sensitivity_plan',
        'test_restore_saved','test_controls_E','test_final_C','test_sensitivity_scores']
    with patch.object(socket.socket,'connect',side_effect=AssertionError('No network in synthetic C engineering')):
        result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromNames(['paper13_ki_execution1.'+n for n in names]))
    if not result.wasSuccessful():raise RuntimeError('C/sensitivity engineering regression failed')
    print(json.dumps({'synthetic_tests':result.testsRun,'current_hashes':len(current['hashes']),'original_hashes':len(original['hashes']),
        'new_real_C_fits':0,'new_real_control_replicates':0,'final_D_outcomes_accessed':False,
        'scope':'Synthetic C worker and sensitivity assembly only; actual E-control PASS and final C input review still required'}))


if __name__=='__main__':main()
