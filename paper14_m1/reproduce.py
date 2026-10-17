"""Offline saved source/metadata audit, not neural execution or model validation."""
import importlib.metadata
import json
import socket
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import requests
from .retrieve import P,read,digest
from .audit import verify_inputs,run as audit_run


def deny(*a,**kw):raise PermissionError('Saved-only checkpoint reproduction denies network')


def run():
    verify_inputs()
    for name,h in read(P/'CLOSEOUT_FREEZE.json')['hashes'].items():
        if digest((P/name).read_bytes())!=h:raise ValueError('Checkpoint changed: '+name)
    for name,h in read(P/'SOURCE_FREEZE.json')['hashes'].items():
        if digest((P/name).read_bytes())!=h:raise ValueError('Source changed: '+name)
    work=P/'work';work.mkdir(exist_ok=True)
    with patch.object(socket.socket,'connect',deny),patch.object(socket,'create_connection',deny),patch.object(requests,'request',deny):
        suite=unittest.defaultTestLoader.loadTestsFromName('paper14_m1.test_contract');result=unittest.TextTestRunner(verbosity=2).run(suite)
        if not result.wasSuccessful():raise RuntimeError('Contract regression failed')
        with tempfile.TemporaryDirectory(dir=work) as directory:
            out=Path(directory);audit_run(out)
            expected={f.name:digest(f.read_bytes()) for f in (P/'results').iterdir() if f.is_file()}
            observed={f.name:digest(f.read_bytes()) for f in out.iterdir() if f.is_file()}
            if expected!=observed:raise ValueError('Saved metadata result mismatch')
    verify_inputs()
    print(json.dumps({'saved_only_checkpoint':'PASS','full_M1_scientific_protocol_PASS':False,'scientific_decision':'SOURCE_RIGHTS_BLOCKED','tests':result.testsRun,'byte_exact_results':len(expected),'historical_M0_hashes':len(read(P/'INPUT_FREEZE.json')['hashes']),'payload_hashes':len(read(P/'CLOSEOUT_FREEZE.json')['hashes']),'source_hashes':len(read(P/'SOURCE_FREEZE.json')['hashes']),'network':'DENIED','raw_neural_or_behavioral_samples_read':0,'neural_fits_scores_final_assessments':0,'external_messages_sent':0,'python':sys.version.split()[0],'pandas':importlib.metadata.version('pandas'),'numpy':importlib.metadata.version('numpy'),'PyYAML':importlib.metadata.version('PyYAML'),'requests':importlib.metadata.version('requests')},sort_keys=True))


if __name__=='__main__':run()
