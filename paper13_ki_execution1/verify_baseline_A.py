"""Saved identities plus network-blocked synthetic baseline-runner reproduction."""
import importlib.metadata
import json
import socket
import unittest
from unittest.mock import patch
from .source import P,ROOT,sha


def main():
    current=json.loads((P/'M3_A_IMPLEMENTATION_FREEZE.json').read_text(encoding='utf8'))
    original=json.loads((ROOT/'paper13_ki_pl_contract1/FREEZE_r2.json').read_text(encoding='utf8'))
    for snap in [current,original]:
        for path,digest in snap['hashes'].items():
            if sha((ROOT/path).read_bytes())!=digest:raise ValueError('Frozen identity mismatch: '+path)
    if importlib.metadata.version('autograd')!='1.8.0':raise ValueError('Pinned independent AD required')
    names=['test_preaccess','test_models','test_fit_engine','test_qc_journal','test_baseline_A']
    with patch.object(socket.socket,'connect',side_effect=AssertionError('Saved/synthetic reproduction forbids network')):
        result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromNames(['paper13_ki_execution1.'+x for x in names]))
    if not result.wasSuccessful():raise RuntimeError('Required regression failed')
    print(json.dumps({'current_hashes':len(current['hashes']),'original_hashes':len(original['hashes']),
        'synthetic_tests':result.testsRun,'neural_acquisition_during_reproduction':False,
        'real_fitting_during_reproduction':False,'B_E_D_evaluation_during_reproduction':False,
        'scope':'M3 A-only implementation and saved identity; actual scientific status is in separately executed gate receipts'}))


if __name__=='__main__':main()
