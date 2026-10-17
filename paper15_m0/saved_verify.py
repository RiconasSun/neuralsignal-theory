"""Offline reproduction: original metadata and tiny saved pilot fixtures only."""
import hashlib,json,socket,tempfile,unittest
from pathlib import Path
import numpy as np
from .coverage import P,R,build,dump
from .numerics import count_bins

def verify():
    def denied(*a,**k):raise RuntimeError('Saved-only reproduction denies network')
    socket.create_connection=denied;socket.socket.connect=denied
    out=P/'work/saved_reproduction';out.mkdir(parents=True,exist_ok=True)
    summary=build(out)
    reproduced=[]
    for name in ['COVERAGE.csv','TRIAL_COVERAGE.csv','REGION_TIERS.csv','ALLOCATION.csv','COVERAGE_SUMMARY.json']:
        assert (out/name).read_bytes()==(P/'results'/name).read_bytes(),name
        reproduced.append(name)
    results=json.loads((P/'results/PILOT_RESULTS.json').read_text(encoding='utf8'))
    assert len(results)==2 and all(x['pass_'] and not x['final_neural_access'] and x['predictive_fits']==0 for x in results)
    for res in results:
        demo=json.loads((P/'results'/(res['subject']+'_COUNT_DEMO.json')).read_text(encoding='utf8'))
        zeros=0
        for e,f in zip(demo['examples'],demo['fragments'],strict=True):
            assert e['trial']==f['trial']
            c,v=count_bins(np.asarray(f['times']),np.asarray(f['labels']),demo['units'],np.asarray(e['edges']),demo['bad_intervals'])
            np.testing.assert_array_equal(c,e['counts']);np.testing.assert_array_equal(v,e['valid']);zeros+=int((c==0).sum())
        assert zeros==res['demo_zero_unit_bins']
        reproduced.append(res['subject']+'_COUNT_DEMO.json')
    receipts=json.loads((P/'results/FILE_RECEIPTS.json').read_text(encoding='utf8'))
    assert len(receipts)==24 and all(x['status']=='COMPLETE' for x in receipts)
    assert sum(x['reserved_bytes'] for x in receipts)==762373609
    # Saved SHA receipts certify past real access; this command deliberately never reads large neural cache.
    from . import test_m0
    run=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromModule(test_m0))
    assert run.wasSuccessful()
    receipt=dict(saved_only=True,network_denied=True,large_neural_cache_read=False,predictive_fits=0,final_neural_access=False,
        reproduced=reproduced,tests=run.testsRun,failed=len(run.failures)+len(run.errors),candidate_mice=summary['candidate_independent_mice'])
    dump(out/'SAVED_REPRODUCTION_RECEIPT.json',receipt);print(json.dumps(receipt,indent=2))
if __name__=='__main__':verify()
