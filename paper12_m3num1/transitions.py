"""A child PASS is insufficient without completed native isolation and cleanup."""
def validate(gate, receipt, proof, fixtures, expected):
    if gate.get('gate')!='PASS':raise RuntimeError('PRECEDING_GATE_NOT_PASS')
    if receipt.get('exit_code')!=0 or receipt.get('timed_out') is not False:
        raise RuntimeError('NATIVE_PROCESS_NOT_SUCCESSFULLY_COMPLETE')
    if receipt.get('role_proof_pass') is not True or proof.get('pass') is not True:
        raise RuntimeError('NATIVE_ISOLATION_PROOF_MISSING')
    if receipt.get('profile_cleanup_hresult')!='0x00000000':raise RuntimeError('NATIVE_CLEANUP_NOT_VERIFIED')
    if proof.get('is_appcontainer') is not True or proof.get('capability_count')!=0:
        raise RuntimeError('NATIVE_ROLE_INVALID')
    if not fixtures.get('passed') or fixtures.get('count')!=7:raise RuntimeError('INDEPENDENT_ORACLES_INCOMPLETE')
    if expected!=120 and (gate.get('completed_fit_count')!=expected or gate.get('converged_fit_count')!=expected):
        raise RuntimeError('COMPLETE_CONVERGED_ROSTER_REQUIRED')


def completed(r,phase,expected):
    paths=dict(gate=r.HERE/f'results/{phase}/gate_result.json',receipt=r.HERE/f'results/{phase}_launch_receipt.json',
        proof=r.HERE/f'results/{phase}/role_proof.json',fixtures=r.HERE/f'results/{phase}/oracle_tests.json')
    records={k:r.load(p) for k,p in paths.items()}
    validate(records['gate'],records['receipt'],records['proof'],records['fixtures'],expected)
    if expected==120:
        summary=r.load(r.HERE/'results/diagnosis/diagnosis_summary.json')
        if summary['fit_count']!=120 or not summary['oracles_pass'] or not summary['premature_relative_stopping_confirmed']:
            raise RuntimeError('DIAGNOSIS_ROSTER_OR_ORACLE_FAILURE')
    return {k:r.sha(p) for k,p in paths.items()}


def verify_bindings(record,current):
    for key,digest in current.items():
        if record.get(key)!=digest:raise RuntimeError('AMENDMENT_EVIDENCE_CHANGED:'+key)
