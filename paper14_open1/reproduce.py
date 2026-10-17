"""Offline saved-metadata audit, never a new release query or experiment."""
import contextlib
import io
import json
import socket
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import requests
from .retrieve import P,read,sha
from .audit import run,verify_history

def denied(*args,**kwargs):raise PermissionError('Saved-only reproduction: NETWORK DENIED')

def main():
    counts={}
    for manifest in ['SOURCE_FREEZE.json','CLOSEOUT_FREEZE.json']:
        hashes=read(P/manifest)['hashes']
        for name,h in hashes.items():
            if sha((P/name).read_bytes())!=h:raise ValueError('Frozen source/payload changed: '+name)
        counts[manifest]=len(hashes)
    history=verify_history()
    with patch.object(socket.socket,'connect',denied),patch.object(socket,'create_connection',denied),patch.object(requests.sessions.Session,'request',denied):
        suite=unittest.defaultTestLoader.loadTestsFromName('paper14_open1.test_recovery')
        result=unittest.TextTestRunner(verbosity=2).run(suite)
        if not result.wasSuccessful():raise RuntimeError('Required source/policy regressions failed')
        work=P/'work';work.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=work) as temp:
            out=Path(temp);decision=run(out);generated=sorted(p.name for p in out.iterdir())
            expected=sorted(p.name for p in (P/'results').iterdir() if p.is_file())
            if generated!=expected:raise ValueError('Result-file manifest changed')
            for name in generated:
                if (out/name).read_bytes()!=(P/'results'/name).read_bytes():raise ValueError('Saved-result mismatch: '+name)
    report=dict(saved_metadata_audit='PASS',scientific_decision=decision['scientific_decision'],full_M1_ready=False,tests=result.testsRun,byte_exact_results=len(generated),historical_hashes=history,manifest_counts=counts,network='DENIED',new_real_fits_or_neural_values=0,final_access=0)
    print(json.dumps(report,indent=2));return report

if __name__=='__main__':main()
