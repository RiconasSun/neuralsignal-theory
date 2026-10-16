"""Saved identities and synthetic family integration; no scientific rerun."""
import importlib.metadata
import json
import socket
import unittest
from unittest.mock import patch
from .source import P,ROOT,sha


def main():
    snap=json.loads((P/'M4_IMPLEMENTATION_FREEZE.json').read_text(encoding='utf8'))
    original=json.loads((ROOT/'paper13_ki_pl_contract1/FREEZE_r2.json').read_text(encoding='utf8'))
    for manifest in [snap,original]:
        for name,digest in manifest['hashes'].items():
            if sha((ROOT/name).read_bytes())!=digest:raise ValueError('Frozen artifact mismatch: '+name)
    if importlib.metadata.version('autograd')!='1.8.0':raise ValueError('Pinned independent AD required')
    modules=['test_preaccess','test_models','test_fit_engine','test_qc_journal','test_baseline_A','test_development_B','test_families']
    with patch.object(socket.socket,'connect',side_effect=AssertionError('Saved/synthetic reproduction forbids network')):
        result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromNames(['paper13_ki_execution1.'+name for name in modules]))
    if not result.wasSuccessful():raise RuntimeError('Family implementation regression failed')
    print(json.dumps({'frozen_hashes':len(snap['hashes']),'original_hashes':len(original['hashes']),
        'synthetic_tests':result.testsRun,'new_source_reads':0,'new_real_fits':0,'new_real_scores':0,
        'scope':'Saved identities plus synthetic tests; executed scientific status is in native gate receipts'}))


if __name__=='__main__':main()
