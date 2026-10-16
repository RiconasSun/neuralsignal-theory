"""Frozen identities and synthetic C worker only, never real C optimization."""
import json
import socket
import unittest
from unittest.mock import patch
from .source import P,ROOT,sha
from . import baseline_A as b
from . import verify_controls_E_r2


def main():
    manifest=b.read(P/'FINAL_C_IMPLEMENTATION_FREEZE.json')
    for name,digest in manifest['hashes'].items():
        if sha((ROOT/name).read_bytes())!=digest:raise ValueError('Final C identity mismatch: '+name)
    previous=verify_controls_E_r2.main()
    with patch.object(socket.socket,'connect',side_effect=AssertionError('Synthetic C reproduction denies network')):
        tests=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromName('paper13_ki_execution1.test_final_C'))
    if not tests.wasSuccessful():raise RuntimeError('C-only worker regression failed')
    print(json.dumps({'synthetic_C_tests':tests.testsRun,'total_current_synthetic_tests':112+tests.testsRun,
        'frozen_hashes':len(manifest['hashes']),'new_real_C_fits':0,'new_real_controls':0,'final_D_values':False,
        'prior_reproduction_tests':previous['synthetic_tests']}))


if __name__=='__main__':main()
