"""Saved-only source/metadata verification and network-blocked synthetic tests."""
import hashlib
import importlib.metadata
import json
from pathlib import Path
import socket
import unittest
from unittest.mock import patch
from .source import P,ROOT

def check(hashes):
    for name,h in hashes.items():
        path=ROOT/name
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest()!=h:raise ValueError('Frozen file mismatch: '+name)

def main():
    own=json.loads((P/'ENGINEERING_FREEZE_r3.json').read_text());check(own['hashes'])
    old=json.loads((ROOT/'paper13_ki_pl_contract1/FREEZE_r2.json').read_text());check(old['hashes'])
    if importlib.metadata.version('autograd')!='1.8.0':raise ValueError('Pinned independent ADlibrary required')
    names=['paper13_ki_execution1.test_preaccess','paper13_ki_execution1.test_models','paper13_ki_execution1.test_fit_engine']
    with patch.object(socket.socket,'connect',side_effect=AssertionError('Saved-only checkpoint reproduction forbids network')):
        suite=unittest.defaultTestLoader.loadTestsFromNames(names)
        result=unittest.TextTestRunner(verbosity=2).run(suite)
    if not result.wasSuccessful():raise RuntimeError('Synthetic checkpoint regression failed')
    summary={'own_hashes':len(own['hashes']),'unchanged_original_hashes':len(old['hashes']),'synthetic_tests':result.testsRun,'real_neural_source_access':False,'real_QC':False,'real_model_fits':False,'D_assessment':False,'scope':'engineering/M1checkpoint only; not real M2-M7validation'}
    print(json.dumps(summary));return summary

if __name__=='__main__':main()
