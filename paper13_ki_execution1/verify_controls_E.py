"""Saved evidence plus synthetic control-stage tests; never real null experiments."""
import json
import socket
import unittest
from unittest.mock import patch
from .source import P,ROOT,sha
from . import baseline_A as b
from . import verify_saved_progress


def main():
    snap=b.read(P/'M6_E_IMPLEMENTATION_FREEZE.json')
    for name,digest in snap['hashes'].items():
        if sha((ROOT/name).read_bytes())!=digest:raise ValueError('M6 E freeze mismatch: '+name)
    verify_saved_progress.main()
    with patch.object(socket.socket,'connect',side_effect=AssertionError('No network in synthetic E control reproduction')):
        tests=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromName('paper13_ki_execution1.test_controls_E'))
    if not tests.wasSuccessful():raise RuntimeError('E control stage regression failed')
    print(json.dumps({'M6_control_stage_tests':tests.testsRun,'total_current_synthetic_tests':108+tests.testsRun,
        'frozen_hashes':len(snap['hashes']),'real_control_replicates':0,'new_real_fits':0,'final_D_values':False}))


if __name__=='__main__':main()
