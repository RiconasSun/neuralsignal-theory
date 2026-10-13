"""Run unchanged synthetic checks with passive assertion-value recording."""
import importlib.util
import sys
import time
import traceback
import unittest
from pathlib import Path
import study as r
from register import IDENTITIES,candidate


def main():
    registration=r.verify();source=r.HERE/'patched/m4_numerical_tests.py'
    syntax=r.load(r.HERE/'results/syntax_receipt.json')
    if not syntax['py_compile_pass'] or r.sha(source)!=registration['candidate_sha256']:
        raise RuntimeError('REGISTERED_COMPILED_SYNTAX_REPAIR_REQUIRED')
    if source.read_bytes()!=candidate((r.HERE/'original/m4_numerical_tests.py.txt').read_bytes()):
        raise RuntimeError('ONLY_REGISTERED_ONE_CHARACTER_REPAIR_PERMITTED')
    policy=r.load(r.M3/'M4_registration.json')
    for name,digest in policy['source_sha256'].items():
        if r.sha(r.ROOT/name)!=digest:raise RuntimeError('MATHEMATICAL_OR_POLICY_SOURCE_CHANGED:'+name)
    sys.path.insert(0,str(r.PREVIOUS))
    spec=importlib.util.spec_from_file_location('repaired_frozen_m4_tests',source)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    cls=module.NumericalTests;observations=[]
    original_less=cls.assertLess;original_almost=cls.assertAlmostEqual
    def less(self,first,second,msg=None):
        observations.append(dict(test=self._testMethodName,assertion='assertLess',actual=float(first),tolerance=float(second)))
        return original_less(self,first,second,msg)
    def almost(self,first,second,places=None,msg=None,delta=None):
        observations.append(dict(test=self._testMethodName,assertion='assertAlmostEqual',absolute_error=float(abs(first-second)),places=places,delta=delta))
        return original_almost(self,first,second,places,msg,delta)
    cls.assertLess=less;cls.assertAlmostEqual=almost
    class Result(unittest.TextTestResult):
        def startTest(self,test):
            started.append(test._testMethodName);super().startTest(test)
        def addSuccess(self,test):
            successes.append(test._testMethodName);super().addSuccess(test)
    started=[];successes=[];suite=unittest.defaultTestLoader.loadTestsFromTestCase(cls)
    frozen=unittest.defaultTestLoader.getTestCaseNames(cls)
    if set(frozen)!=set(IDENTITIES) or suite.countTestCases()!=5:raise RuntimeError('FROZEN_FIVE_IDENTITIES_CHANGED')
    start=time.perf_counter();log=r.HERE/'results/numerical_tests.log';log.parent.mkdir(parents=True,exist_ok=True)
    with log.open('x',encoding='utf-8') as stream:
        result=unittest.TextTestRunner(stream=stream,verbosity=2,resultclass=Result).run(suite)
    expected_counts=dict(test_poisson_analytic=1,test_exhaustive_states=6,test_all_gradients_and_ridge_exposure=18,
        test_causal_future_and_batch_reset=27,test_archived_batch_sequential_parity=18)
    counts={name:sum(x['test']==name for x in observations) for name in IDENTITIES}
    passed=(result.wasSuccessful() and result.testsRun==5 and not result.skipped and set(started)==set(IDENTITIES)
            and set(successes)==set(IDENTITIES) and counts==expected_counts)
    r.save(r.HERE/'results/numerical_gate.json',dict(gate='PASS' if passed else 'FAIL',
        scientific_verdict='NUMERICAL_HARNESS_VERIFIED' if passed else 'M4_NUMERICAL_INCONCLUSIVE',
        tests_run=result.testsRun,started_identities=started,passed_identities=successes,skipped=result.skipped,
        errors=[dict(test=str(t),traceback=e) for t,e in result.errors],failures=[dict(test=str(t),traceback=e) for t,e in result.failures],
        assertion_counts=counts,expected_assertion_counts=expected_counts,assertions=observations,
        original_sha256=registration['original_test_sha256'],repaired_sha256=r.sha(source),
        registration_sha256=r.sha(r.HERE/'registration.json'),syntax_receipt_sha256=r.sha(r.HERE/'results/syntax_receipt.json'),
        log_sha256=r.sha(log),model_source_sha256=policy['source_sha256'],
        elapsed_seconds=time.perf_counter()-start,synthetic_only=True,neural_access=False,final_access=False,
        original_strict_inequalities_preserved=True,exit_code=0 if passed else 1),True)
    print('FIVE_FROZEN_NUMERICAL_CATEGORIES',passed,counts)
    if not passed:raise SystemExit(1)


if __name__=='__main__':main()
