import unittest
import study as r
def main():
    result=unittest.TestResult();unittest.defaultTestLoader.discover(str(r.HERE),pattern='test_*.py').run(result)
    record={'count':result.testsRun,'passed':result.wasSuccessful(),'skipped':len(result.skipped),'failures':str(result.failures),'errors':str(result.errors),'final_access':False,'real_fits':0}
    r.save(r.HERE/'results'/('final_test_results.json' if (r.HERE/'results/test_results.json').exists() else 'test_results.json'),record);print(record)
    if not result.wasSuccessful() or result.skipped or result.testsRun!=43:raise RuntimeError('TEST_GATE')
if __name__=='__main__':main()
