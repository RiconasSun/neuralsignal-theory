"""Current repaired sources, archived failed identities and synthetic regressions."""
import json
import socket
import unittest
import zipfile
from unittest.mock import patch
from .source import P,ROOT,sha
from . import baseline_A as b
from . import development_bundle as bundles
from . import restore_saved_states as restore
from . import controls_E

E=ROOT/'ops/evidence/2026-10-16/p13-ki-pl-science-first-execution'


def main():
    current=b.read(P/'M6_E_IMPLEMENTATION_FREEZE_r2.json');original=b.read(ROOT/'paper13_ki_pl_contract1/FREEZE_r2.json')
    for manifest in [current,original]:
        for name,digest in manifest['hashes'].items():
            if sha((ROOT/name).read_bytes())!=digest:raise ValueError('Current/original hash mismatch: '+name)
    archive=E/'M6_E_r1_failed_code_package.zip';historical=0
    with zipfile.ZipFile(archive) as z:
        preserved={name:z.read(name) for name in z.namelist()}
    for path in [P/'SAVED_PROGRESS_FREEZE.json',E/'CHECKPOINT_CANDIDATE_r2.json',P/'M6_E_IMPLEMENTATION_FREEZE.json']:
        for name,digest in b.read(path)['hashes'].items():
            if sha((ROOT/name).read_bytes())==digest:continue
            if name not in preserved or sha(preserved[name])!=digest:raise ValueError('Historical source not preserved exactly: '+name)
            historical+=1
    names=['test_preaccess','test_models','test_fit_engine','test_qc_journal','test_baseline_A','test_development_B',
        'test_families','test_animal_stats','test_predictive','test_development_bundle','test_exploratory_E',
        'test_control_core','test_sensitivity_plan','test_restore_saved','test_controls_E','test_final_C']
    with patch.object(socket.socket,'connect',side_effect=AssertionError('No source/network in repaired saved/synthetic reproduction')):
        restored=restore.restore(ROOT,b.read(E/'SAVED_DERIVED_STATES_MANIFEST.json'))
        result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromNames(['paper13_ki_execution1.'+name for name in names]))
        if not result.wasSuccessful():raise RuntimeError('Repaired control regression failed')
        m2,qcs,baselines,m3,families,m4=bundles.gates();saved,data=controls_E.inputs()
    summary={'synthetic_tests':result.testsRun,'current_hashes':len(current['hashes']),'original_hashes':len(original['hashes']),
        'historical_source_checks_using_exact_archived_bytes':historical,'failed_source_executed':False,
        'original_saved_states':restored['verified_original_saved_states'],'saved_baseline_fits_verified':len(baselines),
        'saved_dynamic_fits_verified':len(families),'frozen_E_model_state_inputs_verified':len(data),
        'real_control_replicates':0,'new_real_C_fits':0,'final_D_values':False,
        'scope':'Current repaired control implementation and synthetic C worker; no actual scientific experiment or final path approval'}
    print(json.dumps(summary));return summary


if __name__=='__main__':main()
