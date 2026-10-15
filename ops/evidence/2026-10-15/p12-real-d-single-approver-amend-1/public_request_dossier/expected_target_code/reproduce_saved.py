"""Saved SYN evidence/statistics reproduction. No release, fits or neural sources."""
import argparse
from pathlib import Path
from .common import *
from . import study as r
from .frozen_math import load
from .scientific_evaluator import summarize_nulls,verdict,probe_report,rate_report

def verify_saved(output):
    output=Path(output);check_hashes(output,read_json(output/'evidence_inventory.json'))
    run=read_json(output/'result.json');gate=run['evaluator_gate'];mice=run['production_completion']
    if run['gate']!='PASS' or run['synthetic_only'] is not True or any(run[k] for k in ('REAL_D_AUTHORITY_PROVISIONED','REAL_D_SIGNATURE_ISSUED','D_RELEASE_CONSUMED','D_EVALUATION_EXECUTED','SCIENTIFIC_VALIDATION_PASS')):raise PermissionError('SYNTHETIC_ONLY_EVIDENCE')
    if gate['mice']!=13 or gate['null_cases']!=104 or gate['null_evaluations']!=103896 or gate['null_replicates_per_case']!=999 or gate['scored_cases']!=208 or gate['new_fits']!=0:raise PermissionError('FULL_REGISTERED_SYNTHETIC_DENOMINATOR')
    for role in ('target','controller'):
        receipt=read_json(output/('native_'+role+'_receipt.json'));proof=read_json(output/role/'role_proof.json')
        if receipt['exit_code']!=0 or receipt['profile_cleanup_hresult']!='0x00000000' or not proof['pass']:raise PermissionError('ACTUAL_NATIVE_ROLE_EVIDENCE')
    oracle=read_json(output/'controller/oracle_tests.json')
    if oracle['count']!=29 or not oracle['passed'] or oracle['skipped']!=0:raise PermissionError('UNCHANGED_NATIVE_CONTROLLER_ORACLES')
    for phase in ('pregrant','postgrant'):
        if not all(read_json(output/'target'/(phase+'_denials.json')).values()):raise PermissionError('ACTUAL_PROTECTED_ACCESS_DENIALS')
    from .run_synthetic import EXTRA
    if set(run['delivery_negative_tests'])!=set(EXTRA) or not all(v['fail_closed'] and not v['valid_release'] and v['retry_denied'] and v['start_signal_absent'] for v in run['delivery_negative_tests'].values()):raise PermissionError('FAILED_DELIVERY_DENIALS')
    states=read_json(r.SAVED/'C_state_manifest.json');math=load();rows=read_json(output/'target/scientific_scores.json')['rows'];saved=read_json(output/'target/final_statistics.json')
    stats=math['mouse_statistics'].aggregate(rows);stats['primary']['status']='SYNTHETIC_REGISTERED_CRITERIA';nulls=summarize_nulls(states,output/'target',math['mouse_statistics'].holm)
    if canonical(stats)!=canonical(saved['mouse_statistics']) or canonical(nulls)!=canonical(saved['null_statistics']) or canonical(verdict(stats,nulls,True))!=canonical(saved['verdicts']):raise PermissionError('SAVED_STATISTICAL_REPRODUCTION')
    if canonical(probe_report(rows,states))!=canonical(read_json(output/'target/probe_assessment.json')['rows']):raise PermissionError('PROBE_REPRODUCTION')
    if canonical(rate_report(read_json(r.SAVED/'provenance_roster.json')))!=canonical(read_json(output/'target/rate_assessment.json')):raise PermissionError('C_RATE_REPRODUCTION')
    return {'saved_integrity':'PASS','saved_statistics':'PASS','native_windows_roles':'PASS','mice':13,'contrasts':4,'null_cases':104,'replicates':999,'new_fits':0,'REAL_D_AUTHORITY_PROVISIONED':False,'D_RELEASE_CONSUMED':False,'D_EVALUATION_EXECUTED':False,'SCIENTIFIC_VALIDATION_PASS':False}

def main():
    p=argparse.ArgumentParser();p.add_argument('--result',default='');args=p.parse_args();r.verify()
    path=Path(args.result) if args.result else r.HERE/read_json(r.HERE/'latest_saved_result.json')['path']
    print(__import__('json').dumps(verify_saved(path),sort_keys=True))

if __name__=='__main__':main()
