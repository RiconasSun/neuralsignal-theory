"""Prospective one-byte repair registration; never accesses neural exports."""
import ast
import re
import subprocess
import study as r

OLD_LINE=b"for family,sizes in (('Discrete',(2,3,4)),('Continuous',(1,2,4)),('Hybrid',(2,3,4)):"
NEW_LINE=OLD_LINE[:-1]+b'):'
IDENTITIES=['test_poisson_analytic','test_exhaustive_states','test_all_gradients_and_ridge_exposure',
            'test_causal_future_and_batch_reset','test_archived_batch_sequential_parity']


def candidate(original):
    if original.count(OLD_LINE)!=1:raise RuntimeError('ONE_DEMONSTRATED_SYNTAX_LOCATION_REQUIRED')
    return original.replace(OLD_LINE,NEW_LINE,1)


def main():
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=r.ROOT).decode().strip()
    if not head.startswith('035a5388'):raise RuntimeError('BASE_MISMATCH')
    source=r.PREVIOUS/'m4_numerical_tests.py';original=source.read_bytes()
    failure=r.M3/'results/M4/numerical_gate.json';log=r.M3/'results/M4/numerical_tests.log'
    if r.load(failure)['gate']!='FAIL' or r.load(failure)['log_sha256']!=r.sha(log):raise RuntimeError('ORIGINAL_FAILURE_BINDING')
    ids=re.findall(r'^    def (test_\w+)\(',original.decode(),flags=re.M)
    if ids!=IDENTITIES:raise RuntimeError('FIVE_FROZEN_IDENTITIES_REQUIRED')
    try:compile(original,str(source),'exec')
    except SyntaxError as exc:
        syntax=dict(type='SyntaxError',line=exc.lineno,offset=exc.offset,message=exc.msg,text=exc.text)
    else:raise RuntimeError('ORIGINAL_SYNTAX_FAILURE_NOT_REPRODUCED')
    if syntax['line']!=30:raise RuntimeError('OTHER_DEFECT_REQUIRES_AUTHORIZATION')
    repaired=candidate(original);ast.parse(repaired)
    files=subprocess.check_output(['git','ls-files','-z'],cwd=r.ROOT).decode().split('\0')
    implementation=[p for p in r.HERE.glob('*.py')]+[r.HERE/'mission.json',r.HERE/'.gitignore',
        r.ROOT/'ops/evidence/2026-10-13/p12-m4-test-harness-repair-1/goldenstandards.md']
    r.save(r.HERE/'registration.json',dict(mission=r.ID,base=head,utc=r.datetime.now(r.timezone.utc).isoformat(),
        original_test_sha256=r.sha(source),original_failure_sha256=r.sha(failure),original_traceback_sha256=r.sha(log),
        syntax_error=syntax,line_context=original.decode().splitlines()[26:33],test_identities=ids,
        original_assertions_and_references='Entire original byte sequence retained; all except one inserted closing parenthesis identical',
        intended_repair='Insert one ASCII closing parenthesis before colon in line30; separate copy only',
        candidate_sha256=r.hashlib.sha256(repaired).hexdigest(),source_requests=0,neural_access=False,
        prior_sha256={n:r.sha(r.ROOT/n) for n in files if n},
        implementation_sha256={p.relative_to(r.ROOT).as_posix():r.sha(p) for p in implementation}),True)
    originals=r.HERE/'original';originals.mkdir(exist_ok=False)
    (originals/'m4_numerical_tests.py.txt').write_bytes(original)
    (originals/'import_traceback.log').write_bytes(log.read_bytes())
    (originals/'numerical_gate.json').write_bytes(failure.read_bytes())
    print('PROSPECTIVE_ONE_CHARACTER_REPAIR_REGISTERED')


if __name__=='__main__':main()
