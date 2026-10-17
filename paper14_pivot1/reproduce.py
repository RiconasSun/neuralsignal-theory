"""Saved-only source/metadata decision reproduction, no new experiment."""
import json,socket,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import requests
from .retrieve import P,read,sha
from .audit import verify,run
def denied(*args,**kwargs):raise PermissionError('Saved-only NETWORK DENIED')
def main():
    counts={}
    for name in ['SOURCE_FREEZE.json','CLOSEOUT_FREEZE.json']:
        hashes=read(P/name)['hashes']
        for path,h in hashes.items():
            if sha((P/path).read_bytes())!=h:raise ValueError('Frozen source/payload changed: '+path)
        counts[name]=len(hashes)
    history=verify()
    with patch.object(socket.socket,'connect',denied),patch.object(socket,'create_connection',denied),patch.object(requests.sessions.Session,'request',denied):
        test=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromName('paper14_pivot1.test_pivot'))
        if not test.wasSuccessful():raise RuntimeError('Required metadata regressions failed')
        work=P/'work';work.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=work) as temp:
            out=Path(temp);decision=run(out);files=sorted(f.name for f in out.iterdir())
            if files!=sorted(f.name for f in (P/'results').iterdir()):raise ValueError('Result file manifest changed')
            for f in files:
                if (out/f).read_bytes()!=(P/'results'/f).read_bytes():raise ValueError('Byte-exact result mismatch: '+f)
    result=dict(saved_metadata_audit='PASS',scientific_decision=decision['scientific_decision'],decision_scope=decision['decision_scope'],full_M1_ready=False,tests=test.testsRun,byte_exact_results=len(files),manifest_counts=counts,historical_hashes=history,network='DENIED',new_neural_values_or_model_fits=0,final_access=0)
    print(json.dumps(result,indent=2));return result
if __name__=='__main__':main()
