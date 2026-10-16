"""Offline, saved-metadata-only reproduction; does not refresh any evidence."""
import importlib.metadata
import json
import socket
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from .audit import P, read, sha, verify_inputs, workdir


def denied(*args,**kwargs):raise PermissionError('Saved-only reproduction forbids network')


def run():
    workdir()
    verify_inputs()
    for name,digest in read(P/'CLOSEOUT_FREEZE.json')['hashes'].items():
        if sha(P/name)!=digest:raise ValueError('Frozen M0 artifact changed: '+name)
    for name,digest in read(P/'METADATA_FREEZE.json')['hashes'].items():
        if sha(P/name)!=digest:raise ValueError('Metadata changed: '+name)
    import requests
    with patch.object(socket.socket,'connect',denied),patch.object(socket,'create_connection',denied),patch.object(requests,'request',denied):
        suite=unittest.defaultTestLoader.loadTestsFromName('paper14_m0.test_metadata')
        result=unittest.TextTestRunner(verbosity=2).run(suite)
        if not result.wasSuccessful():raise RuntimeError('Regression failure')
        from . import audit,context_audit,summarize
        with tempfile.TemporaryDirectory(dir=P/'work',prefix='saved_repro_') as directory:
            out=Path(directory);audit.run(out);context_audit.run(out);summarize.run(out)
            expected={p.name:sha(p) for p in (P/'results').iterdir() if p.is_file()}
            actual={p.name:sha(p) for p in out.iterdir() if p.is_file()}
            if actual!=expected:raise ValueError('Saved table mismatch: '+str([k for k in actual.keys()|expected.keys() if actual.get(k)!=expected.get(k)]))
    verify_inputs()
    print(json.dumps({'saved_only':'PASS','tests':result.testsRun,'exact_result_files':len(expected),'original_inputs':len(read(P/'INPUT_FREEZE.json')['hashes']),
        'M0_payload_hashes':len(read(P/'CLOSEOUT_FREEZE.json')['hashes']),'python':sys.version.split()[0],
        'pandas':importlib.metadata.version('pandas'),'numpy':importlib.metadata.version('numpy'),'requests':importlib.metadata.version('requests'),
        'network':'DENIED','neural_arrays_fits_scores':0,'scientific_verdict':read(P/'results/M0_DECISION.json')['scientific_feasibility_verdict'],'M1_activated':False},sort_keys=True))


if __name__=='__main__':run()
