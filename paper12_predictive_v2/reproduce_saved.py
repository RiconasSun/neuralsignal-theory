"""One-command saved-evidence reproduction; zero fits/count reads/final access."""
import json
import unittest
import study as r
def main():
    seal=r.load(r.HERE/'final_manifest.json')
    for n,d in seal['sha256'].items():
        if r.sha(r.ROOT/n)!=d:raise RuntimeError('SEALED_FILE_CHANGED:'+n)
    preserved=r.load(r.HERE/'preservation_manifest.json')['tracked_working_bytes_sha256']
    prefix=r.load(r.HERE/'closeout_registration.json')['daily_original_sha256']
    for n,d in preserved.items():
        if n=='ops/daily-operations.md':
            raw=(r.ROOT/n).read_bytes();suffix=(r.HERE/'historical_daily_operations.bin').read_bytes()
            if not raw.endswith(suffix) or r.sha(r.HERE/'historical_daily_operations.bin')!=prefix or d!=prefix:raise RuntimeError('HISTORICAL_STATUS_BYTES')
        elif r.sha(r.ROOT/n)!=d:raise RuntimeError('HISTORICAL_EVIDENCE_CHANGED:'+n)
    suite=unittest.defaultTestLoader.discover(str(r.HERE),pattern='test_*.py');result=unittest.TestResult();suite.run(result)
    if not result.wasSuccessful() or result.skipped or result.testsRun!=43:raise RuntimeError(str({'tests':result.testsRun,'errors':result.errors,'failures':result.failures,'skipped':result.skipped}))
    from analyze_saved import build
    if build()!=r.load(r.HERE/'results/exploratory_statistics.json'):raise RuntimeError('STATISTICAL_REPRODUCTION_CHANGED')
    print(json.dumps({'mission':r.MISSION,'saved_reproduction':'PASS','tests':result.testsRun,'sealed_files':len(seal['sha256']),'preserved_files':len(preserved),'new_fits':0,'final_access':False,'paper_status':'Exploratory draft; final validation not authorized'}))
if __name__=='__main__':main()
